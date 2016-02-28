"""
General utilities
"""

from .error import CMS7Error
from .source import MarkdownSource

_NOTHING = object()

def meta_get_one(md, key, default=_NOTHING):
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
