import os
import sys
sys.path.append('../app')

import collections
import itertools

from palettable.colorbrewer.qualitative import Pastel2_8
import jinja2
import distance
import imageio
imageio.plugins.ffmpeg.download()

from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains

from app import db, models


def colors():
    color_palette = itertools.cycle(Pastel2_8.colors)
    return lambda: next(color_palette)


def get_versions(username):
    user_id = models.User.query.filter_by(username=username).first().id
    for version in models.Text.query.filter_by(
            user_id=user_id).order_by(models.Text.timestamp.asc()):
            yield version.text


def get_current_text(username):
    user_id = models.User.query.filter_by(username=username).first().id
    text = models.Text.query.filter_by(user_id=user_id).order_by(
        models.Text.timestamp.desc()).first().text
    return text


class Converter:
    COLORMAP = collections.defaultdict(colors())

    def __init__(self, contentstate, entitymap):
        self.contentstate = contentstate
        self.entitymap = entitymap
        self.env = jinja2.Environment(
            loader=jinja2.FileSystemLoader('static/templates'),
            autoescape=jinja2.select_autoescape(['html', 'xml'])
        )

    def render(self):
        template = self.env.get_template('index.html')
        return template.render(
            title='Weasimov', blocks=(self._setup_block(block)
                                      for block in self.contentstate))

    def _setup_entity_spans(self, text, entities):
        spans = []
        for entity in entities:
            length, offset = entity['length'], entity['offset']
            props = self.entitymap[str(entity['key'])]
            model = props['data']['model']['path']
            r, g, b = Converter.COLORMAP[model]
            source = props['data']['source']
            target = text[offset: offset + length]
            a = 1 - distance.levenshtein(source, target, normalized=True)
            color = f'rgba({r},{g},{b},{a:.1f})'
            spans.append((offset, offset + length,
                         {'text': target, 'color': color,
                          'model': model}))
        return sorted(spans, key=lambda i: i[0])

    def _setup_block(self, block):
        text = block['text']
        text_start, text_end = 0, len(text)
        # setup entity spans
        spans = self._setup_entity_spans(text, block['entityRanges'])
        # insert author spans
        for start, end, _ in spans[:]:
            if start > text_start:
                spans.append((text_start, start,
                             {'text': text[text_start: start]}))
            text_start = end
        # add trailing author text.
        if text_start < text_end:
            spans.append((text_start, text_end,
                         {'text': text[text_start: text_end]}))
        spans = [d for _, _, d in sorted(spans, key=lambda i: i[0])]
        if block['key'] == self.focus_block:
            spans = [{'text': '', 'id': 'focus'}] + spans
        return spans

    def set_focus_block(self, prev_blocks=None):
        cur_blocks = self.get_blocks_dict()
        if not prev_blocks:
            # if no previous blocks are available, we randomly pick one of
            # the current blocks:
            self.focus_block = list(cur_blocks.keys())[-1]
            #print(f'no new blocks! selected: {self.focus_block}')
        else:
            new_blocks = [k for k in cur_blocks if k not in prev_blocks]
            if new_blocks:
                # if there are new blocks, we randomly pick one of those:
                self.focus_block = new_blocks[-1]
                #print(f'new blocks! selected: {self.focus_block}')
            else:
                overlap_blocks = [k for k in cur_blocks if k in prev_blocks]
                scores = []
                for k in overlap_blocks:
                    b1, b2 = prev_blocks[k], cur_blocks[k]
                    if b1 == b2:
                        scores.append((0, k))
                    else:
                        s = distance.levenshtein(b1, b2, normalized=True)
                        scores.append((s, k))
                self.focus_block = sorted(scores)[::-1][0][1]
                #print(f'no new blocks! selected: {self.focus_block}')

    def get_blocks_dict(self):
        return {b['key']: b['text'] for b in self.contentstate}


if __name__ == '__main__':
    max_nb_frames = 200
    display = Display(visible=0, size=(300, 300))
    display.start()

    browser = webdriver.Chrome()

    p = 'file:///Users/mike/GitRepos/weasimov/reconstruction/'
    statefile = 'state.html'
    statepic = 'state.png'
    animationfile = 'movie.mp4'

    cnt = 0
    prev_blocks = None
    with imageio.get_writer(animationfile, mode='I', fps=0.5) as writer:
        for draft_doc in get_versions(username="ronald"):

            c = Converter(draft_doc['blocks'], draft_doc['entityMap'])

            blocks = c.get_blocks_dict()
            c.set_focus_block(prev_blocks)

            if blocks:
                prev_blocks = blocks
            with open(statefile, "w") as out:
                out.write(c.render())

            browser.get(p + statefile)
            focus = browser.find_element_by_id('focus')
            browser.execute_script("arguments[0].scrollIntoView();", focus)

            browser.save_screenshot(statepic)
            image = imageio.imread(statepic)
            writer.append_data(image)

            cnt += 1
            if cnt >= max_nb_frames:
                break
