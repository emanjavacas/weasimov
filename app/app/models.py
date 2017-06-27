import datetime
from app import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(64), unique=False)

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
    text = db.Column(db.String())
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)


class Edit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start, end = db.Column(db.Integer), db.Column(db.Integer)
    edit = db.String(db.String())
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)


class Generation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    model = db.Column(db.String(120))
    seed = db.Column(db.String())
    temp = db.Column(db.Float)
    text = db.Column(db.String())
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)
