from markdown import Markdown
from markdown.extensions.meta import MetaExtension, MetaPreprocessor
from markdown.extensions.tables import TableExtension
from markdown.extensions.toc import TocExtension
from markdown.extensions.wikilinks import WikiLinkExtension

from jinja2 import Markup

from .mdext import CMS7Extension

import logging
logger = logging.getLogger(__name__)

def load_source(path):
    return MarkdownSource(path)

class Namespace:
    pass

class MarkdownSource:
    def __init__(self, source):
        self.source = source
        self.text = ''
        with self.open_source() as f:
            try:
                self.text = f.read()
            except UnicodeDecodeError:
                logger.error('Invalid unicode in %s', self.source, exc_info=True)
            except:
                logger.error('Error loading %s', self.source, exc_info=True)

        self.meta = self.read_metadata()

    def read_metadata(self):
        ns = Namespace()
        mp = MetaPreprocessor(ns)
        mp.run(self.text.split('\n'))
        return ns.Meta

    def render(self, gs, *, baselevel=2, hyphenate=True, paragraphs=None):
        md = Markdown(extensions=[
                MetaExtension(),
                TableExtension(),
                WikiLinkExtension(),
                CMS7Extension(gs, baselevel=baselevel, hyphenate=hyphenate, paragraphs=paragraphs),
                TocExtension()
            ],
            output_format='html5')
        return Markup(md.convert(self.text))

    def open_source(self):
        return self.source.open('r')
