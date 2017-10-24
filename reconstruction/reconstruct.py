import argparse
import collections
import itertools
import json
import sqlite3

import distance
import jinja2
import palettable.colorbrewer.qualitative
import pandas as pd


def colors():
    color_palette = itertools.cycle(palettable.colorbrewer.qualitative.Pastel2_8.colors)
    return lambda: next(color_palette)


def get_current_text(username, db):
    connection = sqlite3.connect(db)
    cursor = connection.cursor()
    userid = cursor.execute('SELECT id FROM user WHERE username=?', (username,)).fetchone()[0]
    cursor.execute('SELECT text FROM text WHERE user_id=? ORDER BY date(timestamp) DESC Limit 1', (userid,))
    text = cursor.fetchone()[0]
    connection.close()
    return json.loads(text)


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
            title='Weasimov', blocks=(self._setup_block(block) for block in self.contentstate))

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
        print(block['inlineStyleRanges'])
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
        return [d for _, _, d in sorted(spans, key=lambda i: i[0])]


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('username')
    parser.add_argument('database')
    args = parser.parse_args()
    draft_doc = get_current_text(args.username, args.database)
    c = Converter(draft_doc['blocks'], draft_doc['entityMap'])
    with open("G.html", "w") as out:
        out.write(c.render())
