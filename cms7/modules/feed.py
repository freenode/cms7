import logging

import requests
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
        gs = gs.with_absolute()

        blog = self.parent.blog.get_api(gs)
        feed = self.ftype(self.parent.title, gs.url_for(self.name, absolute=True), self.parent.description)

        for a in reversed(blog.articles[-15:]):

            summary = str(a.source.render(gs, paragraphs=3, hyphenate=False))
            content = str(a.source.render(gs, hyphenate=False))

            enclosure = meta_get_one(a.source, 'enclosure', None)
            if enclosure:
                enclosure = self.parent.enclosure_info(enclosure)
            feed.add_item(a.title, gs.url_for(a.name, absolute=True),
                          pubdate=a.datetime,
                          description=summary,
                          content=content,
                          author_name=a.author,
                          enclosure=enclosure)

        return feed.writeString('utf-8') + '\n'


class FeedModule(Module):
    def __init__(self, *a, title, description, module, output, **kw):
        super().__init__(*a, **kw)

        self._info = {}

        self.title = title
        self.description = description

        self.blog = self.config.module_id[module]

        if not isinstance(self.blog, Blog):
            self.log(logging.WARNING, "Configured with a target other than a blog. Expect errors.")

        self.output = PurePosixPath(output)

    def enclosure_info(self, url):
        if url not in self._info:
            response = requests.head(url)
            if response.status_code != 200 or 'content-length' not in response.headers:
                response = requests.get(url, stream=True)
            if 'content-length' in response.headers:
                length = response.headers['content-length']
            else:
                length = '0'
                self.log(logging.WARNING, "Server for %r doesn't report content length!", url)
            self._info[url] = Enclosure(url, length, response.headers['content-type'])
        return self._info[url]

    def run(self, gen):
        gen.add_render(self.output / 'atom', self.output / 'atom.xml',
                       Feed(self, self.output / 'atom', Atom1Feed).render)
        gen.add_render(self.output / 'rss', self.output / 'rss.xml',
                       Feed(self, self.output / 'rss', Rss201rev2Feed).render)
