from dateutil import parser
from datetime import timezone

from . import ProcessorModule
from ..source import load_source
from ..util import meta_get_one


class Article:
    index = None

    def __init__(self, blog, name, source):
        self.blog = blog
        self.name = name
        self.author = meta_get_one(source, 'author')
        self.datetime = parser.parse(meta_get_one(source, 'date'))
        if self.datetime.tzinfo is None:
            self.datetime = self.datetime.replace(tzinfo=timezone.utc)
        self.title = meta_get_one(source, 'title')
        self.slug = meta_get_one(source, 'slug', name.name)
        self.source = source

    def render(self, gs):
        this = ArticleWrapper(gs, self)
        return gs.render_template(self.blog.template, article=this)


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
            name = self.path_to_name(p)
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

    @property
    def url(self):
        return self.gs.url_for(self.name)

    @property
    def newer(self):
        try:
            return ArticleWrapper(self.gs,
                    self.blog.articles[self.index + 1])
        except IndexError:
            return None

    @property
    def older(self):
        if self.index == 0:
            return None
        try:
            return ArticleWrapper(self.gs,
                    self.blog.articles[self.index - 1])
        except IndexError:
            return None

    def render(self):
        return self.source.render(self.gs)

    def __getattr__(self, k):
        return getattr(self.article, k)
