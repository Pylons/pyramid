import sys

from zope.interface import implements

try:
    from chameleon.zpt.template import PageTemplateFile
    PageTemplateFile # prevent pyflakes complaining about a redefinition below
except ImportError: # pragma: no cover
    exc_class, exc, tb = sys.exc_info()
    # Chameleon doesn't work on non-CPython platforms
    class PageTemplateFile(object):
        def __init__(self, *arg, **kw):
            raise ImportError, exc, tb

from pyramid.interfaces import IChameleonTranslate
from pyramid.interfaces import ITemplateRenderer

from pyramid.decorator import reify
from pyramid.path import caller_package
from pyramid import renderers
from pyramid.settings import get_settings
from pyramid.threadlocal import get_current_registry

def renderer_factory(path):
    return renderers.template_renderer_factory(path, ZPTTemplateRenderer)

class ZPTTemplateRenderer(object):
    implements(ITemplateRenderer)
    def __init__(self, path):
        self.path = path

    @reify # avoid looking up reload_templates before manager pushed
    def template(self):
        settings = get_settings()
        debug = False
        auto_reload = False
        if settings:
            # using .get here is a strategy to be kind to old *tests* rather
            # than being kind to any existing production system
            auto_reload = settings.get('reload_templates')
            debug = settings.get('debug_templates')
        reg = get_current_registry()
        translate = None
        if reg is not None:
            translate = reg.queryUtility(IChameleonTranslate)
        return PageTemplateFile(self.path,
                                auto_reload=auto_reload,
                                debug=debug,
                                translate=translate)

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
    """ Return a callable object which can be used to render a
    :term:`Chameleon` ZPT template using the template implied by the
    ``path`` argument.  The ``path`` argument may be a
    package-relative path, an absolute path, or a :term:`resource
    specification`.
    
    .. warning:: This API is deprecated in :mod:`repoze.bfg` 1.3.  Use
       :func:`repoze.bfg.renderers.get_renderer` instead.
    """
    package = caller_package()
    factory = renderers.RendererHelper(path, package=package)
    return factory.get_renderer()

def get_template(path):
    """ Return the underyling object representing a :term:`Chameleon`
    ZPT template using the template implied by the ``path`` argument.
    The ``path`` argument may be a package-relative path, an absolute
    path, or a :term:`resource specification`.

    .. warning:: This API is deprecated in :mod:`repoze.bfg` 1.3.  Use
       the ``implementation()`` method of a template renderer retrieved via
       :func:`repoze.bfg.renderers.get_renderer` instead.
    """
    package = caller_package()
    factory = renderers.RendererHelper(path, package=package)
    return factory.get_renderer().implementation()

def render_template(path, **kw):
    """ Render a :term:`Chameleon` ZPT template using the template
    implied by the ``path`` argument.  The ``path`` argument may be a
    package-relative path, an absolute path, or a :term:`resource
    specification`.  The arguments in ``*kw`` are passed as top-level
    names to the template, and so may be used within the template
    itself.  Returns a string.

    .. warning:: This API is deprecated in :mod:`repoze.bfg` 1.3.  Use
       :func:`repoze.bfg.renderers.render` instead.
    """
    package = caller_package()
    request = kw.pop('request', None)
    renderer = renderers.RendererHelper(path, package=package)
    return renderer.render(kw, None, request=request)

def render_template_to_response(path, **kw):
    """ Render a :term:`Chameleon` ZPT template using the template
    implied by the ``path`` argument.  The ``path`` argument may be a
    package-relative path, an absolute path, or a :term:`resource
    specification`.  The arguments in ``*kw`` are passed as top-level
    names to the template, and so may be used within the template
    itself.  Returns a :term:`Response` object with the body as the
    template result.

    .. warning:: This API is deprecated in :mod:`repoze.bfg` 1.3.  Use
       :func:`repoze.bfg.renderers.render_to_response` instead.
    """
    package = caller_package()
    request = kw.pop('request', None)
    renderer = renderers.RendererHelper(path, package=package)
    return renderer.render_to_response(kw, None, request=request)
