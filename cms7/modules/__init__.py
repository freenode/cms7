import logging

from pathlib2 import PurePosixPath

class Module:
    def __init__(self, cfg, dir_):
        self._dir = dir_
        self.config = cfg
        self._logger = logging.getLogger(self.__class__.__module__)

    def is_ignored(self, p):
        return any(p.match(x) for x in self.config.ignore)

    def path_to_name(self, p):
        return p.relative_to(self._dir).with_suffix('')

    def log(self, lvl, msg, *a, **kw):
        self._logger.log(lvl, msg, *a, **kw)

    def prepare(self):
        pass

    def run(self, gen):
        raise NotImplementedError


class ProcessorModule(Module):
    def __init__(self, *a, source, root, **kw):
        super().__init__(*a, **kw)

        self.source = self._dir / source
        self.root = PurePosixPath(root)

        self.sources = [p for p in self.source.iterdir() if not self.is_ignored(p)]

        self.log(logging.INFO, 'Found %d sources in %s', len(self.sources), self.source.resolve())
