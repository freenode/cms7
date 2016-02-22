"""
General utilities
"""

_NOTHING = object()

def meta_get_one(md, key, default=_NOTHING):
    if key in md:
        return md[key][0]
    if default is not _NOTHING:
        return default
    raise KeyError(key)
