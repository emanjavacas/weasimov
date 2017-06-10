import os
basedir = os.path.abspath(os.path.dirname(__file__))

# model
MODEL_DIR = os.path.join(basedir, 'models')
MODEL_NAMES = ['char-asi-sent.LSTM.1l.1046h.24e.100b.2.65.pt',
               'char-asi-sent.LSTM.1l.1046h.24e.200b.2.96.pt',
               'char-asi-sent.LSTM.1l.2546h.46e.100b.2.39.pt',
               'char-asi-sent.LSTM.2l.512h.24e.100b.2.94.pt',
               'char-asi-sent.LSTM.2l.512h.24e.100b.3.22.pt',
               'char-asi-sent.LSTM.2l.1046h.24e.100b.2.97.pt',
               'char-asi-sent.LSTM.3l.512h.24e.100b.3.21.pt',
               'char.LSTM.1l.1046h.24e.200b.2.69.pt',
               'char.LSTM.1l.2546h.46e.100b.2.98.pt']
