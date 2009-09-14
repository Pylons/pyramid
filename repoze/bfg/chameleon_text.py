from webob import Response

from zope.component import queryUtility

from repoze.bfg.interfaces import IResponseFactory

from repoze.bfg.templating import renderer_from_cache
from repoze.bfg.templating import TextTemplateRenderer
from repoze.bfg.templating import _auto_reload

def get_renderer(path):
    """ Return a callable ``ITemplateRenderer`` object representing a
    ``chameleon`` text template at the package-relative path (may also
    be absolute)."""
    auto_reload = _auto_reload()
    renderer = renderer_from_cache(path, TextTemplateRenderer,
                                   auto_reload=auto_reload)
    return renderer

def get_template(path):
    """ Return a ``chameleon`` text template at the package-relative
    path (may also be absolute)."""
    auto_reload = _auto_reload()
    renderer = renderer_from_cache(path, TextTemplateRenderer,
                                   auto_reload=auto_reload)
    return renderer.implementation()

def render_template(path, **kw):
    """ Render a ``chameleon`` text template at the package-relative
    path (may also be absolute) using the kwargs in ``*kw`` as
    top-level names and return a string."""
    auto_reload = _auto_reload()
    renderer = renderer_from_cache(path, TextTemplateRenderer,
                                   auto_reload=auto_reload)
    return renderer(**kw)

def render_template_to_response(path, **kw):
    """ Render a ``chameleon`` text template at the package-relative
    path (may also be absolute) using the kwargs in ``*kw`` as
    top-level names and return a Response object with the body as the
    template result."""
    auto_reload = _auto_reload()
    renderer = renderer_from_cache(path, TextTemplateRenderer,
                                  auto_reload=auto_reload)
    result = renderer(**kw)
    response_factory = queryUtility(IResponseFactory, default=Response)
    return response_factory(result)
