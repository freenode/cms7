from . import ProcessorModule
from ..source import load_source
from ..util import meta_get_one


class Page:
    def __init__(self, parent, name, source):
        self.source = source
        self.name = name
        self.slug = meta_get_one(source, 'slug', name.name)
        self.title = meta_get_one(source, 'title')
        self.template = meta_get_one(source, 'template', 'page.html')

    def render(self, gs):
        self.content = self.source.render(gs)
        return gs.render_template(self.template, title=self.title, page=self)


class Pages(ProcessorModule):
    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)

        self.pages = {}

    def prepare(self):
        for p in self.sources:
            name = self.path_to_name(p)
            source = load_source(p)
            self.pages[name] = Page(self, name, source)

    def run(self, gen):
        for p in self.pages.values():
            gen.add_render(p.name, self.root / p.slug, p.render)
