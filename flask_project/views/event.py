import re
from datetime import datetime
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
        """
        Base resource class for Event model
        """
        super(EventResource, self).__init__(*args, **kwargs)
        self.event = None

    def dispatch_request(self, *args, **kwargs):
        """
        Checks if the event exists and has not passed,
        and if so, then initializes it
        """
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


class UserEventsAsCreator(Resource):
    @staticmethod
    @login_required
    def get():
        """
        Resource for providing a list of events
        where the current user is the creator
        """
        if current_user.group_id != 2:
            return {'message': 'You are not a creator'}, 400
        return event_short_list_schema.dump(Events.filter_by_creator(user_id=current_user.id))


class RegisterOpen(Resource):
    @staticmethod
    @login_required
    def get():
        """
        Resource for providing a list of events
        where register open in event
        """
        return event_short_list_schema.dump(Events.query.filter_by(status="register open"))


class RegisterClosed(Resource):
    @staticmethod
    @login_required
    def get():
        """
        Resource for providing a list of events
        where register closed in event
        """
        return event_short_list_schema.dump(Events.query.filter_by(status="register closed"))


class EventList(Resource):
    @staticmethod
    def get():
        """
        Resource for retrieving old and adding new events
        """
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
        """
        Method for creating new Event
        """
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
        if not re.match('^[a-z0-9_-]{4,40}$', event_name):
            return jsonify({
                "status": 400,
                "massage": "Incorrect event_name"
            })

        event.save_to_db()
        return event_full_schema.dump(event), 200


class ChangeInformationEvent(EventResource):
    def get(self, event_id):
        """
        Method for retrieving details about the Event
        """
        return event_full_schema.dump(self.event), 200

    @login_required
    def patch(self, event_id):
        """
        Method for partial updating details about the Event
        """
        if current_user.group_id == 2 and current_user.username != Events.find_by_id(event_id).creator:
            return {'message': 'No permissions'}, 400
        elif current_user.group_id == 1:
            return {'message': 'No permissions'}, 400
        event_json = request.get_json(force=True)
        a = Events.find_by_id(event_id)
        if Events.find_by_title(event_json.get('event_name')):
            return {'message': 'Event already exists'}, 400
        if event_json.get('status') or event_json.get('creator'):
            return {'message': 'You cant change creator or status'}, 400
        a.update_in_db(data=event_json)
        return event_full_schema.dump(self.event), 200

    @login_required
    def delete(self, event_id):
        """
        Method for deleting the Event
        """
        if current_user.group_id == 2 and current_user.username != Events.find_by_id(event_id).creator or \
                (current_user.group_id == 3 and current_user.username == Events.find_by_id(event_id).creator):
            return {'message': 'No permissions'}, 400
        elif current_user.group_id == 1:
            return {'message': 'No permissions'}, 400
        a = Events.find_by_id(event_id)
        for author in a.authors:
            a.authors.remove(author)
        a.delete_from_db()
        return {'message': 'Event deleted'}, 200
