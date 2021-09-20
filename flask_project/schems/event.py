from marshmallow import fields, post_load
from marshmallow_sqlalchemy import ModelSchema

from flask_project.models import Events
from flask_project.schems.artifact import artifact_list_schema
from flask_project.schems.author import author_list_schema
from flask_project.schems.user import user_short_list_schema


class EventSchema(ModelSchema):
    event_name = fields.String(
        required=True,
        error_messages={
            'required': 'Sorry, Title field is required',
            'null': 'Sorry, Title field cannot be null',
            'invalid': 'Sorry, Title field must be a string'})

    event_date = fields.DateTime(
        required=True,
        error_messages={
            'required': 'Sorry, Start datetime field is required',
            'null': 'Sorry, Start datetime field cannot be null',
            'invalid': 'Sorry, Start datetime field must be in format YYYY-MM-DD HH:MM'})
    status = fields.String()

    event_id = fields.Nested(user_short_list_schema, many=True)
    artifacts = fields.Nested(artifact_list_schema, many=True)
    authors = fields.Nested(author_list_schema, many=True)
    creator = fields.String()

    class Meta:
        ordered = True
        include_fk = True
        model = Events
        fields = ("id", "event_name", "event_date", "status", "user_id", "artifacts", "authors", 'creator')
        dump_only = ("id", "event_name", "event_date", 'artifacts', "authors", "status")

    @post_load
    def make_event(self, data, **kwargs):
        return Events(**data)


event_full_schema = EventSchema()
event_full_list_schema = EventSchema(many=True)

event_short_schema = EventSchema(exclude=('artifacts', 'authors', 'creator'))
event_short_list_schema = EventSchema(exclude=('artifacts', 'authors', 'creator'), many=True)
