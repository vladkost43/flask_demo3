import os
from typing import Dict, Tuple

import requests
from flask import request, Response, jsonify
from flask_login import login_required, current_user
from flask_restful import Resource
import json

from flask_project.models import Events, Artifact, Authors
from flask_project.models import User
from flask_project.views.event import EventResource
from flask_project.schems.event import event_short_list_schema


class EventArtifacts(EventResource):

    def get(self, event_id):
        a = Events.find_by_id(event_id)
        return jsonify({
            "status": 200,
            "artifacts": event_short_list_schema.dump(a.artifacts)
        })

    def post(self, event_id):
        body = request.get_json(force=True)
        a = Events.find_by_id(event_id)

        if not body.get('books'):
            return jsonify({
                "status": 404,
                "message": "Empty or unprovided authors list"
            })

        for username_id in body.get('books'):
            if User.exists_remote(username_id):
                    response = "{}/api/books/{}".format('http://localhost:8000', username_id)
                    book = Artifact.find_by_url(url=response)
                    if book is None:
                        book = Artifact(url=response)
                        book.save_to_db()
                    a.artifacts.append(book)
            else:
                return jsonify({
                    "status": 404,
                    "message": "Empty or unprovided authors list"
                })



        a.save_to_db()
        return jsonify({
            "status": 200,
            "message": "Author -"
        })

    @EventResource.admin_or_owner_required
    def delete(self, event_id: int) -> Response:
        """Method for deleting participant
        Parameters
        ----------
        event_id : int
            Event id
        Returns
        -------
        Response
            Response message with status code
        """
        body = request.get_json(force=True)

        if not body.get('participants'):
            return jsonify({
                "status": 404,
                "message": "Empty or unprovided participants list"
            })

        for username in body.get('participants'):
            participant = User.find_by_username(username)

            if (participant is None) or (participant not in self.event.participants):
                return jsonify({
                    "status": 404,
                    "message": "User <{}> not in participants list".format(username)
                })

            self.event.participants.remove(participant)
            self.event.save_to_db()

        return jsonify({
            "status": 200,
            "message": "All users were successfully unregistered from event participants"
        })