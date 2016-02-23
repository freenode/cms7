from dateutil import parser

from . import ProcessorModule
from ..source import load_source
from ..util import meta_get_one


class Article:
    index = None

    def __init__(self, blog, name, source):
        self.blog = blog
        self.name = name
        self.datetime = parser.parse(meta_get_one(source.meta, 'date'))
        self.title = meta_get_one(source.meta, 'title')
        self.slug = meta_get_one(source.meta, 'slug', name.relative_to(self.blog.source))
        self.source = source

    def render(self, gs):
        self.content = self.source.render(gs)
        return gs.render_template(self.blog.template, title=self.title, article=self)


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
            name = p.with_suffix('')
            source = load_source(p)
            self.articles.append(Article(self, name, source))
        self.articles.sort(key=lambda a: a.datetime)
        for n, a in enumerate(self.articles):
            a.index = n

    def run(self, gen):
        for a in self.articles:
            gen.add_render(a.name, self.root / a.slug, a.render)

    def get_api(self, gs):
        return BlogAPI(self, gs)


class BlogAPI:
    def __init__(self, blog, gs):
        self.blog = blog
        self.gs = gs
        self.articles = [ArticleWrapper(gs, a) for a in self.blog.articles]


class ArticleWrapper:
    def __init__(self, gs, article):
        self.gs = gs
        self.article = article

    def render(self):
        return self.source.render(self.gs)

    def __getattr__(self, k):
        return getattr(self.article, k)
