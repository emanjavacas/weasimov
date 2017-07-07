
from functools import wraps
from datetime import datetime
import uuid
import itertools

from palettable.colorbrewer.qualitative import Pastel2_8
import flask
import flask_login
from flask_socketio import emit, join_room, leave_room
from sqlalchemy import desc, and_

from app import app, db, lm
from . import socketio
from .models import User, Doc, Text, Edit, Generation
from .forms import LoginForm, RegisterForm


def get_colors():
    def format_color(r, g, b):
        return {'r': r,
                'g': g,
                'b': b,
                'a': 1}
    return (format_color(*c) for c in Pastel2_8.colors)


def format_models():
    models = []
    model_names = app.config.get("MODEL_NAMES", {})
    ignore_unnamed = app.config.get('IGNORE_UNNAMED', False)
    colors = itertools.cycle(get_colors())
    for model in app.synthesizer.list_models():
        if ignore_unnamed and model['path'] not in model_names:
            continue
        model['color'] = next(colors)
        model['modelName'] = model_names.get(model['path'])
        models.append(model)
    return models


@lm.user_loader
def load_user(id):
    return User.query.get(int(id))


@app.before_request
def before_request():
    flask.g.user = flask_login.current_user


@app.route('/login', methods=['GET', 'POST'])
def login():
    if flask.g.user is not None and flask.g.user.is_authenticated:
        return flask.redirect(flask.url_for('index'))
    form = LoginForm()
    if flask.request.method == 'GET':
        return flask.render_template('login.html', title='Sign in', form=form)
    if form.validate_on_submit() and form.validate_fields():
        flask.session['remember_me'] = form.remember_me.data
        flask_login.login_user(form.get_user(), remember=form.remember_me.data)
        # set active
        user = form.get_user()
        user.active = True
        db.session.commit()
        # websocket
        socketio.emit('login', {'user_id': user.id}, namespace='/monitor')
        return flask.redirect(flask.url_for("index"))
    return flask.render_template("login.html", title='Sign in', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if flask.request.method == 'GET':
        return flask.render_template(
            'register.html', title='Sign In', form=form)
    if form.validate_on_submit() and form.validate_fields():
        user = User(username=form.username.data,
                    password=form.password.data)
        db.session.add(user)
        db.session.flush()
        doc = Doc(user_id=user.id)
        db.session.add(doc)
        db.session.commit()
        return flask.redirect(flask.url_for('login'))
    return flask.render_template('register.html', title='Sign Up', form=form)


@app.route('/logout', methods=['POST', 'GET'])
@flask_login.login_required
def logout():
    user_id = int(flask_login.current_user.id)
    flask_login.logout_user()
    user = User.query.get(user_id)
    user.active = False
    db.session.commit()
    # websocket
    socketio.emit('logout', {'user_id': user_id}, namespace='/monitor')
    return flask.redirect(flask.url_for('login'))


@app.route('/')
@app.route('/index', methods=['GET', 'POST'])
@flask_login.login_required
def index():
    return flask.render_template('index.html')


def get_session_value(key, session={}):
    return session.get(key) or app.config["DEFAULTS"][key]


def get_last_text(user_id, doc_id):
    expr = and_(Text.user_id == user_id, Text.doc_id == doc_id)
    return Text.query.filter(expr) \
                     .order_by(desc(Text.timestamp)) \
                     .first()


def get_user_docs(user_id, doc_id=None):
    """
    Fetch user docs metadata from the db. If doc_id is given, it will
    fetch only that doc metadata.
    """
    expr = and_(Doc.user_id == user_id, Doc.active == True)  # nopep8
    if doc_id is not None:
        expr = and_(Doc.user_id == user_id,
                    Doc.active == True,  # nopep8
                    Doc.id == doc_id)
    return Doc.query.filter(expr)


@app.route('/init', methods=['GET'])
@flask_login.login_required
def init():
    user_id = int(flask_login.current_user.id)
    user = User.query.get(user_id)
    docs = get_user_docs(user_id).all()
    doc_id = docs[0].id
    text = get_last_text(user_id, doc_id)
    payload = {
        # app state data
        "username": user.username,
        "models": format_models(),
        # user session data
        "temperature": get_session_value("temperature", user.session or {}),
        "maxSeqLen": get_session_value("max_seq_len", user.session or {}),
        # docs
        "docs": [doc.as_json() for doc in docs],
        "docId": doc_id,
        # last editor state
        "contentState": text.text if text is not None else None}
    return flask.jsonify(status="OK", session=payload)


@app.route('/savechange', methods=['POST'])
@flask_login.login_required
def savechange():
    """
    doc_id: int,
    edit: json,
    timestamp: int
    """
    # TODO: check if user is allowed to modify based on doc_id?
    # TODO: check if doc is active
    data = flask.request.json
    timestamp = datetime.fromtimestamp(data['timestamp'])
    user_id = int(flask_login.current_user.id)
    edit = Edit(user_id=user_id,
                doc_id=data['doc_id'],
                edit=data['edit'],
                timestamp=timestamp)
    doc = Doc.query.get(data['doc_id'])
    doc.last_modified = timestamp
    db.session.add(edit)
    db.session.commit()
    # websocket
    emit('savechange', data, room=user_id, namespace='/monitor')
    return flask.jsonify(status='OK')


@app.route('/savesuggestion', methods=['POST'])
@flask_login.login_required
def savesuggestion():
    """
    generation_id: str,
    doc_id: int, id of doc where the action took place
    selected: True, (optional), requires `draft_entity_id`
    draft_entity_id: str
    dismissed: True, (optional)
    timestamp: int
    """
    data = flask.request.json
    generation_id = data['generation_id']
    timestamp = datetime.fromtimestamp(data['timestamp'])
    generation = Generation.query.filter_by(generation_id=generation_id)
    generation.action_doc_id = data['doc_id']
    if data.get('selected'):
        # TODO: check if user is allowed to modify based on doc_id?
        # TODO: check if doc is active
        generation.selected = True
        generation.selected_timestamp = timestamp
        generation.draft_entity_id = data['draft_entity_id']
    if data.get('dismissed'):
        generation.dismissed = True
        generation.dismissed_timestamp = timestamp
    db.session.commit()
    # websocket
    user_id = int(flask_login.current_user.id)
    emit('savesuggestion', data, room=user_id, namespace='/monitor')
    return flask.jsonify(status='OK', message='Suggestion updated.')


@app.route('/createdoc', methods=['POST'])
@flask_login.login_required
def createdoc():
    """
    doc_id: int
    screen_name: str
    timestamp: int
    """
    data = flask.request.json
    user_id = int(flask_login.current_user.id)
    timestamp = datetime.fromtimestamp(data['timestamp'])
    doc = Doc(user_id=user_id,
              screen_name=data['screen_name'],
              timestamp=timestamp,
              last_modified=timestamp)
    db.session.add(doc)
    db.session.commit()
    data = doc.as_json()
    data['snippet'] = ''
    emit('createdoc', data, room=user_id, namespace='/monitor')
    return flask.jsonify(status='OK', doc=doc.as_json())


@app.route('/fetchdoc', methods=['GET'])
@flask_login.login_required
def fetchdoc():
    """
    doc_id: int
    user_id: int, optional
    """
    requested_user = flask.request.args.get('user_id')
    if requested_user is not None:
        # TODO check if whitelisted
        pass
    user_id = requested_user or int(flask_login.current_user.id)
    doc_id = flask.request.args.get('doc_id')
    doc = get_user_docs(user_id, doc_id=doc_id).first()
    text = get_last_text(user_id, doc.id)
    text = text.text if text is not None else None
    return flask.jsonify(status='OK', doc=doc.as_json(), contentState=text)


@app.route('/savedoc', methods=['POST'])
@flask_login.login_required
def savedoc():
    """
    doc_id: int
    text: json
    timestamp: int
    """
    user_id = int(flask_login.current_user.id)
    data = flask.request.json
    # TODO: check if user is allowed to modify based on doc_id?
    # TODO: check if doc is active
    timestamp = datetime.fromtimestamp(data['timestamp'])
    text = Text(user_id=user_id,
                doc_id=data['doc_id'],
                text=data['text'],
                timestamp=timestamp)
    db.session.add(text)
    db.session.commit()
    return flask.jsonify(status='OK', message='Document saved.')


@app.route('/removedoc', methods=['POST'])
@flask_login.login_required
def removedoc():
    """
    doc_id: int
    """
    user_id = int(flask_login.current_user.id)
    doc_id = flask.request.args.get('doc_id')
    doc = get_user_docs(user_id, doc_id=doc_id).first()
    doc.active = False
    db.session.commit()
    # websocket
    emit('removedoc', {'doc_id': doc_id}, room=user_id, namespace='/monitor')
    return flask.jsonify(status='OK', message='Document deleted.')


@app.route('/editdocname', methods=['POST'])
@flask_login.login_required
def editdocname():
    """
    doc_id: int
    screen_name: str
    timestamp: int
    """
    data = flask.request.json
    doc = Doc.query.get(data['doc_id'])
    doc.last_modified = datetime.fromtimestamp(data['timestamp'])
    doc.screen_name = data['screen_name']
    db.session.commit()
    # websocket
    user_id = int(flask_login.current_user.id)
    emit('editdocname', data, room=user_id, namespace='/monitor')
    return flask.jsonify(status='OK', message='Name changed.')


@app.route('/savesession', methods=['POST'])
@flask_login.login_required
def savesession():
    """
    session: json {'max_seq_len': int, 'temperature': float}
    """
    user = User.query.get(int(flask_login.current_user.id))
    user.session = flask.request.json['session']
    db.session.commit()
    return flask.jsonify(status="OK", message='Session saved.')


@app.route('/generate', methods=['POST'])
@flask_login.login_required
def generate():
    """
    seed: str
    seed_doc_id: int, doc id where the generation was triggered
    model: str, path of the model used for generation
    temperature: float
    max_seq_len: int
    """
    user_id = int(flask_login.current_user.id)
    model = flask.request.json['model']
    app.synthesizer.load(model_names=(model,))  # maybe load model
    seed = flask.request.json["seed"]
    seed_doc_id = flask.request.json['seed_doc_id']
    temperature = float(flask.request.json['temperature'])
    max_seq_len = int(flask.request.json['max_seq_len'])
    try:
        timestamp = datetime.utcnow()
        hyps = app.synthesizer.sample(
            model_name=model,
            seed_texts=None if not seed else [seed],
            temperature=temperature,
            batch_size=app.config.get('DEFAULTS', {}).get('batch_size', 3),
            ignore_eos=app.config.get('DEFAULTS', {}).get('ignore_eos', False),
            max_seq_len=max_seq_len,
            max_tries=1)
        for hyp in hyps:
            generation_id = str(uuid.uuid4())
            db.session.add(
                Generation(
                    generation_id=generation_id,
                    user_id=user_id,
                    seed_doc_id=seed_doc_id,
                    model=model,
                    seed=seed or '',
                    temperature=temperature,
                    max_seq_len=max_seq_len,
                    text=hyp['text'],
                    timestamp=timestamp))
            hyp["generation_id"] = generation_id
            hyp["timestamp"] = timestamp
            hyp["model"] = model
        db.session.commit()
        return flask.jsonify(status='OK', hyps=hyps, seed=seed, model=model)
    except Exception as e:
        if app.debug is True:
            raise e
        return flask.jsonify(status='Error', message=str(e)), 500


# WebSockets
def whitelist(whitelisted):
    def wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            user = User.query.get(int(flask_login.current_user.id))
            if user.username not in whitelisted:
                return flask.jsonify(status='ERROR', message='Forbidden'), 403
            return f(*args, **kwargs)
        return wrapped
    return wrapper


@app.route('/monitor', methods=['GET'])
@flask_login.login_required
@whitelist(app.config.get('MONITORS', []))
def monitor():
    return flask.render_template('monitor.html', title='Monitor')


def fetch_snippet(doc_id, max_length=50):
    """
    Get a snippet of length `max_length` from the beginning of the last version
    of a given document.
    """
    snippet = ''
    text = Text.query.filter_by(doc_id=doc_id) \
               .order_by(desc(Text.timestamp)) \
               .first()
    for block in text.text['blocks']:
        if len(snippet) >= max_length:
            return snippet
        block_text = block['text']
        snippet += block_text[:min(max_length - len(snippet), len(block_text))]
    return snippet


def fetch_docs(max_length=50):
    """
    Fetch all document metadata (Doc) for monitoring, attaching a snippet of
    size `max_length` for preview.
    """
    result = []
    for doc in Doc.query.filter(Doc.active == True).all():  # nopep8
        doc = doc.as_json()
        doc['snippet'] = fetch_snippet(doc['id'], max_length=max_length)
        result.append(doc)
    return result


@app.route('/monitorinit', methods=['GET'])
@flask_login.login_required
@whitelist(app.config.get('MONITORS', []))
def monitorinit():
    users = [{'id': user.id,
              'username': user.username,
              'active': user.is_active()} for user in User.query.all()]
    return flask.jsonify(status='OK', users=users, docs=fetch_docs())


@socketio.on('connect', namespace='/monitor')
def on_connect():
    username = flask_login.current_user.username
    if username in app.config.get('MONITORS', []):  # TODO: fetch from db
        print("{username} has joined /monitor".format(username=username))
        emit('Connected to /monitor',
             {'data': 'connected', 'username': username},
             broadcast=True)
    else:
        return False            # user is not in MONITORS


@socketio.on('disconnect', namespace='/monitor')
def on_disconnect():
    username = flask_login.current_user.username
    print("{username} is leaving".format(username=username))


@socketio.on('join', namespace='/monitor')
def on_join(data):
    username = flask_login.current_user.username
    join_room(data['room'])
    print("{username} has joined room {room}".format(
        username=username, room=data['room']))


@socketio.on('leave', namespace='/monitor')
def on_leave(data):
    username = flask_login.current_user.username
    leave_room(data['room'])
    print("{username} has left room {room}".format(
        username=username, room=data['room']))
