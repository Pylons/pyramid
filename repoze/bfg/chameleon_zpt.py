from webob import Response

from zope.interface import implements

try:
    from chameleon.zpt.template import PageTemplateFile
except ImportError, why: # pragma: no cover
    # Chameleon doesn't work on non-CPython platforms
    class PageTemplateFile(object):
        def __init__(self, *arg, **kw):
            raise ImportError(why[0])

from repoze.bfg.interfaces import IResponseFactory
from repoze.bfg.interfaces import ITemplateRenderer

from repoze.bfg.renderers import template_renderer_factory
from repoze.bfg.settings import get_settings
from repoze.bfg.threadlocal import get_current_registry

def renderer_factory(path):
    return template_renderer_factory(path, ZPTTemplateRenderer)

class ZPTTemplateRenderer(object):
    implements(ITemplateRenderer)
    def __init__(self, path):
        settings = get_settings()
        auto_reload = settings and settings['reload_templates']
        self.template = PageTemplateFile(path, auto_reload=auto_reload)

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
    ``chameleon.zpt`` template at the package-relative path (may also
    be absolute). """
    return renderer_factory(path)

def get_template(path):
    """ Return a ``chameleon.zpt`` template at the package-relative
    path (may also be absolute).  """
    renderer = renderer_factory(path)
    return renderer.implementation()

def render_template(path, **kw):
    """ Render a ``chameleon.zpt`` template at the package-relative
    path (may also be absolute) using the kwargs in ``*kw`` as
    top-level names and return a string."""
    renderer = renderer_factory(path)
    return renderer(kw, {})

def render_template_to_response(path, **kw):
    """ Render a ``chameleon.zpt`` template at the package-relative
    path (may also be absolute) using the kwargs in ``*kw`` as
    top-level names and return a Response object with the body as the
    template result. """
    renderer = renderer_factory(path)
    result = renderer(kw, {})
    reg = get_current_registry()
    response_factory = reg.queryUtility(IResponseFactory, default=Response)
    return response_factory(result)

