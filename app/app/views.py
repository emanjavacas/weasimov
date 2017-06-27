import json
import datetime
import unicodedata
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
        return flask.render_template('register.html', title='Sign In', form=form)
    if form.validate_on_submit() and form.validate_fields():
        user = User(username=form.username.data,
                    password=form.password.data)
        db.session.add(user)
        db.session.commit()
        return flask.redirect(flask.url_for('login'))
    return flask.render_template('register.html', title='Sign Up', form=form)


@app.route('/')
@app.route('/index', methods=['GET', 'POST'])
@flask_login.login_required
def index():
    text = Text.query.order_by('timestamp desc').first()
    if text is None:
        text = "Bieb, bieb!"
    return flask.render_template('index.html')


@app.route('/logout', methods=['POST', 'GET'])
@flask_login.login_required
def logout():
    flask_login.logout_user()
    return flask.redirect(flask.url_for('login'))


@app.route('/savechange', methods=['POST'])
@flask_login.login_required
def savechange():
    data = flask.request.json
    edit = Edit(start=int(data['start']), end=int(data['end']), edit=data['edit'])
    db.session.add(edit)
    db.session.commit()
    return flask.jsonify(status='OK', message='changes saved.')


@app.route('/savedoc', methods=['POST'])
@flask_login.login_required
def savedoc():
    data = flask.request.json
    text = Text(text=data['text'])
    db.session.add(text)
    db.session.commit()
    return flask.jsonify(status='OK', message='document saved.')


@app.route('/generate', methods=['POST'])
@flask_login.login_required
def generate():
    seed = flask.request.json["selection"]
    temperature = float(flask.request.json['temperature'])
    max_seq_len = int(flask.request.json['max_seq_len'])
    batch_size = int(flask.request.json['batch_size'])
    seed = None if not seed else [seed]
    print(seed)
    try:
        hyps = app.synthesizer.sample(
            model_name=flask.request.json['model_name'],
            seed_texts=seed,
            temperature=temperature,
            ignore_eos=True,
            max_seq_len=max_seq_len,
            batch_size=batch_size,
            max_tries=1)
        timestamp = datetime.datetime.utcnow()
        for hyp in hyps:
            print(hyp['text'])
            db.session.add(Generation(
                model=flask.request.json['model_name'],
                seed=seed[0] if seed is not None else '',
                temp=temperature,
                text=hyp['text'],
                timestamp=timestamp))
        db.session.commit()
        return flask.jsonify(status='OK', hyps=hyps)
    except ValueError as e:
        return flask.jsonify(status='Error', message=str(e)), 500


@app.route('/temperature', methods=['POST'])
def temperature():
    app.synthesizer.temperature = float(flask.request.json["data"])
    return flask.jsonify(
        status='OK',
        message=f'temperature adjusted to {app.synthesizer.temperature}',
        temperature=app.synthesizer.temperature)


@app.route('/models', methods=['GET'])
def models():
    return flask.jsonify(status='OK', models=app.synthesizer.list_models())


@app.route('/load_model', methods=['POST'])
def load_model():
    model_name = flask.request.json['model_name']
    app.synthesizer.load(model_names=(model_name,))
    return flask.jsonify(status='OK',
                         model={'path': model_name,
                                'loaded': True})
