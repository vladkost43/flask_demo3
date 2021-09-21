import os
import re

import jwt
from flask import request, jsonify, Response
from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    current_user
)
from flask_restful import Resource

from flask_project import app, db
from flask_project.models import User
from flask_project.schems.user import user_full_schema

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.unauthorized_handler
def unauthorized_callback():
    return Response("Authorization required", status=403)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def decode_token(token):
    return jwt.decode(token, os.getenv('SECRET_KEY'), algorithms='HS256')


def encode_token(username, password):
    return jwt.encode({"name": username, "password": password}, os.getenv('SECRET_KEY'), algorithm='HS256')


class Login(Resource):
    @classmethod
    def post(cls):
        if current_user.is_authenticated:
            return jsonify({
                "status": 403,
                "massage": "Already logged in as {0}".format(current_user.id)
            })

        user_data = request.get_json(force=True)
        username = user_data["username"]
        password = user_data["password"]

        if username is None or password is None:
            return jsonify({
                "status": 400,
                "massage": "Username or password wasn`t provided"
            })

        user = User.find_by_username(username)

        if not user.check_password(password):
            return jsonify({
                    "status": 400,
                    "massage": "Incorrect passdword"
            })

        login_user(user)
        db.session.commit()
        return jsonify({
                "status": 200,
                "message": "Successfully logged in as <{}>".format(username),
                "profile": user_full_schema.dump(user)
            })


class Register(Resource):
    @classmethod
    def post(cls):
        user_json = request.get_json(force=True)
        username = user_json['username']
        password = user_json['password']
        group_id = user_json['group_id']
        if username is None or password is None or group_id is None:
            return jsonify({
                "status": 400,
                "massage": "Username or password or group id wasn`t provided"
            })

        elif User.exists_local(username):
            return {"status": 401, "message": "User already exists"}
        elif not re.Match('^[a-z0-9_-]{4,20}$', username):
            return jsonify({
                "status": 400,
                "massage": "Incorrect username"
            })

        else:
            user = User(username=username,
                        group_id=group_id,
                        password=password)
            if user.group_id < 1 and user.group_id > 2:
                return {"status": 401, "message": "Invalid group id"}
            user.save_to_db()
            return user_full_schema.dump(user), 200


class Logout(Resource):
    @classmethod
    @login_required
    def post(cls):
        logout_user()
        return jsonify({
            "result": 200,
            "message": "Logout success"
        })
