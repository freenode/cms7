from urllib.parse import urlparse, urlunparse

from markdown.extensions import Extension
from markdown.treeprocessors import Treeprocessor
from markdown.util import STX

import html5lib
import xml.etree

from .error import CMS7Error
from .util import hyphenate

import logging
logger = logging.getLogger(__name__)


class CMS7Extension(Extension):
    def __init__(self, gs, baselevel=1):
        self.gs = gs
        self.baselevel = baselevel
        super().__init__()

    def extendMarkdown(self, md, md_globals):
        md.treeprocessors['cms7processor'] = CMS7TreeProcessor(md, self.gs, self.baselevel)


class CMS7TreeProcessor(Treeprocessor):
    def __init__(self, md, gs, baselevel):
        self.gs = gs
        self.baselevel = baselevel
        super().__init__(md)

    def process_links(self, root):
        for el in root.findall('.//a[@href]'):
            self.fix_link(el, 'href')
        for el in root.findall('.//{http://www.w3.org/1999/xhtml}a[@href]'):
            self.fix_link(el, 'href')
        for el in root.findall('.//*[@src]'):
            self.fix_link(el, 'src')

    def process_headings(self, root):
        hl = []
        for n in range(1, 7):
            headings = root.findall('.//h{}'.format(n))
            if len(headings) == 0:
                continue
            hl.append(headings)

        for level, headings in enumerate(hl, self.baselevel):
            tag = 'h{}'.format(level)
            for el in headings:
                el.tag = tag

    def process_hyphens(self, root):
        for el in root:
            tag = el.tag
            if tag.startswith('{http://www.w3.org/1999/xhtml}'):
                tag = tag[len('{http://www.w3.org/1999/xhtml}'):]
            if tag in ('p', 'li'):
                self.hyphenate(el)
                continue
            self.process_hyphens(el)

    def run(self, root):
        S = '<body xmlns="http://www.w3.org/1999/xhtml">'
        E = '</body>'

        self.process_links(root)
        self.process_headings(root)
        self.process_hyphens(root)

        for i in range(len(self.markdown.htmlStash.rawHtmlBlocks)):
            html, safe = self.markdown.htmlStash.rawHtmlBlocks[i]
            tree = html5lib.parse(html)
            self.process_links(tree)
            self.process_hyphens(tree)
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

    def hyphenate(self, element):
        tag = element.tag
        if tag.startswith('{http://www.w3.org/1999/xhtml}'):
            tag = tag[len('{http://www.w3.org/1999/xhtml}'):]
        if tag in ('code', 'pre'):
            return
        element.text = hyphenate(element.text) if element.text else None
        for child in element:
            self.hyphenate(child)
            child.tail = hyphenate(child.tail) if child.tail else None
