from datetime import datetime
import requests
from sqlalchemy import exc, case
from sqlalchemy.ext.hybrid import hybrid_property

from flask_project import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


class EventArtifactModel(db.Model):
    """
    Many-to-Many relationship model between Event and Artifact
    """

    __tablename__ = 'event_artifact'

    event_id = db.Column(db.Integer, db.ForeignKey('events.id', ondelete="CASCADE"), primary_key=True)
    artifact_id = db.Column(db.Integer, db.ForeignKey('artifact.id', ondelete="CASCADE"), primary_key=True)

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
    """
     Many-to-Many relationship model between Event and User
     """
    __tablename__ = 'party'

    event_id = db.Column(db.Integer, db.ForeignKey('events.id', ondelete="CASCADE"), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"), primary_key=True)

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
    """
    Events model
    """
    __tablename__ = 'events'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    event_name = db.Column(db.String())
    event_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(50), unique=False)
    user_id = db.relationship('User',
                              secondary="party",
                              cascade='all, delete')
    artifacts = db.relationship('Artifact',
                                secondary="event_artifact",
                                cascade='all, delete')
    creator = db.Column(db.String(50), unique=False)
    authors = db.relationship('Authors',
                              secondary="event_authors",
                              cascade='all, delete'
                              )

    @classmethod
    def filter_by_artifacts(cls, art_id, queryset=None):
        """
        Method for searching by event artifacts
        """
        queryset = queryset or cls.query
        return queryset.join(EventArtifactModel). \
            filter(EventArtifactModel.artifact_id == int(art_id))

    def add_guest(self, user):
        """
        Add given user to the guests list
        """
        if user in self.user_id:
            raise exc.IntegrityError("User can not be guest and participant", params=None, orig=None)
        self.user_id.append(user)
        self.save_to_db()

    def __repr__(self):
        return "<Event: {0}>".format(self.event_name)

    @classmethod
    def find_by_id(cls, user_id):
        """
        Method for searching by event id
        """
        return cls.query.filter_by(id=user_id).first()

    def update_in_db(self, data):
        Events.query.filter_by(id=self.id).update(data)
        db.session.commit()

    @classmethod
    def find_by_title(cls, event_name):
        """
        Method for searching by event name
        """
        return cls.query.filter_by(event_name=event_name).first()

    @classmethod
    def find_by_status(cls, status, queryset=None):
        """
        Method for searching by event status
        """
        queryset = queryset or cls.query
        return queryset.filter_by(status=status)

    @hybrid_property
    def status(self):
        """
        Method for post status< after checking event_date
        """
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

    @classmethod
    def filter_by_guest(cls, user_id, queryset=None):
        """
        Method for searching by event guests
        """
        queryset = queryset or cls.query
        return queryset.join(EventWithUsers). \
            filter(EventWithUsers.user_id == int(user_id))

    @classmethod
    def filter_by_participant(cls, user_id, queryset=None):
        """
        Method for searching by event authors
        """
        queryset = queryset or cls.query
        return queryset.join(EventAuthorsModel). \
            filter(EventAuthorsModel.authors_id == int(user_id))

    @classmethod
    def filter_by_creator(cls, user_id, queryset=None):
        """
        Method for searching by event creator
        """
        queryset = queryset or cls.query
        user = User.query.filter_by(id=user_id).first()
        return queryset.filter_by(creator=user.username)


class User(UserMixin, db.Model):
    """
    User model
    """
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
        """
        Method for hask password
        """
        if password is None:
            self._password = None
        else:
            self._password = generate_password_hash(password)

    def check_password(self, password):
        """
        Method for check password
        """
        if not self._password or not password:
            return False
        return check_password_hash(self._password, password)

    @classmethod
    def find_by_username(cls, username):
        """
        Method for searching by user username
        """
        return User.query.filter_by(username=username).first()

    @classmethod
    def exists(cls, username):
        return User.exists_local(username)

    @classmethod
    def exists_local(cls, username):
        """
        Method for checking, exist user  in Users be username
        """
        return bool(User.query.filter_by(username=username).first())

    @classmethod
    def get_or_create(cls, username):
        """
        Method for get or create user
        """
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

    @classmethod
    def exists_remote(cls, books_id):
        """
        Method for checking, eexists Book in other host
        """
        return bool(requests.get('{}/api/books/{}'.format('http://localhost:8000', books_id)))


class Group(db.Model):
    """
    Group model
    Many-to-one relationship model between User and Group
    """
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
    """
    Artifact model
    """
    __tablename__ = 'artifact'

    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(128), nullable=False, unique=True)
    db.relationship('Events',
                    secondary="event_artifact",
                    cascade='all, delete')

    def __str__(self):
        return self.url

    @classmethod
    def find_by_url(cls, url):
        return cls.query.filter_by(url=url).first()


class Authors(db.Model, BaseModel):
    """
    Authors model
    """
    __tablename__ = 'authors'

    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(128), nullable=False, unique=True)
    events = db.relationship('Events',
                             secondary="event_authors",
                             cascade='all, delete')

    def __str__(self):
        return self.url

    @classmethod
    def find_by_url(cls, url):
        return cls.query.filter_by(url=url).first()


class EventAuthorsModel(db.Model):
    """
    Many-to-Many relationship model between Event and Authors
    """

    __tablename__ = 'event_authors'

    event_id = db.Column(db.Integer, db.ForeignKey('events.id', ondelete="CASCADE"), primary_key=True)
    authors_id = db.Column(db.Integer, db.ForeignKey('authors.id', ondelete="CASCADE"), primary_key=True)

    @classmethod
    def find_all(cls):
        return cls.query.all()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
