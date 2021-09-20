from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_restful import Api

app = Flask(__name__)

app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://vlad:123456@localhost/event'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
api = Api(app)
db = SQLAlchemy(app)

migrate = Migrate(app, db, compare_type=True)

from flask_project.views.login import Login, SignUp, Logout
from flask_project.views.user import SignupApi, UserApi
from flask_project.views.event import EventList, RetrieveUpdateDestroyEvent
from flask_project.views.guest import UserEventsAsGuest, UserAsGuest, EventGuests
from flask_project.views.authors import EventArtifacts

api.add_resource(SignupApi, '/user')
api.add_resource(UserApi, '/user/<int:user_id>')
api.add_resource(Login, "/login")
api.add_resource(SignUp, "/signup")
api.add_resource(Logout, "/logout")
api.add_resource(EventList, "/event")
api.add_resource(RetrieveUpdateDestroyEvent, "/event/<int:event_id>")
api.add_resource(UserEventsAsGuest, "/where_i_guest")
api.add_resource(UserAsGuest, "/event/<int:event_id>/me_guest")
api.add_resource(EventGuests, "/event/<int:event_id>/guests")
api.add_resource(EventArtifacts, "/event/<int:event_id>/artifacts")
