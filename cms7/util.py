"""
General utilities
"""

import re

from urllib.parse import urlparse

from markdown.util import ETX, STX

from .error import CMS7Error
from .hyphenate import hyphenate_word


_NOTHING = object()

def meta_get_one(md, key, default=_NOTHING):
    from .source import MarkdownSource
    source = None
    if isinstance(md, MarkdownSource):
        source = md
        md = md.meta
    if key in md:
        return md[key][0]
    if default is not _NOTHING:
        return default
    if source:
        raise CMS7Error('{!s} missing required metadata key: {!r}'.format(source.source, key))
    else:
        raise KeyError(key)


def is_relative_url(url):
    url = urlparse(url)
    if url.scheme or url.netloc or url.path.startswith('/'):
        return False
    if url.path == '':
        return False
    return True


WORD_RE = re.compile(r"[A-Za-z0-9'-]+")

def _hyphenate(text):
    le = 0
    quoted = False
    for match in WORD_RE.finditer(text):
        plain = text[le:match.start()]
        le = match.end()
        yield plain

        """
        python-markdown uses STX...ETX pairs to demarcate magical processing
        tokens. we avoid messing those up here by keeping track of which of
        the two special characters we last saw.
        we never have to deal with them inside the match, since WORD_RE can't
        match them.
        """
        stx, etx = plain.rfind(STX), plain.rfind(ETX)
        if stx > etx:
            quoted = True
        elif etx > -1:
            quoted = False

        if not quoted:
            yield '\u00ad'.join(hyphenate_word(match.group()))
        else:
            yield match.group()
    yield text[le:]

def hyphenate(text):
    return ''.join(_hyphenate(text))
