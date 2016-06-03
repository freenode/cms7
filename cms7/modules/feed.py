import logging

from pathlib2 import PurePosixPath

from feedgenerator.django.utils.feedgenerator import Atom1Feed, Rss201rev2Feed, Enclosure

from . import Module
from .blog import Blog

from ..source import load_source
from ..util import meta_get_one


class Feed:
    def __init__(self, parent, name, ftype):
        self.parent = parent
        self.name = name
        self.ftype = ftype

    def render(self, gs):
        blog = self.parent.blog.get_api(gs)
        feed = self.ftype(self.parent.cfg['title'], gs.url_for(self.name, absolute=True), self.parent.cfg['description'])

        for a in reversed(blog.articles[-15:]):
            text = a.source.render(gs, paragraphs=3, hyphenate=False)
            feed.add_item(a.title, gs.url_for(a.name, absolute=True), text, author_name=a.author)

        return feed.writeString('utf-8') + '\n'


class FeedModule(Module):
    def __init__(self, *a, module, output, **kw):
        self.cfg = {}
        self.cfg['title'] = kw.pop('title')
        self.cfg['link'] = kw.pop('link')
        self.cfg['description'] = kw.pop('description')

        super().__init__(*a, **kw)

        self.blog = self.config.module_id[module]

        if not isinstance(self.blog, Blog):
            self.log(logging.WARNING, "Configured with a module other than a blog. Expect errors.")

        self.output = PurePosixPath(output)

    def run(self, gen):
        gen.add_render(self.output / 'atom', self.output / 'atom.xml',
                       Feed(self, self.output / 'atom', Atom1Feed).render)
        gen.add_render(self.output / 'rss', self.output / 'rss.xml',
                       Feed(self, self.output / 'rss', Rss201rev2Feed).render)
