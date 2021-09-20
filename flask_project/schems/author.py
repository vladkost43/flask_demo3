from marshmallow import post_load
from marshmallow_sqlalchemy import ModelSchema

from flask_project.models import Authors


class AuthorSchema(ModelSchema):
    class Meta:
        ordered = True
        model = Authors
        fields = ("id", "url",)
        dump_only = ("id", "url",)

    @post_load
    def make_artifact(self, data, **kwargs):
        return Authors(**data)


author_schema = AuthorSchema()
author_list_schema = AuthorSchema(many=True)