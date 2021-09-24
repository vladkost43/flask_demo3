from flask_project import api
from flask_project.views.login import Login,\
    Register,\
    Logout
from flask_project.views.user import SignupApi,\
    UserApi
from flask_project.views.event import EventList,\
    ChangeInformationEvent,\
    UserEventsAsCreator,\
    RegisterOpen,\
    RegisterClosed
from flask_project.views.guest import UserEventsAsGuest,\
    UserAsGuest,\
    EventGuests
from flask_project.views.authors import EventArtifacts

api.add_resource(SignupApi, '/user')
api.add_resource(UserApi, '/user/<int:user_id>')
api.add_resource(Login, "/login")
api.add_resource(Register, "/register")
api.add_resource(Logout, "/logout")

api.add_resource(EventList, "/event")
api.add_resource(RegisterOpen, "/event/open")
api.add_resource(RegisterClosed, "/event/close")

api.add_resource(ChangeInformationEvent, "/event/<int:event_id>")
api.add_resource(UserEventsAsGuest, "/event/me_guest")
api.add_resource(UserEventsAsCreator, "/event/creator")

api.add_resource(UserAsGuest, "/event/<int:event_id>/me_guest_event")
api.add_resource(EventGuests, "/event/<int:event_id>/guests")

api.add_resource(EventArtifacts, "/event/<int:event_id>/artifacts")


