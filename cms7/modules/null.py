from pathlib2 import PurePosixPath

from . import Module

class Null(Module):
    def __init__(self, *a, map, **kw):
        super().__init__(*a, **kw)

        self.mapping = map

    def run(self, gen):
        for link, template in self.mapping.items():
            link = PurePosixPath(link)
            def render(gs, template=template):
                return gs.render_template(template)
            gen.add_render(link, link, render)
