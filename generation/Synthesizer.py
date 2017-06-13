# -*- coding: utf-8 -*-

import os
import math

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
        self.temperature = 0.35

    def list_models(self, only_loaded=False):
        return [{'path': f, 'loaded': f in self.models}
                for f in os.listdir(self.model_dir)
                if f.endswith('pt') and (not only_loaded or f in self.models)]

    def load(self, model_names=None):
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
            model_names = [m['path']
                           for m in self.list_models(only_loaded=True)]

        for name in model_names:
            try:
                m = load_model(os.path.join(self.model_dir, name))
                self.models[name] = m['model']
                self.dicts[name] = m['dict']
            except (ValueError, FileNotFoundError):
                print("Couldn't find model [%s]" % name)
        if not self.models:
            ValueError('No models were loaded.')
        if not self.dicts:
            ValueError('No dictionaties were loaded.')
        if len(self.models) != len(self.dicts):
            ValueError('# dicts does not match # models.')

    def sample(self, model_name, seed_texts=None,
               max_seq_len=200, max_tries=5, temperature=1.0,
               method='sample', batch_size=5, ignore_eos=True):
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
        batch_size : int (default = 10)
            The sizes of the batches.
        ignore_eos : bool (default = False)
            Whether to ignore the end-of-sentence symbol.

        Returns
        -------
        [{'text': hypothesis text (str),
          'bos': [pointers to original bos tokens (int)],
          'eos': [pointers to original eos tokens (int)],
          'pad': [pointers to original par tokens (int),
          'score': hypothesis score (float)}
         ...]

        """
        if not self.models:
            raise ValueError('Models have not been set yet.')

        def normalize_hyp(hyp):
            bos, eos, par, found = [], [], [], 0
            for idx, c in enumerate(hyp):
                if c == d.get_bos():
                    bos.append(idx - found)
                    found += 1
                elif c == d.get_eos():
                    eos.append(idx - found)
                    found += 1
                elif c == d.s2i['<par>']:
                    par.append(idx - found)
                    found += 1

            text = ''.join(d.vocab[c] for c in hyp)
            return {'text': text
                    .replace(d.bos_token, '')
                    .replace(d.eos_token, '\n')
                    .replace('<par>', '\n'),
                    'bos': bos, 'eos': eos, 'par': par}

        def normalize_score(score):
            return round(math.exp(score), 3)

        def has_valid_hyp(hyps):
            for hyp in hyps:
                if hyp[-1] == d.get_eos():
                    return True
            return False

        d = self.dicts[model_name]
        m = self.models[model_name]
        out = []

        if ignore_eos:
            scores, hyps = m.generate(
                d, max_seq_len=max_seq_len,
                temperature=temperature,
                batch_size=batch_size,
                ignore_eos=ignore_eos,
                method=method,
                bos=True,
                seed_texts=seed_texts)

        else:
            hyps, tries = [], 0
            while (hyps and not has_valid_hyp(hyps)) and tries < max_tries:
                scores, hyps = m.generate(
                    d, max_seq_len=max_seq_len,
                    temperature=temperature,
                    batch_size=batch_size,
                    ignore_eos=ignore_eos,
                    method=method,
                    bos=True,
                    seed_texts=seed_texts)
                tries += 1

        for score, hyp in sorted(zip(scores, hyps), key=lambda p: p[0], reverse=True):
            if not ignore_eos and hyp[-1] == d.get_eos():
                continue
            out.append(dict(normalize_hyp(hyp), score=normalize_score(score)))

        return out
