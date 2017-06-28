import json
from datetime import datetime
import unicodedata
import uuid
import flask
import flask_login
from app import app, db, lm
from .models import User, Text, Edit, Generation
from .forms import LoginForm, RegisterForm


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
    user_id = flask_login.current_user.id
    user = db.session.query(User).filter(User.id == user_id).first()
    session = user.session or {}
    text = db.session.query(Text).order_by(Text.timestamp).first()
    text = text.text if text is not None else None
    payload = {"temperature": get_session_value("temperature", session),
               "maxSeqLen": get_session_value("max_seq_len", session),
               "contentState": text,
               "models": format_models()}
    return flask.jsonify(status="OK", session=payload)


@app.route('/savechange', methods=['POST'])
@flask_login.login_required
def savechange():
    data = flask.request.json
    timestamp = datetime.fromtimestamp(data['timestamp'])
    edit = Edit(edit=data['edit'], timestamp=timestamp)
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
    text = Text(text=data['text'], timestamp=timestamp)
    db.session.add(text)
    db.session.commit()
    return flask.jsonify(status='OK', message='Document saved.')


@app.route('/generate', methods=['POST'])
@flask_login.login_required
def generate():
    model_name = flask.request.json['model_path']
    app.synthesizer.load(model_names=(model_name,))  # maybe load model
    seed = flask.request.json["selection"]
    temperature = float(flask.request.json['temperature'])
    max_seq_len = int(flask.request.json['max_seq_len'])
    seed = None if not seed else [seed]
    try:
        hyps = app.synthesizer.sample(
            model_name=model_name,
            seed_texts=seed,
            temperature=temperature,
            ignore_eos=True,
            max_seq_len=max_seq_len,
            max_tries=1)
        timestamp = datetime.utcnow()
        for hyp in hyps:
            generation_id = str(uuid.uuid4())
            db.session.add(Generation(
                model=model_name,
                seed=seed[0] if seed is not None else '',
                temp=temperature,
                text=hyp['text'],
                generation_id=generation_id,
                timestamp=timestamp))
            hyp['generation_id'] = generation_id
        db.session.commit()
        return flask.jsonify(status='OK', hyps=hyps)
    except ValueError as e:
        return flask.jsonify(status='Error', message=str(e)), 500
