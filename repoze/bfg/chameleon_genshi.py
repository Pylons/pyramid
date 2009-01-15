from webob import Response

from zope.component import queryUtility

from zope.interface import implements
from zope.interface import classProvides
from zope.deprecation import deprecated

from repoze.bfg.interfaces import IResponseFactory
from repoze.bfg.interfaces import ISettings
from repoze.bfg.interfaces import ITemplateRenderer
from repoze.bfg.interfaces import ITemplateRendererFactory

from repoze.bfg.templating import renderer_from_cache

from chameleon.genshi.template import GenshiTemplateFile

class GenshiTemplateRenderer(object):
    classProvides(ITemplateRendererFactory)
    implements(ITemplateRenderer)

    def __init__(self, path, auto_reload=False):
        self.template = GenshiTemplateFile(path, auto_reload=auto_reload)

    def implementation(self):
        return self.template

    def __call__(self, **kw):
        return self.template(**kw)

GenshiTemplateFactory = GenshiTemplateRenderer
deprecated('GenshiTemplateFactory',
           ('repoze.bfg.chameleon_genshi.GenshiTemplateFactory should now be '
            'imported as repoze.bfg.chameleon_genshi.GenshiTemplateRenderer'))

def _auto_reload():
    settings = queryUtility(ISettings)
    auto_reload = settings and settings.reload_templates
    return auto_reload

def get_template(path):
    """ Return a ``chameleon.genshi`` template object at the
    package-relative path (may also be absolute)"""
    auto_reload = _auto_reload()
    renderer = renderer_from_cache(path, GenshiTemplateRenderer,
                                   auto_reload=auto_reload)
    return renderer.implementation()

def get_renderer(path):
    """ Return a ``chameleon.genshi`` template renderer at the
    package-relative path (may also be absolute)"""
    auto_reload = _auto_reload()
    renderer = renderer_from_cache(path, GenshiTemplateRenderer,
                                   auto_reload=auto_reload)
    return renderer

def render_template(path, **kw):
    """ Render a ``chameleon.genshi`` template at the package-relative
    path (may also be absolute) using the kwargs in ``*kw`` as
    top-level names and return a string."""
    auto_reload = _auto_reload()
    renderer = renderer_from_cache(path, GenshiTemplateRenderer,
                                   auto_reload=auto_reload)
    return renderer(**kw)

def render_template_to_response(path, **kw):
    """ Render a ``chameleon.genshi`` template at the package-relative
    path (may also be absolute) using the kwargs in ``*kw`` as
    top-level names and return a Response object."""
    auto_reload = _auto_reload()
    renderer = renderer_from_cache(path, GenshiTemplateRenderer,
                                   auto_reload=auto_reload)
    result = renderer(**kw)
    response_factory = queryUtility(IResponseFactory, default=Response)
    return response_factory(result)
