from pathlib import Path, PurePosixPath

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
    def load_from_file(cls, f, d):
        self = cls()
        data = yaml.load(f)

        self.name     = data['name']
        self.theme    = d / data.get('theme', 'theme')
        self.basedir  = PurePosixPath(data.get('basedir', '/'))
        self.output   = Path(data.get('output', 'out'))

        self.output.mkdir(exist_ok=True)
        logger.info('Outputting to %s', self.output.resolve())

        if 'compiled-theme' in data:
            self.compiled_theme = d / data['compiled-theme']
        else:
            self.compiled_theme = None

        self.module_id = {}

        self._modules = []
        for m in data['modules']:
            name = m.pop('name')
            _id = None
            if 'id' in m:
                _id = m.pop('id')
            logger.info('Loading module: %s', name)
            module = _MODULES[name](self, d, **m)
            if _id is not None:
                self.module_id[_id] = module
            self._modules.append(module)

        return self

    def modules(self):
        yield from self._modules
