import logging

from clize import run

from . import config as _config
from .generator import Generator


def main_(*, config: 'c' = 'config.yml'):
    """
    Run cms7.

    config: Path to site configuration
    """
    cfg = _config.load(config)
    gen = Generator(cfg)
    for m in cfg.modules():
        m.prepare()
    for m in cfg.modules():
        m.run(gen)
    gen.run()


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
    logging.basicConfig(level=logging.INFO)
    run(main_, alt=[compile_theme])
