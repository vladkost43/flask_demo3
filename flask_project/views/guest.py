
from flask import request, jsonify
from flask_login import login_required, current_user
from flask_restful import Resource

from flask_project.models import Events
from flask_project.models import User

from flask_project.schems.event import event_short_list_schema
from flask_project.schems.user import user_short_list_schema


class UserEventsAsGuest(Resource):
    @staticmethod
    @login_required
    def get():
        return event_short_list_schema.dump(Events.filter_by_guest(user_id=current_user.id))


class UserAsGuest(Resource):
    @login_required
    def get(self, event_id):
        a = Events.find_by_id(event_id)
        if current_user in a.user_id:
            return jsonify({
                "status": 200,
                "message": "You are registered as a Guest(User)"
            })
        elif current_user.group_id == 2:
            return jsonify({
                "status": 200,
                "message": "You are registered as a Creator"
            })
        elif current_user.group_id == 3:
            return jsonify({
                "status": 200,
                "message": "You are registered as a Creator"
            })
        else:
            return jsonify({
                "status": 200,
                "message": "You are nor registred as a Guest"})

    @login_required
    def post(self, event_id):
        if current_user.group_id != 1:
            return jsonify({
                "status": 404,
                "message": "You already registered as a Creator or Admin"
            })
        else:
            a = Events.find_by_id(event_id)
            if current_user in a.user_id:
                return jsonify({
                    "status": 404,
                    "message": "You can be a guest"
                })

            a.add_guest(current_user)
            a.save_to_db()
            return jsonify({
                "status": 200,
                "message": "Successfully register as a guest"
            })

    @login_required
    def delete(self, event_id):
        a = Events.find_by_id(event_id)
        if current_user not in a.user_id:
            return jsonify({
                "status": 404,
                "message": "You are not registered as a guest"
            })
        else:
            a.user_id.remove(current_user)
            a.save_to_db()

            return jsonify({
                "status": 200,
                "message": "Successfully unregister from guests"
            })


class EventGuests(Resource):
    def get(self, event_id):
        a = Events.find_by_id(event_id)
        return jsonify({
                "status": 200,
                "guests": user_short_list_schema.dump(a.user_id)
            })

    def post(self, event_id):

        body = request.get_json(force=True)
        if current_user.username != Events.find_by_id(event_id).creator or current_user.group_id == 1:
            return {'message': 'No permissions'}, 200

        if not body.get("guests"):
            return jsonify({
                "status": 404,
                "message": "Empty or unprovided guests list"
            })

        for username in body.get("guests"):
            guest = User.find_by_username(username)

            if guest is None:
                return jsonify({
                        "status": 404,
                        "message": "User <{}> not found".format(username)
                })
            a = Events.find_by_id(event_id)

            if guest in a.user_id:
                return jsonify({
                        "status": 400,
                        "message": "<{}> already registered for event as guest".format(guest.username)
                    })

            a.add_guest(guest)

        return jsonify({
            "status": 200,
            "message": "User were successfully registered for event guests"
        })

    def delete(self, event_id):
        if current_user.username != Events.find_by_id(event_id).creator or current_user.group_id == 1:
            return {'message': 'No permissions'}, 200
        body = request.get_json(force=True)

        if not body.get("guests"):
            return jsonify({
                "status": 404,
                "message": "Empty or unprovided guests list"
            })
        a = Events.find_by_id(event_id)

        for username in body.get('guests'):
            guest = User.find_by_username(username)
            if (guest is None) or (guest not in a.user_id):
                return jsonify({
                    "status": 404,
                    "message": "User <{}> not in guests list".format(username)
                })
            a.user_id.remove(guest)
            a.save_to_db()

        return jsonify({
            "status": 200,
            "message": "All users were successfully unregistered from event guests"
        })
