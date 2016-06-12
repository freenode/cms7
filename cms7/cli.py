import logging
import sys

from clize import run, parameters, Parameter

from . import config as _config
from .error import CMS7Error, report_error
from .generator import Generator

logger = logging.getLogger('cms7')


def main_(*,
          config: 'c' = 'config.yml',
          debug: 'd' = False,
          extra: ('e', str, parameters.multi()) = None,
          optimistic = False,
          quiet: 'q' = False,
          vim_is_fucking_retarded: Parameter.UNDOCUMENTED = False):
    """
    Run cms7.

    config: Path to project configuration

    debug: Print obnoxious debugging output

    extra: Path to additional configuration (e.g. site local overrides). Can
           be specified multiple times. Later configurations override.

    optimistic: Try to continue processing after rendering errors

    quiet: Only ever print warnings
    """

    rl = logging.getLogger()
    h = logging.StreamHandler()
    try:
        if not sys.stdin.isatty():
            raise Exception
        import colorlog
        h.setFormatter(colorlog.ColoredFormatter(
            "%(log_color)s%(levelname)-8s%(reset)s %(message_log_color)s%(name)s:%(message)s",
            secondary_log_colors={
                'message': {
                    'WARNING':  'yellow',
                    'ERROR':    'red',
                    'CRITICAL': 'red',
                }
            }))
    except:
        h.setFormatter(logging.Formatter(
            "%(levelname)-8s %(name)s:%(message)s"))
    rl.addHandler(h)

    if vim_is_fucking_retarded:
        report_error.quiet = False

    if debug:
        rl.setLevel(logging.DEBUG)
    elif quiet:
        if vim_is_fucking_retarded:
            rl.setLevel(logging.CRITICAL + 1)
        else:
            rl.setLevel(logging.WARNING)
    else:
        rl.setLevel(logging.INFO)

    try:
        cfg = _config.load(config, *extra)
        if optimistic:
            cfg.optimistic = True
        gen = Generator(cfg)
        for m in cfg.modules():
            m.prepare()
        for m in cfg.modules():
            m.run(gen)
        gen.run()
        for r in cfg.resources:
            r.run()
    except CMS7Error as e:
        logger.critical('%s', e.message, exc_info=debug)
        if not debug:
            logger.warning('exiting for exception. use --debug to get a traceback')
        sys.exit(1)
    except Exception:
        logger.critical('unexpected exception', exc_info=True)
        sys.exit(1)


def compile_theme(theme, target, *, zip_=False):
    """
    Compile a theme (i.e. directory of Jinja2 templates)

    theme: Path to directory with templates in

    target: Directory in which to store compiled templates

    zip_: Target is a zip file, rather than a directory
    """
    from jinja2 import Environment, FileSystemLoader
    env = Environment(loader=FileSystemLoader(theme))
    env.compile_templates(target, zip='deflated' if zip_ else None)


def main():
    run(main_, alt=[compile_theme])
