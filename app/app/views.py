
from functools import wraps
from datetime import datetime
import uuid
import itertools

from palettable.colorbrewer.qualitative import Pastel2_8
import flask
import flask_login
from flask_socketio import join_room, leave_room, emit
from sqlalchemy import desc, and_

from app import app, db, lm
from . import socketio
from .models import User, Doc, Text, Edit, Generation
from .forms import LoginForm, RegisterForm, EmailForm, PasswordForm
from .utils import send_email, ts


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
    if form.validate_on_submit() and form.validate_fields():
        user = form.get_user()
        flask.session['remember_me'] = form.remember_me.data
        flask_login.login_user(user, remember=form.remember_me.data)
        user.active = True
        db.session.commit()
        # websocket
        socketio.emit('login', {'user_id': user.id}, namespace='/monitor')
        return flask.redirect(flask.url_for('index'))
    return flask.render_template('login.html', title='Sign in', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
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


def get_last_text(doc_id):
    return Text.query.filter(Text.doc_id == doc_id) \
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


def get_snippet(text, max_length=50):
    """
    Get a snippet of length `max_length` from the beginning of the last version
    of a given document.
    """
    snippet = ''
    if text is not None:        # Document is not empty
        for block in text.text['blocks']:
            if len(snippet) >= max_length:
                return snippet
            block_text = block['text']
            stop = min(max_length - len(snippet), len(block_text))
            snippet += block_text[:stop]
        return snippet
    else:
        return ''


def get_wordcount(text):
    wordcount = 0
    if text is not None:
        for block in text.text['blocks']:
            wordcount += len(block['text'].split())
    return wordcount


@app.route('/init', methods=['GET'])
@flask_login.login_required
def init():
    user_id = int(flask_login.current_user.id)
    user = User.query.get(user_id)
    docs = get_user_docs(user_id).all()
    doc_id = docs[0].id
    text = get_last_text(doc_id)
    payload = {
        # app state data
        "username": user.username,
        # - TODO: move monitor whitelisting to db
        "isMonitor": user.username in app.config.get('MONITORS', []),
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
    emit('savechange', data, room=str(doc.id), namespace='/monitor')
    return flask.jsonify(status='OK')


@app.route('/savesuggestion', methods=['POST'])
@flask_login.login_required
def savesuggestion():
    """
    id: str, generation id
    doc_id: int, id of doc where the action took place
    selected: True, (optional), requires `draft_entity_id`
    draft_entity_id: str
    dismissed: True, (optional)
    timestamp: int
    """
    data = flask.request.json
    timestamp = datetime.fromtimestamp(data['timestamp'])
    generation = Generation.query.filter_by(id=data['id']).first()
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
    text = get_last_text(doc.id)
    snippet = get_snippet(text)
    wordcount = get_wordcount(text)
    data = dict(doc.as_json(), snippet=snippet, wordcount=wordcount)
    socketio.emit('createdoc', data, namespace='/monitor')
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
    text = get_last_text(doc.id)
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
    doc_id = flask.request.json['doc_id']
    doc = get_user_docs(user_id, doc_id=doc_id).first()
    doc.active = False
    db.session.commit()
    # websocket
    socketio.emit('removedoc', {'doc_id': doc_id}, namespace='/monitor')
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
    socketio.emit('editdocname', data, namespace='/monitor')
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
        generation_id = str(uuid.uuid4())
        for hyp in hyps:
            generation = Generation(
                generation_id=generation_id,
                user_id=user_id,
                seed_doc_id=seed_doc_id,
                model=model,
                seed=seed or '',
                temperature=temperature,
                max_seq_len=max_seq_len,
                text=hyp['text'],
                timestamp=timestamp)
            db.session.add(generation)
            db.session.flush()  # ensure generation gets the id
            hyp['id'] = generation.id
            hyp["generation_id"] = generation_id
            hyp["timestamp"] = timestamp
            hyp["model"] = model
        db.session.commit()
        elapsed = round((datetime.utcnow() - timestamp).total_seconds(), 2)
        return flask.jsonify(status='OK',
                             hyps=hyps,
                             seed=seed,
                             model=model,
                             elapsed=elapsed)
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


def fetch_docs(max_length=50):
    """
    Fetch all document metadata (Doc) for monitoring, attaching a snippet of
    size `max_length` for preview.
    """
    result = []
    for doc in Doc.query.filter(Doc.active == True).all():  # nopep8
        doc = doc.as_json()
        text = get_last_text(doc['id'])
        snippet = get_snippet(text, max_length=max_length)
        wordcount = get_wordcount(text)
        result.append(dict(doc, snippet=snippet, wordcount=wordcount))
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


@app.route('/reset', methods=['GET', 'POST'])
def reset():
    form = EmailForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.email.data).first()
        if user is None:
            form.email.errors = ('Opgegeven email-adres is onbekend.')
            return flask.render_template('reset.html', form=form)
        subject = "Wachtwoord vergeten"
        token = ts.dumps(user.username, salt='recover-key')

        recover_url = flask.url_for('reset_with_token', token=token, _external=True)
        html = flask.render_template('recover_email.html', recover_url=recover_url)
        send_email(user.username, subject, html)
        return flask.redirect(flask.url_for('index'))
    return flask.render_template('reset.html', form=form)


@app.route('/reset/<token>', methods=['GET', 'POST'])
def reset_with_token(token):
    email = ts.loads(token, salt="recover-key", max_age=86400)
    form = PasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=email).first()
        user.password = form.password.data
        db.session.add(user)
        db.session.commit()
        return flask.redirect(flask.url_for('login'))
    return flask.render_template('reset_with_token.html', form=form, token=token)