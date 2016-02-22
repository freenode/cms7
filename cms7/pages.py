from .base_module import ProcessorModule
from .source import load_source
from .util import meta_get_one


class Page:
    def __init__(self, name, source):
        self.source = source
        self.name = name
        self.slug = meta_get_one(source.meta, 'slug', name)
        self.title = meta_get_one(source.meta, 'title')
        self.template = meta_get_one(source.meta, 'template', 'page.html')

    def render(self, gs):
        html = self.source.render(gs)
        return gs.render_template(self.template, title=self.title, content=html)


class Pages(ProcessorModule):
    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)

        self.pages = {}

    def prepare(self):
        for p in self.sources:
            name = p.relative_to(self.source).with_suffix('')
            source = load_source(p)
            self.pages[name] = Page(name, source)

    def run(self, gen):
        for p in self.pages.values():
            gen.add_render(p.name, self.root / p.slug, p.render)

