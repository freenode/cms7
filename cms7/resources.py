import logging
import subprocess

from .error import CMS7Error

logger = logging.getLogger(__name__)

class Resource:
    def __init__(self, config, command, root, source, output, suffix=None, recursive=False, pattern='*'):
        self.config = config
        self.command = command
        self.root = root
        self.source = source
        self.output = output
        self.suffix = suffix
        self.recursive = recursive
        self.pattern = pattern

        self.map_ = {}
        self.prepare()

    def prepare(self):
        top = self.root / self.source
        l = list(top.iterdir())
        while len(l) > 0:
            f = l.pop(0)
            if f.is_dir():
                if self.recursive:
                    l.extend(f.iterdir())
                continue
            if not f.match(self.pattern):
                continue
            dest = self.root / self.output / f.relative_to(top)
            if self.suffix is not None:
                dest = dest.with_suffix(self.suffix)
            self.map_[str(f.relative_to(self.root))] = (f, dest.relative_to(self.root))

    def run(self):
        for f, dest in self.map_.values():
            dest.parent.mkdir(parents=True, exist_ok=True)
            try:
                if dest.stat().st_mtime > f.stat().st_mtime:
                    logger.info('skip %s', dest)
                    continue
            except FileNotFoundError:
                pass

            with f.open('rb') as in_, dest.open('wb') as out:
                logger.info('%s <%s >%s', ' '.join(self.command), f, dest)
                r = subprocess.call(self.command, stdin=in_, stdout=out)
                if r != 0:
                    raise CMS7Error('build step ({}) failed: {}'.format(' '.join(self.command), r))

    def lookup_target(self, n):
        p = self.map_.get(n, None)
        if p is None:
            return None
        src, dst = p
        return dst.relative_to(self.config.output)
