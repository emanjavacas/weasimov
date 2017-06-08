#!/usr/bin/env python
# -*- coding: utf-8 -*-

from Synthesizer import *
import random
import time
from prompt_toolkit import prompt
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.completion import Completer, Completion


class AsimovCompleter(Completer):
    def __init__(self, synthesizer):
        self.synthesizer = synthesizer

    def get_completions(self, document, complete_event):
        completion = self.synthesizer.generate(document.current_line_before_cursor)
        yield Completion(' %s' % completion, start_position=0)

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

    info = '\n' * 5
    info += "######################################################\n"
    info += "##### Synthetic Literature Demo ######################\n"
    info += "######################################################\n\n"
    print(info)

    seed = ''
    history = InMemoryHistory()

    try:
        while True:
            text = prompt('> ', history=history, completer=AsimovCompleter(synthesizer),
                          complete_while_typing=False)
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
            slow_type(text)
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
