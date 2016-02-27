from urllib.parse import urlparse, urlunparse

from markdown.extensions import Extension
from markdown.treeprocessors import Treeprocessor
from markdown.util import STX

from .error import CMS7Error

import logging
logger = logging.getLogger(__name__)


class CMS7Extension(Extension):
    def __init__(self, gs):
        self.gs = gs
        super().__init__()

    def extendMarkdown(self, md, md_globals):
        md.treeprocessors['cms7processor'] = CMS7TreeProcessor(self.gs)


class CMS7TreeProcessor(Treeprocessor):
    def __init__(self, gs):
        self.gs = gs
        super().__init__()

    def run(self, root):
        for el in root.findall('.//a[@href]'):
            self.fix_link(el, 'href')
        for el in root.findall('.//*[@src]'):
            self.fix_link(el, 'src')

    def fix_link(self, element, attribute):
        at = element.attrib[attribute]
        if STX in at:
            return
        url = urlparse(at)
        if url.scheme or url.netloc or url.params or url.path.startswith('/'):
            return
        link = self.gs.gen.build_url(self.gs.targetpath, url.path)
        if link is None:
            raise CMS7Error("can't resolve relative URL: {}".format(at))
        at = urlunparse(('', '', str(link), url.params, url.query, url.fragment))
        element.attrib[attribute] = at
