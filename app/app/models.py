from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    firstname = db.Column(db.String(64), unique=False)
    surname = db.Column(db.String(64), unique=False)
    password = db.Column(db.String(64), unique=False)

class Text(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String())
    timestamp = db.Column(db.Date)

class Edit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    startpos = db.Column(db.Integer)
    endpos = db.Column(db.Integer)
    edit = db.String(db.String())
    timestamp = db.Column(db.Date)

class Generation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    seed = db.Column(db.String())
    text = db.Column(db.String())
    timestamp = db.Column(db.Date)
    
