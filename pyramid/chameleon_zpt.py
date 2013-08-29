from zope.interface import implementer

from pyramid.interfaces import ITemplateRenderer
from pyramid.decorator import reify
from pyramid import renderers

from chameleon.zpt.template import PageTemplateFile

def renderer_factory(info):
    return renderers.template_renderer_factory(info, ZPTTemplateRenderer)

class PyramidPageTemplateFile(PageTemplateFile):
    def cook(self, body):
        PageTemplateFile.cook(self, body)
        if self.macro:
            # render only the portion of the template included in a
            # define-macro named the value of self.macro
            macro_renderer = self.macros[self.macro].include
            self._render = macro_renderer

@implementer(ITemplateRenderer)
class ZPTTemplateRenderer(object):
    def __init__(self, path, lookup, macro=None):
        self.path = path
        self.lookup = lookup
        self.macro = macro

    @reify # avoid looking up reload_templates before manager pushed
    def template(self):
        tf = PyramidPageTemplateFile(
            self.path,
            auto_reload=self.lookup.auto_reload,
            debug=self.lookup.debug,
            translate=self.lookup.translate,
            macro=self.macro,
            )
        return tf

    def implementation(self):
        return self.template
    
    def __call__(self, value, system):
        try:
            system.update(value)
        except (TypeError, ValueError):
            raise ValueError('renderer was passed non-dictionary as value')
        result = self.template(**system)
        return result

