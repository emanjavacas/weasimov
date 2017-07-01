import os


basedir = os.path.abspath(os.path.dirname(__file__))

# Model
MODEL_DIR = '/home/asibot/resources/models/'

# Database
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'weasimov.db') + '?check_same_thread=False'
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')

# Sentence sampler
FILEDIR = '/home/asibot/resources/novels/'
METAPATH = '/home/asibot/prod/weasimov/metainfo.csv'

# Model names
MODEL_NAMES = {
    'fine_asi_giph.LSTM.1l.2048h.64e.256b.pt': 'Isaac Asimov & Ronald Giphart',
    'fine_asi.LSTM.1l.2048h.64e.256b.pt': 'Isaac Asimov',
    'fine_asi_hem.LSTM.1l.2048h.64e.256b.pt': 'Isaac Asimov & Kristien Hemmerechts',
    'MEDIUM.pt': 'Alles'
}

# Defaults
DEFAULTS = {
    "temperature": 0.35,
    "max_seq_len": 100,
    "batch_size": 3,
    "ignore_eos": False,
    "gpu": False
}
