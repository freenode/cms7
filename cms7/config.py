from pathlib2 import Path, PurePosixPath

from .error import CMS7Error
from .resources import Resource

from .modules.blog import Blog
from .modules.faq import Faq
from .modules.null import Null
from .modules.pages import Pages
from .modules.feed import FeedModule

import logging
import yaml

logger = logging.getLogger(__name__)

def load(path, *extra):
    return Config.load_from_file(Path(path), Path(path).parent, map(Path, extra))


_MODULES = {
    'blog': Blog,
    'faq': Faq,
    'null': Null,
    'pages': Pages,
    'feed': FeedModule,
}


class IncludeLoader(yaml.Loader):
    def __init__(self, stream, name):
        self.__name = Path(name).parent
        super().__init__(stream)

    @classmethod
    def load(cls, path):
        with path.open('r') as f:
            loader = IncludeLoader(f, path)
            try:
                return loader.get_single_data()
            finally:
                loader.dispose()

    def include(self, node):
        path = self.__name / self.construct_scalar(node)
        return self.load(path)

IncludeLoader.add_constructor('!include', IncludeLoader.include)


class Config:
    @classmethod
    def load_from_file(cls, f, dir_, extra=()):
        self = cls()
        data = IncludeLoader.load(f)

        for p in extra:
            data.update(IncludeLoader.load(p))

        try:
            self.name     = data['name']
            self.theme    = dir_ / data.get('theme', 'theme')
            self.output   = Path(data.get('output', 'out'))

            self.content_root = dir_ / data.get('content-root', '.')

            self.ignore   = data.get('ignore', [])

            self.output.mkdir(exist_ok=True)
            logger.info('Outputting to %s', self.output.resolve())

            self.htmlless = data.get('pretty-html', False)

            self.absolute_url = data.get('absolute-url')
            if self.absolute_url is None:
                logger.warning("absolute-url is not set, some modules won't work.")

            if 'compiled-theme' in data:
                self.compiled_theme = dir_ / data['compiled-theme']
            else:
                self.compiled_theme = None

            self.resources = []
            for r in data.get('resources', []):
                try:
                    command = r['command']
                    source = Path(r['source'])
                    output = Path(r['output'])
                    suffix = r.get('ext', None)
                    recursive = r.get('recursive', False)
                    pattern = r.get('pattern', '*')
                except KeyError as e:
                    raise CMS7Error('resource missing required key {}'.format(e.args[0])) from e
                self.resources.append(Resource(self, command, dir_, source, output, suffix, recursive, pattern))

            self.module_id = {}

            self._modules = []
            for m in data['modules']:
                name = m.pop('name')
                _id = None
                if 'id' in m:
                    _id = m.pop('id')
                if name not in _MODULES:
                    raise CMS7Error('unknown module: {!r}'.format(name))
                logger.info('Loading module: %s', name)
                module = _MODULES[name](self, self.content_root, **m)
                if _id is not None:
                    self.module_id[_id] = module
                self._modules.append(module)

        except KeyError as e:
            raise CMS7Error('config missing required key {}'.format(e.args[0])) from e

        self._data = data

        return self

    def modules(self):
        yield from self._modules

    def __getitem__(self, k):
        return self._data[k]
