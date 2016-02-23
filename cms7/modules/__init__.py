import logging

from pathlib2 import PurePosixPath

class Module:
    def __init__(self, cfg, dir_):
        self._dir = dir_
        self.config = cfg
        self._logger = logging.getLogger(self.__class__.__module__)

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

        self.sources = list(self.source.iterdir())

        self.log(logging.INFO, 'Found %d sources in %s', len(self.sources), self.source.resolve())
