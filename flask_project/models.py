from datetime import datetime


from sqlalchemy import exc, case
from sqlalchemy.ext.hybrid import hybrid_property

from flask_project import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


class EventArtifactModel(db.Model):

    __tablename__ = 'event_artifact'

    event_id = db.Column(db.Integer,
                         db.ForeignKey("events.id", ondelete="CASCADE"),
                         primary_key=True)
    artifact_id = db.Column(db.Integer,
                            db.ForeignKey("artifact.id", ondelete="CASCADE"),
                            primary_key=True)
    event = db.relationship("Events", back_populates="artifacts")
    artifact = db.relationship("Artifact", back_populates="events")

    @classmethod
    def find_all(cls):
        return cls.query.all()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()


class EventWithUsers(db.Model):
    __tablename__ = 'party'

    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, primary_key=True)

    @classmethod
    def find_all(cls):
        return cls.query.all()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()


class Events(UserMixin, db.Model):
    __tablename__ = 'events'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    event_name = db.Column(db.String())
    event_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(50), unique=False)
    user_id = db.relationship('User',
                              secondary="party",
                              cascade='all, delete')
    artifacts = db.relationship("EventArtifactModel", back_populates='event', cascade='all, delete')
    creator = db.Column(db.String(50), unique=False)

    def add_guest(self, user):
        if user in self.event_id:
            raise exc.IntegrityError("User can not be guest and participant", params=None, orig=None)
        self.event_id.append(user)
        self.save_to_db()

    def __repr__(self):
        return "<Event: {0}>".format(self.event_name)

    @classmethod
    def find_by_id(cls, user_id):
        return cls.query.filter_by(id=user_id).first()

    def update_in_db(self, data):
        Events.query.filter_by(id=self.id).update(data)
        db.session.commit()

    @classmethod
    def find_by_title(cls, event_name):
        return cls.query.filter_by(event_name=event_name).first()

    @classmethod
    def find_by_status(cls, status, queryset=None):
        queryset = queryset or cls.query
        return queryset.filter_by(status=status)

    @classmethod
    def filter_by_owner(cls, user_id):
        return cls.query.filter_by(owner_id=user_id)

    @hybrid_property
    def status(self):
        self.event_date = datetime.strptime(str(self.event_date), "%Y-%m-%d %H:%M:%S")
        if self.event_date > datetime.now():
            return "register open"
        if self.event_date <= datetime.now():
            return "register closed"

    @status.expression
    def status(self):
        return case([
            (self.event_date > datetime.now(), "register open"),
        ], else_="register closed")

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

    def update_in_db(self, data):
        Events.query.filter_by(id=self.id).update(data)
        db.session.commit()

    @classmethod
    def filter_by_guest(cls, user_id, queryset=None):
        queryset = queryset or cls.query
        return queryset.join(EventWithUsers). \
            filter(EventWithUsers.user_id == int(user_id))

    def add_guest(self, user):
        if user in self.user_id:
            raise exc.IntegrityError("User can not be guest and participant", params=None, orig=None)
        self.user_id.append(user)
        self.save_to_db()


class User(UserMixin, db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50))
    _password = db.Column(db.String(200))

    group = db.relationship("Group", back_populates="user")
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=False)

    event_id = db.relationship('Events',
                               secondary="party",
                               cascade='all, delete'
                               )

    __table_args__ = (
        db.CheckConstraint("LENGTH(username) >= 2", name='username_len_constraint'),
    )

    def __repr__(self):
        return "<User: {0}>".format(self.username)

    @hybrid_property
    def password(self):
        return self._password

    @password.setter
    def password(self, password):
        if password is None:
            self._password = None
        else:
            self._password = generate_password_hash(password)

    def check_password(self, password):
        if not self._password or not password:
            return False
        return check_password_hash(self._password, password)

    @classmethod
    def find_by_username(cls, username):
        return User.query.filter_by(username=username).first()

    @classmethod
    def exists(cls, username):
        return User.exists_local(username)

    @classmethod
    def exists_local(cls, username):
        return bool(User.query.filter_by(username=username).first())

    @classmethod
    def exists(cls, username):
        return User.exists_local(username)

    @classmethod
    def get_or_create(cls, username):
        user = User.find_by_username(username)
        if user is None:
            user = User(username=username)
            user.save_to_db()
        return user

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()


class Group(db.Model):

    __tablename__ = 'group'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    group = db.Column(db.String(50), unique=True)
    user = db.relationship('User', back_populates='group')

    def __init__(self, *args, **kwargs):
        super(Group, self).__init__(*args, **kwargs)

    def __repr__(self):
        return "<Group: {0}>".format(self.group)


class BaseModel:
    @classmethod
    def find_all(cls):
        return cls.query.all()

    @classmethod
    def find_by_id(cls, iid):
        return cls.query.filter_by(id=iid).first()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

    def as_dict(self):
        return {col.name: getattr(self, col.name) for col in self.__table__.columns}


class Artifact(db.Model, BaseModel):
    __tablename__ = 'artifact'

    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(128), nullable=False, unique=True)
    events = db.relationship("EventArtifactModel", back_populates='artifact', cascade='all, delete')

    def __str__(self):
        return self.url

    @classmethod
    def find_by_url(cls, url):
        return cls.query.filter_by(url=url).first()
