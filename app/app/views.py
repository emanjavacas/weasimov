
from datetime import datetime
import uuid
import itertools

from palettable.colorbrewer.qualitative import Pastel2_8
import flask
import flask_login
from sqlalchemy import desc

from app import app, db, lm
from .models import User, Text, Edit, Generation
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
        db.session.commit()
        return flask.redirect(flask.url_for('login'))
    return flask.render_template('register.html', title='Sign Up', form=form)


@app.route('/logout', methods=['POST', 'GET'])
@flask_login.login_required
def logout():
    flask_login.logout_user()
    return flask.redirect(flask.url_for('login'))


@app.route('/')
@app.route('/index', methods=['GET', 'POST'])
@flask_login.login_required
def index():
    return flask.render_template('index.html')


def get_session_value(key, session):
    return session.get(key) or app.config["DEFAULTS"][key]


@app.route('/init', methods=['GET'])
@flask_login.login_required
def init():
    user_id = int(flask_login.current_user.id)
    user = User.query.get(user_id)
    session = user.session or {}
    text = db.session.query(Text) \
                     .filter(Text.user_id == user_id) \
                     .order_by(desc(Text.timestamp)) \
                     .first()
    content_state = text.text if text is not None else None
    payload = {
        # app state data
        "username": user.username,
        "models": format_models(),
        # user session data
        "temperature": get_session_value("temperature", session),
        "maxSeqLen": get_session_value("max_seq_len", session),
        "hyps": session.get("hyps", []),
        # last editor state
        "contentState": content_state}
    return flask.jsonify(status="OK", session=payload)


@app.route('/savechange', methods=['POST'])
@flask_login.login_required
def savechange():
    data = flask.request.json
    timestamp = datetime.fromtimestamp(data['timestamp'])
    user_id = int(flask_login.current_user.id)
    edit = Edit(edit=data['edit'], timestamp=timestamp, user_id=user_id)
    db.session.add(edit)
    db.session.commit()
    return flask.jsonify(status='OK', message='Changes saved.')


@app.route('/savesuggestion', methods=['POST'])
@flask_login.login_required
def savesuggestion():
    data = flask.request.json
    timestamp = datetime.fromtimestamp(data['timestamp'])
    generation = Generation.query.filter_by(
        generation_id=data['generation_id'])
    generation.selected = True
    generation.draft_entity_id = data['draft_entity_id']
    generation.selected_timestamp = timestamp
    db.session.commit()
    return flask.jsonify(status='OK', message='Suggestion updated.')


@app.route('/savedoc', methods=['POST'])
@flask_login.login_required
def savedoc():
    data = flask.request.json
    timestamp = datetime.fromtimestamp(data['timestamp'])
    user_id = int(flask_login.current_user.id)
    text = Text(text=data['text'], timestamp=timestamp, user_id=user_id)
    db.session.add(text)
    db.session.commit()
    return flask.jsonify(status='OK', message='Document saved.')


@app.route('/savesession', methods=['POST'])
@flask_login.login_required
def savesession():
    user = User.query.get(int(flask_login.current_user.id))
    user.session = flask.request.json['session']
    db.session.commit()
    return flask.jsonify(status="OK", message='Session saved.')


@app.route('/generate', methods=['POST'])
@flask_login.login_required
def generate():
    user_id = int(flask_login.current_user.id)
    model = flask.request.json['model_path']
    app.synthesizer.load(model_names=(model,))  # maybe load model
    seed = flask.request.json["selection"]
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
            db.session.add(Generation(
                model=model,
                seed=seed or '',
                temp=temperature,
                text=hyp['text'],
                generation_id=generation_id,
                timestamp=timestamp,
                user_id=user_id))
            hyp["generation_id"] = generation_id
            hyp["timestamp"] = timestamp
            hyp["model"] = model
        db.session.commit()
        return flask.jsonify(status='OK', hyps=hyps, seed=seed, model=model)
    except Exception as e:
        return flask.jsonify(status='Error', message=str(e)), 500
