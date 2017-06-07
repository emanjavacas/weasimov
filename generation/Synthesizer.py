# -*- coding: utf-8 -*-

import os

from seqmod.utils import load_model


class Synthesizer(object):

    def __init__(self, model_dir):
        """Constructor

        Parameters
        ----------
        model_dir : str
            Path to dir where saved models live.
        """

        super(Synthesizer, self).__init__()

        self.model_dir = model_dir
        self.models = {}
        self.dicts = {}

    def load(model_names=None):
        """Loads models from the model_dir

        Parameters
        ----------
        model_names : iterable of str
            Names of individual models to load under `self.model_dir`
            If `None`, all models will be noted.

        Notes
        -----
        Individual models are assumed to contain
        (dict, model) tuples, stored after training.

        """
        if not model_names:
            model_names = os.listdir(self.model_dir)

        for name in model_names:
            try:
                p = os.path.join(self.model_dir, name)
                m = load_model(p)
                self.models[name] = m['model']
                self.dicts[name] = m['dict']
            except ValueError:
                print('Unable to load model:', name)

        if not self.models:
            ValueError('No models were loaded.')
        if not self.dicts:
            ValueError('No dictionaties were loaded.')
        if len(self.models) != len(self.dicts):
            ValueError('# dicts does not match # models.')

    def generate(self, text):
        return "Some generated text."

    def sample(self, model_name, seed_texts=None,
               max_seq_len=200, max_tries=5, temperature=1.0,
               method='sample', batch_size=10, ignore_eos=False):
        """Samples a sentence.

        Samples a single sentence from a single model.

        Parameters
        ----------
        model_name : str
            The name of the individual model to sample from.
        seed_texts : str or None (default = None)
            The texts (e.g. the previous sentence) to seed the
            model with. Can be `None`, if no seed text is available.
        max_seq_len : int (default = 200)
            The maximum length of a sentence (expressed in # of
            characters) after which the generation breaks off.
        max_tries : int (default = 5)
            The maximum number of times we attempt to generate
            a sentence, until we get one that ends in <eos>.
        temperature : float (default = 1.0)
            The temperature passed to the sentence generator.
        method : str (default = 'sample')
            The sampling method used; one of:
                * `'sample'`
                * `'argmax'`
                * `'beam'`
        width : int (default=5)
            The width of the beam used if method = `'beam'`.
        batch_size : int (default = 10)
            The sizes of the batches.
        ignore_eos : bool (default = 5)
            Whether to ignore the end-of-sentence symbol.

        Returns
        -------
        str
            A single generated sentence. If all tries failed,
            we return a `" <NO OUTPUT> "` str.

        """
        if not self.models:
            raise AttributeError('Models have not been set yet.')

        tries, hyp = 0, []
        d = self.dicts[model_name]
        m = self.models[model_name]

        while (not hyp or hyp[-1] != d.get_eos()) and tries < max_tries:
            tries += 1
            scores, hyps = m.generate(d, max_seq_len=max_sent_len,
                                      temperature=temperature,
                                      batch_size=batch_size,
                                      beam=beam,
                                      width=width,
                                      ignore_eos=ignore_eos,
                                      method=method,
                                      seed_texts=seed_texts)
            score, hyp = scores[0], hyps[0]

        sent = ''.join(d.vocab[c] for c in hyp)
        sent = sent.replace('<bos>', '') \
                   .replace('<eos>', '\n') \
                   .replace('<par>', '\n')

        return sent or '<NO OUTPUT>'
