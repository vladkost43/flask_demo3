from marshmallow import post_load
from marshmallow_sqlalchemy import ModelSchema

from flask_project.models import Artifact

"""
Artifact Schema
"""


class ArtifactSchema(ModelSchema):
    class Meta:
        """
        Connecting Schema with the Artifact Model
        """
        ordered = True
        model = Artifact
        fields = ("id", "url",)
        dump_only = ("id", "url",)

    @post_load
    def make_artifact(self, data, **kwargs):
        """
        Returning Artifact Model
        """
        return Artifact(**data)


artifact_schema = ArtifactSchema()
artifact_list_schema = ArtifactSchema(many=True)
