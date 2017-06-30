import os


basedir = os.path.abspath(os.path.dirname(__file__))

# model
MODEL_DIR = os.path.join(basedir, 'models')

# database
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'weasimov.db') + '?check_same_thread=False'
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')

# model names
MODEL_NAMES = {
    'char.LSTM.1l.2546h.46e.200b.2.49.post.3.16.pt': 'Ronald Giphart',
    'char.LSTM.1l.2546h.46e.200b.2.49.post.2.78.pt': 'Isaac Asimov',
    'char.LSTM.1l.2546h.46e.200b.2.49.pt': '5000 Romans'
}

# defaults
DEFAULTS = {
    "temperature": 0.35,
    "max_seq_len": 100,
    "batch_size": 3,
    "ignore_eos": False
}
