import os
import matplotlib.pyplot as plt
import matplotlib.colors as colors


basedir = os.path.abspath(os.path.dirname(__file__))

# model
MODEL_DIR = os.path.join(basedir, 'models')

# database
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'weasimov.db') + '?check_same_thread=False'
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')

# model names
MODEL_NAMES = {
    'asimov.pt': 'Isaac Asimov',
    'giphart.pt': 'Ronald Giphart',
    'char.LSTM.1l.2546h.46e.200b.2.49.pt.cpu.pt': '5000 romans'
}

COLOR_CODES = [colors.to_rbga(c) for c in plt.get_cmap('Pastel2').colors]