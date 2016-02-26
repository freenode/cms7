from pathlib2 import Path, PurePosixPath

from .resources import Resource

from .modules.blog import Blog
from .modules.faq import Faq
from .modules.null import Null
from .modules.pages import Pages

import logging
import yaml

logger = logging.getLogger(__name__)

def load(path):
    with open(path, 'r') as f:
        c = Config.load_from_file(f, Path(path).parent)
        return c

_MODULES = {
    'blog': Blog,
    'faq': Faq,
    'null': Null,
    'pages': Pages,
}

class Config:
    @classmethod
    def load_from_file(cls, f, dir_):
        self = cls()
        data = yaml.load(f)

        self.name     = data['name']
        self.theme    = dir_ / data.get('theme', 'theme')
        self.basedir  = PurePosixPath(data.get('basedir', '/'))
        self.output   = Path(data.get('output', 'out'))

        self.content_root = dir_ / data.get('content-root', '.')

        self.output.mkdir(exist_ok=True)
        logger.info('Outputting to %s', self.output.resolve())

        if 'compiled-theme' in data:
            self.compiled_theme = dir_ / data['compiled-theme']
        else:
            self.compiled_theme = None

        self.resources = []
        for r in data.get('resources', []):
            command = r['command']
            source = Path(r['source'])
            output = Path(r['output'])
            suffix = r.get('ext', None)
            recursive = r.get('recursive', False)
            pattern = r.get('pattern', '*')
            self.resources.append(Resource(command, source, output, suffix, recursive, pattern))

        self.module_id = {}

        self._modules = []
        for m in data['modules']:
            name = m.pop('name')
            _id = None
            if 'id' in m:
                _id = m.pop('id')
            logger.info('Loading module: %s', name)
            module = _MODULES[name](self, self.content_root, **m)
            if _id is not None:
                self.module_id[_id] = module
            self._modules.append(module)

        self._data = data

        return self

    def modules(self):
        yield from self._modules

    def __getitem__(self, k):
        return self._data[k]
