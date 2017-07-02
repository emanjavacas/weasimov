import os


basedir = os.path.abspath(os.path.dirname(__file__))

# Model
MODEL_DIR = os.path.join(basedir, 'models')

# Database
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'weasimov.db') + '?check_same_thread=False'
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')

# Sentence sampler
FILEDIR = os.path.join(basedir, 'data/novels/')
METAPATH = os.path.join(basedir, 'metainfo.csv')

# Model names
MODEL_NAMES = {
    'fine_asi_giph.LSTM.1l.2048h.64e.256b.pt': 'Isaac Asimov & Ronald Giphart',
    'fine_asi.LSTM.1l.2048h.64e.256b.pt': 'Isaac Asimov',
    'fine_asi_hem.LSTM.1l.2048h.64e.256b.pt': 'Isaac Asimov & Kristien Hemmerechts',
    'MEDIUM.pt': 'Alles'
}

IGNORE_UNNAMED = True  # ignore models if not listed in MODEL_NAMES?

# Defaults
DEFAULTS = {
    "temperature": 0.35,
    "max_seq_len": 100,
    "batch_size": 3,
    "ignore_eos": True,
    "gpu": False
}
