import logging

from jinja2 import Environment, ChoiceLoader, FileSystemLoader, ModuleLoader

logger = logging.getLogger(__name__)

class Generator:
    def __init__(self, config):
        self.config = config
        self.pages = {}

        loaders = [FileSystemLoader(str(self.config.theme))]
        if self.config.compiled_theme is not None:
            loaders.append(ModuleLoader(str(self.config.compiled_theme)))
        self.env = Environment(loader=ChoiceLoader(loaders))

    def add_render(self, link, target, generator):
        self.pages[link] = (target, generator)

    def build_url(self, label, base, end):
        pass

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
        return template.render(**kw)
