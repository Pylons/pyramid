from webob import Response

from zope.interface import implements

from chameleon.core.template import TemplateFile
from chameleon.zpt.language import Parser

from repoze.bfg.interfaces import IResponseFactory
from repoze.bfg.interfaces import ITemplateRenderer

from repoze.bfg.renderers import template_renderer_factory
from repoze.bfg.settings import get_settings
from repoze.bfg.threadlocal import get_current_registry

class TextTemplateFile(TemplateFile):
    default_parser = Parser()
    
    def __init__(self, filename, parser=None, format='text', doctype=None,
                 **kwargs):
        if parser is None:
            parser = self.default_parser
        super(TextTemplateFile, self).__init__(filename, parser, format,
                                               doctype, **kwargs)

def renderer_factory(path):
    return template_renderer_factory(path, TextTemplateRenderer)

class TextTemplateRenderer(object):
    implements(ITemplateRenderer)
    def __init__(self, path):
        settings = get_settings()
        auto_reload = settings and settings['reload_templates']
        self.template = TextTemplateFile(path, auto_reload=auto_reload)

    def implementation(self):
        return self.template
    
    def __call__(self, value, system):
        try:
            system.update(value)
        except (TypeError, ValueError):
            raise ValueError('renderer was passed non-dictionary as value')
        result = self.template(**system)
        return result

def get_renderer(path):
    """ Return a callable ``ITemplateRenderer`` object representing a
    ``Chameleon`` text template at the package-relative path (may also
    be absolute)."""
    return renderer_factory(path)

def get_template(path):
    """ Return a ``Chameleon`` text template at the package-relative
    path (may also be absolute)."""
    renderer = renderer_factory(path)
    return renderer.implementation()

def render_template(path, **kw):
    """ Render a ``chameleon`` text template at the package-relative
    path (may also be absolute) using the kwargs in ``*kw`` as
    top-level names and return a string."""
    renderer = renderer_factory(path)
    return renderer(kw, {})

def render_template_to_response(path, **kw):
    """ Render a ``chameleon`` text template at the package-relative
    path (may also be absolute) using the kwargs in ``*kw`` as
    top-level names and return a Response object with the body as the
    template result."""
    renderer = renderer_factory(path)
    result = renderer(kw, {})
    reg = get_current_registry()
    response_factory = reg.queryUtility(IResponseFactory, default=Response)
    return response_factory(result)
