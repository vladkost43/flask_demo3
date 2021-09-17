from flask import Flask, request, jsonify, make_response, url_for
from flask_restful import abort

from flask_project import app, db
from flask_project.models import User

@app.route('/')
def hello():
    return "Hello World! {0}"


if __name__ == '__main__':
    app.run(debug=True)
