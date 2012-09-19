from zope.interface import implementer

from chameleon.zpt.template import PageTextTemplateFile

from pyramid.interfaces import ITemplateRenderer

from pyramid.decorator import reify
from pyramid import renderers

def renderer_factory(info):
    return renderers.template_renderer_factory(info, TextTemplateRenderer)

@implementer(ITemplateRenderer)
class TextTemplateRenderer(object):
    def __init__(self, path, lookup, macro=None):
        self.path = path
        self.lookup = lookup
        # text template renderers have no macros, so we ignore the
        # macro arg

    @reify # avoid looking up reload_templates before manager pushed
    def template(self):
        return PageTextTemplateFile(self.path,
                                    auto_reload=self.lookup.auto_reload,
                                    debug=self.lookup.debug,
                                    translate=self.lookup.translate)

    def implementation(self):
        return self.template
    
    def __call__(self, value, system):
        try:
            system.update(value)
        except (TypeError, ValueError):
            raise ValueError('renderer was passed non-dictionary as value')
        result = self.template(**system)
        return result

