
from flask import request, jsonify, Response
from flask_login import current_user, login_required


from flask_project.models import User, Group
from flask_restful import Resource
from functools import wraps

from flask_project.schems.user import user_full_schema
from flask_project.views.checker import admin_required


class UserResource(Resource):
    """
    Base resource class for User model
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None

    @login_required
    def dispatch_request(self, *args, **kwargs):
        """
        Checks if the user exists,
        and if so, then initializes it
        """
        username = kwargs.get("username")
        user = User.find_by_username(username)

        if user is None:
            return jsonify({
                "status": 404,
                "message": "User <{}> not found".format(username)
            })
        else:
            self.user = user
            return super(self).dispatch_request(*args, **kwargs)

    @staticmethod
    def admin_or_owner_required(foo):
        @wraps(foo)
        def wrapper(_, username):
            if not current_user.is_admin() and current_user != User.find_by_username(username):
                return Response("Admin or owner account required", status=403)
            return foo(_, username)

        return wrapper


class SignupApi(Resource):
    """
    Resource for retrieving exists and adding new users
    """
    @classmethod
    def get(self):
        if current_user.is_authenticated and current_user.group_id == 3:

            users = User.query.all()
            output = []
            for user in users:
                user_data = {}
                user_data['id'] = user.id
                user_data['username'] = user.username
                a = Group.query.get(user.group_id)
                user_data['group'] = a.group
                output.append(user_data)

            return jsonify({'users': output})
        return jsonify({'message': 'You dont admin'})

    @classmethod
    @admin_required
    def post(cls):
        user_json = request.get_json(force=True)
        username = user_json['username']
        password = user_json['password']

        if (username is None) or (password is None):
            return jsonify({
                "status": 400,
                "massage": "Username or password wasn`t provided"
            })
        elif User.exists(username):
            return {"status": 401, "reason": "User already exist"}
        else:
            user = User(username=username,
                        group_id=user_json.get('group_id')
                        )
            user.password = password
            if (user.group_id) < 1 and user.group_id > 2:
                return {"status": 401, "message": "Invalid group id"}
            user.save_to_db()
            return user_full_schema.dump(user), 200


class UserApi(Resource):
    """
    Resource for managing User details
    """
    @classmethod
    @login_required
    def get(self, user_id):
        """
        Method for retrieving details about the User
        """
        if current_user.is_authenticated and (current_user.group_id == 3 or current_user.id == user_id):
            user = User.query.filter_by(id=user_id).first()
            if not user:
                return jsonify({'message': 'No User'})
            user_data = {}
            user_data['username'] = user.username
            user_data['password'] = user.password
            a = Group.query.get(user.group_id)
            user_data['group'] = a.group
            return jsonify({'user': user_data})
        return jsonify({'message': 'You dint admin'})

    @classmethod
    @login_required
    def delete(cls, user_id):
        """
        Method for deleting the User
        """
        if current_user.is_authenticated and current_user.group_id == 3:
            user_data = User.query.get(user_id)
            if user_data:
                user_data.delete_from_db()
                return {"status": 200, 'message': "User Deleted successfully"}

            return {"status": 404, 'message': "User mnot founf"}

        return {"status": 401, "reason": "User is not admin"}

    @classmethod
    @login_required
    def put(cls, user_id):
        """
        Method for partial updating details about the User
        """
        if current_user.is_authenticated and (current_user.group_id == 3 or current_user.id == user_id):
            user_data = User.query.get(user_id)
            user_json = request.get_json(force=True)
            username = user_json['username']

            if not user_data:
                return {"status": 404, 'message': "User not found"}

            if User.exists(username=username) and current_user.username != username:
                return {"status": 401, "reason": "User already exist"}

            try:
                user_data.username = user_json['username']
                user_data.password = user_json['password']
                if current_user.group_id == 3:
                    user_data.group_id = user_json['group_id']
            except AssertionError:
                return {"status": 401, "message": "Invalid data"}
            if user_data.group_id < 1 and user_data.group_id > 2:
                return {"status": 401, "message": "Invalid group id"}
            user_data.save_to_db()
            return user_full_schema.dump(user_data), 200

        return {"status": 401, "reason": "User is not admin"}
