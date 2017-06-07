#!/usr/bin/env python
# -*- coding: utf-8 -*-

from Synthesizer import *
import random
import time

typing_speed = 50


def slow_type(t):
    for l in list(t):
        print(l, end='', flush=True)
        time.sleep(random.random() * 12.0 / typing_speed)
    print('')


def main():
    """
    Demo
    """

    synthesizer = Synthesizer(model_dir='../models')
    #synthesizer.load(model_names=['full'])

    info = '\n' * 10
    info += "######################################################\n"
    info += "##### Synthetic Literature Demo ######################\n"
    info += "######################################################\n\n"
    print(info)

    phrase = 'Geef een zin in (of geef Q om te stoppen): '
    seed = ''

    while seed != 'Q':
        seed = input(phrase)
        """
        generated = synthesizer.generate(model_name='full',
                                         seed_texts=[list(seed)],
                                         max_seq_len=200,
                                         max_tries=5,
                                         temperature=1.0,
                                         method='sample',
                                         batch_size=1,
                                         ignore_eos=False)
        """
        generated = 'Dit is wat, heel langzaam, getypt wordt...'
        print('Voorstel: ')
        slow_type(generated)


if __name__ == '__main__':
    main()
