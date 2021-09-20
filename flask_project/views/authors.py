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
                "message": "Empty or unprovided books list"
            })

        for username_id in body.get('books'):
            if User.exists_remote(username_id):
                response = "{}/api/books/{}/".format("http://localhost:8000", username_id)
                book = Artifact.find_by_url(url=response)
                if book is None:
                    book = Artifact(url=response)
                    book.save_to_db()
                a.artifacts.append(book)
                response = requests.get("{}/api/books/{}/".
                                        format("http://localhost:8000", username_id))
                json_data = json.loads(response.text)
                if json_data["authors"]:
                    for authors in json_data["authors"]:
                        auth = authors[0]
                        url = "{}/api/authors/{}/".format("http://localhost:8000", auth)
                        author = Authors.find_by_url(url)

                        # If it is new artifact
                        if author is None:
                            author = Authors(url=url)
                            author.save_to_db()
                        a.authors.append(author)
        a.save_to_db()
        return jsonify({
            "status": 200,
            "message": "All books are rigistreted"
        })

    def delete(self, event_id):
        body = request.get_json(force=True)
        a = Events.find_by_id(event_id)

        if not body.get('books'):
            return jsonify({
                "status": 404,
                "message": "Empty or unprovided books list"
            })

        for book in body.get('books'):
            url = "{}/api/books/{}/".format("http://localhost:8000", book)
            artifact = Artifact.find_by_url(url)

            if artifact is None:
                return jsonify({
                    "status": 404,
                    "message": "Book not in participants list"
                })
            a.artifacts.remove(artifact)
            response = requests.get("{}/api/books/{}/".format("http://localhost:8000", book))
            json_data = json.loads(response.text)
            if json_data["authors"]:
                for authors in json_data["authors"]:
                    auth = authors[0]
                    url = "{}/api/authors/{}/".format("http://localhost:8000", auth)
                    author = Authors.find_by_url(url)

                    if author is None:
                        continue
                    else:
                        if author in a.authors:
                            a.authors.remove(author)
            a.save_to_db()

        return jsonify({
            "status": 200,
            "message": "All books were successfully unregistered from event participants"
        })