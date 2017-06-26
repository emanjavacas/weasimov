import json
import unicodedata
import flask
from app import app, db
from .models import Edit, Text, Generation, User


@app.route('/')
def index():
    return flask.render_template('index.html')


@app.route('/savechange', methods=['POST'])
def savechange():
    data = flask.request.json
    edit = Edit(start=int(data['start']), end=int(data['end']), edit=data['edit'])
    db.session.add(edit)
    db.session.commit()
    return flask.jsonify(status='OK', message='changes saved.')


@app.route('/savedoc', methods=['POST'])
def savedoc():
    data = flask.request.json
    text = Text(text=data['text'])
    db.session.add(text)
    db.session.commit()
    return flask.jsonify(status='OK', message='document saved.')


@app.route('/generate', methods=['POST'])
def generate():
    seed = flask.request.json["selection"]
    temperature = float(flask.request.json['temperature'])
    max_seq_len = int(flask.request.json['max_seq_len'])
    batch_size = int(flask.request.json['batch_size'])
    seed = None if not seed else [seed]
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
            db.session.add(Generation(
                model=flask.request.json['model_name'],
                seed=seed[0],
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
