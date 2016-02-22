from dateutil import parser

from .base_module import ProcessorModule
from .source import load_source
from .util import meta_get_one


class Article:
    index = None

    def __init__(self, blog, name, source):
        self.blog = blog
        self.name = name
        self.datetime = parser.parse(meta_get_one(source.meta, 'date'))
        self.title = meta_get_one(source.meta, 'title')
        self.slug = meta_get_one(source.meta, 'slug', name)
        self.source = source

    def render(self, gs):
        html = self.source.render(gs)
        return gs.render_template(self.blog.template, title=self.title, content=html)


class Blog(ProcessorModule):
    def __init__(self, *a, template='article.html', **kw):
        super().__init__(*a, **kw)

        self.articles = []
        self.template = template

    def render(self, config, env, source, html):
        tn = source.meta.get('template', ['blog.html'])[0]
        template = env.get_template(tn)
        return template.render(content=html)

    def prepare(self):
        for p in self.sources:
            name = p.relative_to(self.source).with_suffix('')
            source = load_source(p)
            self.articles.append(Article(self, name, source))
        self.articles.sort()
        for n, a in enumerate(self.articles):
            a.index = n

    def run(self, gen):
        for a in self.articles:
            gen.add_render(a.name, self.root / a.slug, a.render)
