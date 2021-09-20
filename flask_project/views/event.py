from functools import wraps

from flask import Response
from flask import request, jsonify
from flask_login import login_required, current_user
from flask_restful import Resource

from flask_project import db
from flask_project.models import Events
from flask_project.schems.event import event_full_schema, event_short_list_schema


class EventResource(Resource):
    def __init__(self, *args, **kwargs):
        super(EventResource, self).__init__(*args, **kwargs)
        self.event = None

    def dispatch_request(self, *args, **kwargs):
        event = Events.find_by_id(kwargs.get("event_id"))
        if event is None:
            return jsonify({
                "status": 404,
                "message": "Event not found"
            })
        elif event.status == "registe closed" and request.method != "GET":
            return jsonify({
                "status": 404,
                "message": "You can not apply changes to past event"
            })
        else:
            self.event = event
            return super(EventResource, self).dispatch_request(*args, **kwargs)

    @staticmethod
    def owner_required(foo):
        @login_required
        @wraps(foo)
        def wrapper(_, event_id):
            a = Events.find_by_id(event_id)
            if current_user.username != a.creator:
                return Response("GOOD", status=403)
            return foo(_, event_id)

        return wrapper

    @staticmethod
    def admin_or_owner_required(foo):
        @login_required
        @wraps(foo)
        def wrapper(_, event_id):
            if (current_user.group_id != 2 or current_user.group_id != 3) \
                    and current_user.username != Events.find_by_id(event_id).creator:
                return Response("GOOD", status=403)
            return foo(_, event_id)

        return wrapper


class UserEventsAsOwner(Resource):
    @staticmethod
    @login_required
    def get():
        return event_short_list_schema.dump(Events.filter_by_owner(user_id=current_user.id))


class EventList(Resource):
    @staticmethod
    def get():
        events = Events.query.all()
        output = []
        for event in events:
            user_data = {}
            user_data['id'] = event.id
            user_data['event_name'] = event.event_name
            user_data['event_date'] = event.event_date
            user_data['status'] = event.status
            output.append(user_data)

        return jsonify({'events': output})

    @staticmethod
    @login_required
    def post():
        if current_user.group_id != 2:
            return {'message': 'You dont have permissions'}, 400
        event_json = request.get_json(force=True)

        if Events.find_by_title(event_json.get('event_name')):
            return {'message': 'Event already exists'}, 400
        user_json = request.get_json(force=True)
        event_name = user_json['event_name']
        event_date = user_json['event_date']
        creator = current_user.username
        event = Events(event_name=event_name, event_date=event_date, creator=creator)

        if event.status == "register closed":
            db.session.rollback()
            return {'message': 'You can not create past event'}, 400

        event.save_to_db()
        return event_full_schema.dump(event), 200


class RetrieveUpdateDestroyEvent(EventResource):
    def get(self, event_id):
        return event_full_schema.dump(self.event), 200

    @login_required
    def patch(self, event_id):
        if current_user.username != Events.find_by_id(event_id).creator or current_user.group_id != 3:
            return {'message': 'No permissions'}, 200
        event_json = request.get_json(force=True)
        a = Events.find_by_id(event_id)
        if Events.find_by_title(event_json.get('event_name')):
            return {'message': 'Event already exists'}, 400

        a.update_in_db(data=event_json)
        return event_full_schema.dump(self.event), 200

    @login_required
    def delete(self, event_id):
        if current_user.username != Events.find_by_id(event_id).creator or current_user.group_id != 3:
            return {'message': 'No permissions'}, 200
        a = Events.find_by_id(event_id)
        a.delete_from_db()
        return {'message': 'Event deleted'}, 200
