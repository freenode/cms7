from pathlib import Path, PurePosixPath

from .modules.blog import Blog
from .modules.null import Null
from .modules.pages import Pages

import yaml

def load(path):
    with open(path, 'r') as f:
        c = Config.load_from_file(f, Path(path).parent)
        return c

_MODULES = {
    'blog': Blog,
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
        self.basedir  = PurePosixPath(data.get('basedor', '/'))
        self.output   = Path(data.get('output', 'out'))

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
            module = _MODULES[name](self, d, **m)
            if _id is not None:
                self.module_id[_id] = module
            self._modules.append(module)

        return self

    def modules(self):
        yield from self._modules
