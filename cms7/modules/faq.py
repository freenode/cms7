from pathlib2 import PurePosixPath

import logging

from . import Module
from ..source import load_source
from ..util import meta_get_one


class FaqEntry:
    def __init__(self, faq, name, source):
        self.faq = faq
        self.name = name
        self.title = meta_get_one(source.meta, 'title')
        self.slug = meta_get_one(source.meta, 'slug', name.name)
        self.template = meta_get_one(source.meta, 'template', 'faq.html')
        self.source = source

    def render(self, gs):
        self.content = self.source.render(gs)
        return gs.render_template(self.template, title=self.title, article=self)


class FaqIndex:
    def __init__(self, faq, name, data):
        self.faq = faq
        self.name = name
        self.title = data['title']
        self.cats = data['cats']
        self.template = data.get('template', 'faq_index.html')
        self.promote = data.get('promote', [])
        self.entries = set()
        for cat in self.cats:
            self.entries |= self.faq.cats[cat]

    def render(self, gs):
        return gs.render_template('faq_index.html', title=self.title, index=self)


class Faq(Module):
    def __init__(self, *a, indexes, source, root, index_root, **kw):
        super().__init__(*a, **kw)

        self.source = self._dir / source
        self.root = PurePosixPath(root)
        self.index_root = PurePosixPath(index_root)
        self.indexes = indexes

        self.cats = {}

    def prepare(self):
        for d in self.source.iterdir():
            if d.is_dir():
                for s in d.iterdir():
                    source = load_source(s)
                    entry = FaqEntry(self, self.path_to_name(s), source)
                    self.cats.setdefault(d.name, set()).add(entry)
        self.log(logging.INFO, 'Found %d sources in %s (%d subdirs)',
                 sum(map(len, self.cats.values())), self.source.resolve(), len(self.cats))

    def run(self, gen):
        for cat, el in self.cats.items():
            for entry in el:
                gen.add_render(entry.name, self.root / entry.slug, entry.render)
        for name, data in self.indexes.items():
            index = FaqIndex(self, name, data)
            link = self.source / 'index' / index.name
            self.log(logging.INFO, 'Creating index %s with %d entries', link, len(index.entries))
            gen.add_render(link, self.index_root / index.name, index.render)
