import datetime
import json
from app import db


class JSONEncodedDict(db.TypeDecorator):
    "Represents an immutable structure as a json-encoded string."

    impl = db.VARCHAR

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = json.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = json.loads(value)
        return value


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(64), unique=False)
    session = db.Column(JSONEncodedDict)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

    def __repr__(self):
        return '<User(%r)>' % self.username


class Text(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(JSONEncodedDict)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)


class Edit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    edit = db.Column(JSONEncodedDict)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)


class Generation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    model = db.Column(db.String(120))
    seed = db.Column(db.String())
    temp = db.Column(db.Float)
    selected = db.Column(db.Boolean, default=False)
    text = db.Column(db.String())
    generation_id = db.Column(db.String(64))
    draft_entity_id = db.Column(db.String(64), default='')
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    selected_timestamp = db.Column(db.DateTime)
