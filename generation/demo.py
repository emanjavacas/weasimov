#!/usr/bin/env python
# -*- coding: utf-8 -*-

from Synthesizer import *
import random
import time
from prompt_toolkit import prompt
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.completion import Completer, Completion


class AsimovCompleter(Completer):
    def __init__(self, synthesizer, model_name, temperature):
        self.synthesizer = synthesizer
        self.model_name = model_name
        self.temperature = temperature

    def get_completions(self, document, complete_event):
        completion = self.synthesizer.sample(
            self.model_name, seed_texts=[[document.current_line_before_cursor]],
            temperature=self.temperature, ignore_eos=True)
        yield Completion(' %s' % completion, start_position=0)

typing_speed = 50

def slow_type(t):
    for l in list(t):
        print(l, end='', flush=True)
        time.sleep(random.random() * 12.0 / typing_speed)
    print('')


def main(model_name, temperature):
    """
    Demo
    """

    synthesizer = Synthesizer(model_dir='../models')
    synthesizer.load([model_name])

    info = '\n' * 5
    info += "######################################################\n"
    info += "##### Synthetic Literature Demo ######################\n"
    info += "######################################################\n\n"
    print(info)

    seed = ''
    history = InMemoryHistory()

    try:
        completer = AsimovCompleter(synthesizer, model_name, temperature)
        while True:
            text = prompt('> ', history=history,
                          completer=completer,
                          complete_while_typing=False)
            slow_type(text)
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--model_name', default='char.LSTM.1l.1046h.24e.200b.2.69.pt')
    parser.add_argument('--temperature', default=0.2, type=float)
    args = parser.parse_args()

    main(args.model_name, args.temperature)
