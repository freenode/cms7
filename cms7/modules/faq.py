from pathlib2 import PurePosixPath

import logging

from . import Module
from ..source import load_source
from ..util import meta_get_one


class FaqEntry:
    def __init__(self, faq, name, source):
        self.faq = faq
        self.name = name
        self.title = meta_get_one(source, 'title')
        self.slug = meta_get_one(source, 'slug', name.name)
        self.template = meta_get_one(source, 'template', 'faq.html')
        self.source = source

    def render(self, gs):
        this = FaqEntryWrapper(gs, self)
        return gs.render_template(self.template, entry=this)


class FaqEntryWrapper:
    def __init__(self, gs, entry):
        self.gs = gs
        self.entry = entry

    def __getattr__(self, k):
        return getattr(self.entry, k)

    @property
    def url(self):
        return self.gs.url_for(self.name)

    def render(self):
        return self.source.render(self.gs)


class FaqIndex:
    def __init__(self, faq, name, data):
        self.faq = faq
        self.name = name
        self.title = data['title']
        self.cats = data['cats']
        self.template = data.get('template', 'faq_index.html')
        self.entries = set()
        for cat in self.cats:
            self.entries |= self.faq.cats[cat]
        self.promote = []
        promote = data.get('promote', [])
        for d in promote:
            entry = self.faq.by_name[d['name']]
            caption = d['caption'] or entry.title
            icon = d['icon'] or None
            self.promote.append({
                'entry': entry,
                'caption': caption,
                'icon': icon
            })

    def render(self, gs):
        this = FaqIndexWrapper(gs, self)
        return gs.render_template('faq_index.html', index=this)


class FaqIndexWrapper:
    def __init__(self, gs, index):
        self.gs = gs
        self.index = index
        self.entries = sorted((FaqEntryWrapper(self.gs, x) for x in self.entries),
                              key=lambda x: x.title)
        self.promote = []
        for item in self.index.promote:
            self.promote.append({
                'entry': FaqEntryWrapper(self.gs, item['entry']),
                'caption': item['caption'],
                'icon': item['icon']
            })

    def __getattr__(self, k):
        return getattr(self.index, k)

    @property
    def url(self):
        return self.gs.url_for(self.name)


class Faq(Module):
    def __init__(self, *a, indexes, source, root, index_root, **kw):
        super().__init__(*a, **kw)

        self.source = self._dir / source
        self.root = PurePosixPath(root)
        self.index_root = PurePosixPath(index_root)
        self.indexes = indexes

        self.by_name = {}
        self.cats = {}

    def prepare(self):
        for d in self.source.iterdir():
            if d.is_dir():
                for s in d.iterdir():
                    if self.is_ignored(s):
                        continue
                    source = load_source(s)
                    name = self.path_to_name(s)
                    entry = FaqEntry(self, name, source)
                    self.by_name[str(name)] = entry
                    self.cats.setdefault(d.name, set()).add(entry)
        self.log(logging.INFO, 'Found %d sources in %s (%d subdirs)',
                 sum(map(len, self.cats.values())), self.source.resolve(), len(self.cats))

    def run(self, gen):
        for cat, el in self.cats.items():
            for entry in el:
                gen.add_render(entry.name, self.root / entry.slug, entry.render)
        for name, data in self.indexes.items():
            index = FaqIndex(self, name, data)
            link = self.path_to_name(self.source / 'index' / index.name)
            self.log(logging.INFO, 'Creating index %s with %d entries', link, len(index.entries))
            gen.add_render(link, self.index_root / index.name, index.render)
