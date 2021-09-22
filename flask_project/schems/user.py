from marshmallow_sqlalchemy import ModelSchema
from flask_project.models import User
from marshmallow import post_load

"""
User Schema
"""


class UserSchema(ModelSchema):
    class Meta:
        """
        Connecting Schema to the User Model
        """
        model = User
        ordered = True
        include_fk = True

        fields = ("id", "username", "group_id")

    @post_load
    def make_event(self, data, **kwargs):
        """
        Returning User Model
        """
        return User(**data)


user_full_schema = UserSchema()
user_full_list_schema = UserSchema(many=True)

user_short_schema = UserSchema(only=("username", "group_id"))
user_short_list_schema = UserSchema(only=("username", "group_id"), many=True)
