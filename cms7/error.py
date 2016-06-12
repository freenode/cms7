import logging
import sys


class CMS7Error(Exception):
    def __init__(self, message, filename=None):
        self.message = message
        self.filename = filename


def report_error(exc):
    if report_error.quiet or not exc:
        return
    if isinstance(exc, CMS7Error):
        exc = exc.__cause__ or exc.__context__ or exc
    tb = exc.__traceback__
    while tb.tb_next:
        tb = tb.tb_next
    filename = exc.filename or tb.tb_frame.f_code.co_filename
    if not exc.filename:
        lineno = tb.tb_lineno
    else:
        lineno = 0
    desc = (filename, lineno, exc.__class__.__name__, exc.message)
    if desc in report_error.errors:
        return
    report_error.errors.add(desc)
    print('{}:{}: {}: {}'.format(*desc), file=sys.stderr)

report_error.errors = set()
report_error.quiet = True
