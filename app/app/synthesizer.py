# -*- coding: utf-8 -*-

import os
import math
import functools
import nltk.data

from seqmod.utils import load_model


def detokenizer(s):
    post_punc = {';', '.', ',',
                 ':', '?', '!',
                 ')', '»', '›',
                 '„', '‚', '❞',
                 '❯', '”', '❜',
                 '’', '...'}
    pre_punc = {'(', '«', '‹',
                '❮', '‟', '❝',
                '❛', '‘', '‛', '“'}

    def func(acc, x):
        if x in post_punc:
            return acc + x
        if acc[-1] in pre_punc:
                return acc + x
        else:
            return acc + ' ' + x
    result = functools.reduce(func, s.split())
    if s.startswith(' '):
        result = ' ' + result
    return result


VOCAB = "\n !%&'()*+,-./0123456789:;=?ABCDEFGHIJKLMNOPQRSTUVWXYZ[]_abcdefghijklmnopqrstuvwxyzÁÅÇÈÉËÍÓÖÜàáâãäåçèéêëìíîïñòóôöøùúûü…⁄"
HYPHENS = '-–‐—−‑‒', '-'
QUOTES = "'′’”\"‚“„ʼ`ʻ‟«¨'´»‘˝″", "'"
SPACES = "\x94\x92\x9a\x96\u200b\x9c\x8e\x9d\x9e\x88", " "
STARS = "∗✷★", "*"
LIGATURES = 'ﬁ', 'fi'
GARBAGE = '�•·€¬©™', ''
MAPPINGS = HYPHENS, QUOTES, SPACES, STARS, LIGATURES, GARBAGE
CHAR_MAPPINGS = {c: r for chars, r in MAPPINGS for c in chars}
REPLACER = str.maketrans(CHAR_MAPPINGS)


def standardize_seed(seed):
    return ''.join(c for c in seed.translate(REPLACER) if c in VOCAB)


def format_seed(seed, artificial_break='<Art-break>', bos='<bos>', eos='<eos>'):
    _seed = f'{seed} {artificial_break}'  # TODO BOS
    seed_with_final_stop = False
    sents = nltk.sent_tokenize(_seed, language='dutch')
    if sents[-1].strip() == artificial_break:
        seed_with_final_stop = True
        sents = sents[:-1]
    else:
        sents[-1] = sents[-1].replace(f' {artificial_break}', '')
    output = []
    for sent in sents[:-1]:
        output += [bos] + list(sent.strip()) + [eos]
    if seed_with_final_stop:
        output += [bos] + list(sents[-1].strip()) + [eos]
    else:
        output += [bos] + list(sents[-1].strip())
    if seed.endswith(' ') and not seed_with_final_stop:
        output += [' ']
    return output


class Synthesizer(object):
    def __init__(self, model_dir, gpu=False, sentence_sampler=None):
        """Constructor

        Parameters
        ----------
        model_dir : str
            Path to dir where saved models live.
        """
        super(Synthesizer, self).__init__()

        self.gpu = gpu
        self.model_dir = model_dir
        self.sentence_sampler = sentence_sampler
        self.models = {}
        self.dicts = {}

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
            If `None`, all models will be loaded.

        Notes
        -----
        Individual models are assumed to be dicts with keys {"model", "dict"}

        """
        if not model_names:
            model_names = [m['path'] for m in self.list_models()]

        for name in model_names:
            if name in self.models:
                print("Not loading [%s], already loaded" % name)
                continue
            try:
                m = load_model(os.path.join(self.model_dir, name))
                if self.gpu:
                    m.cuda()
                self.models[name] = m['model']
                self.dicts[name] = m['dict']
            except (ValueError, OSError):
                print("Couldn't find model [%s]" % name)

        if not self.models:
            ValueError('No models were loaded.')
        if not self.dicts:
            ValueError('No dictionaties were loaded.')
        if len(self.models) != len(self.dicts):
            ValueError('# dicts does not match # models.')

    def sample(self, model_name, seed_texts=None,
               max_seq_len=100, max_tries=1, temperature=1.0,
               method='sample', batch_size=5, ignore_eos=True, **kwargs):
        """
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

        bos, eos = False, False  # default to not prefix <bos> suffix <eos>
        if not seed_texts and self.sentence_sampler is not None:
            try:
                sent = self.sentence_sampler.sample(min_len=25, filters=None)
                seed_texts = [sent]
                bos, eos = True, True
            except:
                print("Couldn't load default seed")
            ignore_eos = True
        else:
            seed_texts = [format_seed(standardize_seed(s)) for s in seed_texts]

        def clean_hyp(hyp):
            text = ''.join(d.vocab[c] for c in hyp) \
                     .replace(d.bos_token, '') \
                     .replace(d.eos_token, ' ') \
                     .replace('<par>', '')
            # Remove quote artifacts at beginning of lines.
            if text.strip().startswith("' '"):
                text = text[2:]
            return text

        def normalize_hyp(hyp):
            bos, eos, par, found = [], [], [], 0
            for idx, c in enumerate(hyp):
                if c == d.get_bos():
                    bos.append(idx - found)
                    found += 1
                elif c == d.get_eos():
                    eos.append(idx - found)
                    found += 1
                elif c == d.s2i.get('<par>'):
                    par.append(idx - found)
                    found += 1

            text = clean_hyp(hyp)
            return {'text': text, 'bos': bos, 'eos': eos, 'par': par}

        def normalize_score(score):
            return round(math.exp(score), 3)

        def filter_valid_hyps(scores, hyps):
            scores, hyps = zip(*[(s, h) for s, h in zip(scores, hyps)
                                 if h[-1] == d.get_eos()])
            return list(scores), list(hyps)

        d, m = self.dicts[model_name], self.models[model_name]
        result = []

        scores, hyps = m.generate(
            d, max_seq_len=max_seq_len,
            temperature=temperature,
            batch_size=batch_size,
            ignore_eos=ignore_eos,
            method=method,
            seed_texts=seed_texts,
            gpu=self.gpu,
            eos=eos, bos=bos,
            **kwargs)

        if not ignore_eos:
            scores, hyps = filter_valid_hyps(scores, hyps)
            left, tries = batch_size - len(hyps), 0
            while left > 0 and tries < max_tries:
                new_scores, new_hyps = m.generate(
                    d, max_seq_len=max_seq_len,
                    temperature=temperature,
                    batch_size=left,
                    ignore_eos=ignore_eos,
                    method=method,
                    seed_texts=seed_texts,
                    gpu=self.gpu,
                    eos=eos, bos=bos,
                    **kwargs)
                scores.extend(new_scores), hyps.extend(new_hyps)
                scores, hyps = filter_valid_hyps(scores, hyps)
                left, tries = len(hyps), tries + 1

        sort_hyps = sorted(zip(scores, hyps), key=lambda p: p[0], reverse=True)
        for score, hyp in sort_hyps:
            if (not ignore_eos) and hyp[-1] != d.get_eos():
                continue
            hyp = dict(normalize_hyp(hyp), score=normalize_score(score))
            result.append(hyp)

        return result
