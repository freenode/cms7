from urllib.parse import urlparse, urlunparse

from markdown.extensions import Extension
from markdown.treeprocessors import Treeprocessor
from markdown.util import STX

import html5lib
import xml.etree

from .error import CMS7Error

import logging
logger = logging.getLogger(__name__)


class CMS7Extension(Extension):
    def __init__(self, gs):
        self.gs = gs
        super().__init__()

    def extendMarkdown(self, md, md_globals):
        md.treeprocessors['cms7processor'] = CMS7TreeProcessor(md, self.gs)


class CMS7TreeProcessor(Treeprocessor):
    def __init__(self, md, gs):
        self.gs = gs
        super().__init__(md)

    def process(self, root):
        for el in root.findall('.//a[@href]'):
            self.fix_link(el, 'href')
        for el in root.findall('.//{http://www.w3.org/1999/xhtml}a[@href]'):
            self.fix_link(el, 'href')
        for el in root.findall('.//*[@src]'):
            self.fix_link(el, 'src')

    def run(self, root):
        S = '<body xmlns="http://www.w3.org/1999/xhtml">'
        E = '</body>'
        self.process(root)
        for i in range(len(self.markdown.htmlStash.rawHtmlBlocks)):
            html, safe = self.markdown.htmlStash.rawHtmlBlocks[i]
            tree = html5lib.parse(html)
            self.process(tree)
            xml.etree.ElementTree.register_namespace('', 'http://www.w3.org/1999/xhtml')
            body = tree.find('{http://www.w3.org/1999/xhtml}body')
            html = xml.etree.ElementTree.tostring(body, method='html', encoding='unicode')
            assert html.startswith(S) and html.endswith(E)
            html = html[len(S):-len(E)]
            self.markdown.htmlStash.rawHtmlBlocks[i] = html, safe

    def fix_link(self, element, attribute):
        at = element.attrib[attribute]
        if STX in at:
            return
        url = urlparse(at)
        if url.scheme or url.netloc or url.params or url.path.startswith('/'):
            return
        if url.path == '':
            return
        link = self.gs.gen.build_url(self.gs.targetpath, url.path)
        if link is None:
            raise CMS7Error("can't resolve relative URL: {}".format(at))
        at = urlunparse(('', '', str(link), url.params, url.query, url.fragment))
        element.attrib[attribute] = at
