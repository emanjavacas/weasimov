
import datetime
import json

from app import db
from sqlalchemy.dialects.mysql import MEDIUMTEXT


class JSONEncodedDict(db.TypeDecorator):
    "Represents an immutable structure as a json-encoded string."

    impl = MEDIUMTEXT

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = json.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = json.loads(value)
        return value


class User(db.Model):
    """
    id: int, user id
    username: str, username
    password: str, password
    session: json, {'max_seq_len': int, 'temperature': float}
    timestamp: DateTime, time when user joined
    """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(64), unique=False)
    session = db.Column(JSONEncodedDict)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    active = db.Column(db.SmallInteger, default=False)

    def is_authenticated(self):
        return True

    def is_active(self):
        return self.active

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

    def __repr__(self):
        return '<User(%r)>' % self.username


class Doc(db.Model):
    """
    id: str, doc id
    user_id: User.id, user id of the creator of the document
    timestamp: DateTime, creation timestamp
    last_modified: DateTime, timestamp of last edit
    active: bool, False if doc has been deleted
    screen_name: str, name to be displayed for this document
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    screen_name = db.Column(db.String(120), default='Untitled Document')
    active = db.Column(db.SmallInteger, default=True)
    last_modified = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def as_json(self):
        def serialize_col(col):
            data = getattr(self, col.name)
            if col.name in ['last_modified', 'timestamp']:
                return int(data.timestamp() * 1000)
            else:
                return data
        return {col.name: serialize_col(col) for col in self.__table__.columns}


class Text(db.Model):
    """
    Class representing document content. Currently Text entries are not
    modified in place but added so that we can reconstruct document stages.

    id: str, text entry id
    user_id: User.id, id of the doc owner
    doc_id: Doc.id, id of the doc to which the snapshot belongs
    text: json, dump of ConvertToRaw(ContentState), see DraftJS
    timestamp: DateTime, timestamp of the snapshot
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    doc_id = db.Column(db.Integer)
    text = db.Column(JSONEncodedDict)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)


class Edit(db.Model):
    """
    Class representing an edit on a given document. Edits are meant to
    represent diffs and are therefore tightly coupled to the structure of
    DraftJs ContentState. Currently Edits adhere to the JSON patch RCE
    standard.

    id: int, edit id
    user_id: User.id, id of the owner of the document (who is always author
        of the edit)
    doc_id: Doc.id, id of the document
    edit: json (array), json patch between consecutive DraftJS ContentState's
    timestamp: DateTime, timestamp of the edit
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    doc_id = db.Column(db.Integer)
    edit = db.Column(JSONEncodedDict)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)


class Generation(db.Model):
    """
    Class representing generations output by the model.

    id: int, primary_key for the Generation table
    generation_id: str, uuid of the generation batch
    user_id: User.id, id of the user who triggered the generation
    seed_doc_id: Doc.id, id of the doc that provided the seed
    model: str, id of the model that was used for generation
    seed: str, input for the generation
    temperature: float, temperature used for generation
    max_seq_len: int, max_seq_len used for generation
    text: str, output of the generation
    timestamp: DateTime, timestamp of the generation
    action_doc_id: str, id of document in which the action (selection or
        dismiss) was triggered
    draft_entity_id: str, id of the DraftJS entity that was created upon
        insertion. This can be used in combination with insert_doc_id to
        find out the context in which the generation was inserted.
    selected: bool, whether the generation has been inserted into the text
    selected_timestamp: DateTime, timestamp of the insertion
    dismissed: bool, whether the generation has been dismissed
    dismissed_timestamp: DateTime, timestamp of the dismission
    """
    id = db.Column(db.Integer, primary_key=True)
    generation_id = db.Column(db.String(64))
    user_id = db.Column(db.Integer)
    seed_doc_id = db.Column(db.Integer)
    model = db.Column(db.String(120))
    seed = db.Column(db.String(500))
    temperature = db.Column(db.Float)
    max_seq_len = db.Column(db.Integer)
    text = db.Column(db.String(500))
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    action_doc_id = db.Column(db.Integer)
    draft_entity_id = db.Column(db.String(64), default='')
    selected = db.Column(db.SmallInteger, default=False)
    selected_timestamp = db.Column(db.DateTime)
    dismissed = db.Column(db.SmallInteger, default=False)
    dismissed_timestamp = db.Column(db.DateTime)
