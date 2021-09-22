from marshmallow import post_load
from marshmallow_sqlalchemy import ModelSchema

from flask_project.models import Authors
"""
AuthorSchema
"""


class AuthorSchema(ModelSchema):
    class Meta:
        """
        Connecting Schema with the Author Model
         """
        ordered = True
        model = Authors
        fields = ("id", "url",)
        dump_only = ("id", "url",)

    @post_load
    def make_artifact(self, data, **kwargs):
        """
        Returning Author Model
        """
        return Authors(**data)


author_schema = AuthorSchema()
author_list_schema = AuthorSchema(many=True)
