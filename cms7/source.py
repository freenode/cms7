from markdown import Markdown
from markdown.extensions.meta import MetaExtension, MetaPreprocessor
from markdown.extensions.wikilinks import WikiLinkExtension

from markupsafe import Markup

def load_source(path):
    return MarkdownSource(path)

class Namespace:
    pass

class MarkdownSource:
    def __init__(self, source):
        self.source = source
        with self.open_source() as f:
            self.text = f.read()
        self.meta = self.read_metadata()

    def read_metadata(self):
        ns = Namespace()
        mp = MetaPreprocessor(ns)
        mp.run(self.text.split('\n'))
        return ns.Meta

    def render(self, gen):
        md = Markdown(extensions=[
            MetaExtension(), WikiLinkExtension()],
            output_format='html5')
        return Markup(md.convert(self.text))

    def open_source(self):
        return self.source.open('r')
