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
    def __init__(self, gs, *, baselevel=1, hyphenate=True, paragraphs=None):
        self.gs = gs
        self.baselevel = baselevel
        self.hyphenate = hyphenate
        self.paragraphs = paragraphs
        super().__init__()

    def extendMarkdown(self, md, md_globals):
        md.treeprocessors['cms7processor'] = CMS7TreeProcessor(md, self.gs, self.baselevel, self.hyphenate, self.paragraphs)


class CMS7TreeProcessor(Treeprocessor):
    def __init__(self, md, gs, baselevel, hyphenate, paragraphs):
        self.gs = gs
        self.baselevel = baselevel
        self.hyphens = hyphenate
        self.paragraphs = paragraphs
        super().__init__(md)

    def process_links(self, root):
        for el in root.findall('.//a[@href]'):
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
            if tag in ('p', 'li'):
                self.hyphenate(el)
                continue
            self.process_hyphens(el)

    def run(self, root):
        S = '<body>'
        E = '</body>'

        self.process_links(root)
        self.process_headings(root)

        if self.hyphens:
            self.process_hyphens(root)

        for i in range(len(self.markdown.htmlStash.rawHtmlBlocks)):
            html, safe = self.markdown.htmlStash.rawHtmlBlocks[i]
            tree = html5lib.parse(html, namespaceHTMLElements=False)
            self.process_links(tree)
            if self.hyphens:
                self.process_hyphens(tree)
            body = tree.find('body')
            html = xml.etree.ElementTree.tostring(body, method='html', encoding='unicode')
            assert html.startswith(S) and html.endswith(E)
            html = html[len(S):-len(E)]
            self.markdown.htmlStash.rawHtmlBlocks[i] = html, safe

        if self.paragraphs is not None:
            children = list(root)
            count = 0
            stop = False
            for child in children:
                count += 1
                if child.tag != 'p':
                    stop = True
                if stop or count > self.paragraphs:
                    root.remove(child)

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
        if tag in ('code', 'pre'):
            return
        element.text = hyphenate(element.text) if element.text else None
        for child in element:
            self.hyphenate(child)
            child.tail = hyphenate(child.tail) if child.tail else None
