# -*- coding: utf-8 -*-

import os

from seqmod.utils import load_model


class Synthesizer(object):

    def __init__(self, model_dir):

        super(Synthesizer, self).__init__()

        self.model_dir = model_dir
        self.models = {}
        self.dicts = {}

    def load(model_names=None):
        if not model_names:
            model_names = os.listdir(self.model_dir)

        for name in model_names:
            try:
                p = os.path.join(self.model_dir, name)
                # assume we pickled (dict, model) tuples:
                d, m = load_model(p)
                self.models[name] = d
                self.dicts[name] = d
            except ValueError:
                print('Unable to load model:', name)

        if not self.models:
            ValueError('No models were loaded.')
        if not self.dicts:
            ValueError('No dictionaties were loaded.')
        if len(self.models) != len(self.dicts):
            ValueError('# dicts does not match # models.')

    def sample(self, model_name, seed_text=None,
               max_seq_len=200, max_tries=5):
        """Sample a single sentence from a given LM."""
        if not self.models:
            raise AttributeError('Models have not been set yet.')

        tries, hyp = 0, []
        d = self.dicts[model_name]
        e = d.get_eos()
        m = self.models[model_name]

        while (not hyp or hyp[-1] != e) and tries < max_tries:
            tries += 1
            scores, hyps = m.generate(d, max_seq_len=max_sent_len, **kwargs)
            score, hyp = scores[0], hyps[0]

        sent = ''.join(d.vocab[c] for c in hyp)
        sent = sent.replace('<bos>', '').replace('<eos>', '')

        if not sent:
            sent = ' <NO OUTPUT> '

        return sent
