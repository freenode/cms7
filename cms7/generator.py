from pathlib import PurePosixPath

import logging

from jinja2 import Environment, ChoiceLoader, FileSystemLoader, ModuleLoader, StrictUndefined

logger = logging.getLogger(__name__)

class Generator:
    def __init__(self, config):
        self.config = config
        self.pages = {}

        loaders = [FileSystemLoader(str(self.config.theme))]
        if self.config.compiled_theme is not None:
            loaders.append(ModuleLoader(str(self.config.compiled_theme)))
        self.env = Environment(loader=ChoiceLoader(loaders), undefined=StrictUndefined)

    def add_render(self, link, target, generator):
        self.pages[link] = (target, generator)

    def build_url(self, location, name):
        target = self.pages[name][0]
        n = 0
        for a, b in zip(location.parts, target.parts):
            if a != b:
                break
            n += 1
        newpath = ['..'] * (len(location.parts) - n) + target.parts[n:]
        return PurePosixPath(*newpath)

    def open_target(self, path):
        p = self.config.output / path
        p.parent.mkdir(parents=True, exist_ok=True)
        return p.open('w')

    def run(self):
        for link, v in sorted(self.pages.items(), key=lambda x: str(x[0])):
            target, generator = v
            tf = target.with_suffix('.html')
            logger.info('Rendering %s -> %s', link, tf)
            data = generator(GeneratorState(self, target))
            with self.open_target(target.with_suffix('.html')) as f:
                f.write(data)


class GeneratorState:
    def __init__(self, gen, targetpath):
        self.gen = gen
        self.targetpath = targetpath

    def render_template(self, template, **kw):
        template = self.gen.env.get_template(template)
        def url_for(name):
            return self.gen.build_url(self.targetpath, name)
        def get_module(name):
            return self.gen.config.module_id[name].get_api(self)
        return template.render(config=self.gen.config,
                               url_for=url_for,
                               get_module=get_module,
                               **kw)
