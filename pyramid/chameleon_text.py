import sys

from zope.deprecation import deprecated
from zope.interface import implements

try:
    from chameleon.zpt.template import PageTextTemplateFile
    # prevent pyflakes complaining about a redefinition below
    PageTextTemplateFile
except ImportError: # pragma: no cover
    exc_class, exc, tb = sys.exc_info()
    # Chameleon doesn't work on non-CPython platforms
    class PageTextTemplateFile(object):
        def __init__(self, *arg, **kw):
            raise ImportError, exc, tb

from pyramid.interfaces import ITemplateRenderer

from pyramid.decorator import reify
from pyramid import renderers
from pyramid.path import caller_package

def renderer_factory(info):
    return renderers.template_renderer_factory(info, TextTemplateRenderer)

class TextTemplateRenderer(object):
    implements(ITemplateRenderer)
    def __init__(self, path, lookup):
        self.path = path
        self.lookup = lookup

    @reify # avoid looking up reload_templates before manager pushed
    def template(self):
        if sys.platform.startswith('java'): # pragma: no cover
            raise RuntimeError(
                'Chameleon templates are not compatible with Jython')
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

def get_renderer(path):
    """ Return a callable object which can be used to render a
    :term:`Chameleon` text template using the template implied by the
    ``path`` argument.  The ``path`` argument may be a
    package-relative path, an absolute path, or a :term:`asset
    specification`.

    .. warning:: This API is deprecated in :app:`Pyramid` 1.0.  Use
       :func:`pyramid.renderers.get_renderer` instead.
    """
    package = caller_package()
    factory = renderers.RendererHelper(path, package=package)
    return factory.get_renderer()

deprecated(
    'get_renderer',
    '(pyramid.chameleon_text.get_renderer is deprecated '
    'as of Pyramid 1.0; instead use pyramid.renderers.get_renderer)')

def get_template(path):
    """ Return the underyling object representing a :term:`Chameleon`
    text template using the template implied by the ``path`` argument.
    The ``path`` argument may be a package-relative path, an absolute
    path, or a :term:`asset specification`.

    .. warning::

       This API is deprecated in :app:`Pyramid` 1.0.  Use the
       ``implementation()`` method of a template renderer retrieved via
       :func:`pyramid.renderers.get_renderer` instead.
    """
    package = caller_package()
    factory = renderers.RendererHelper(path, package=package)
    return factory.get_renderer().implementation()

deprecated(
    'get_template',
    '(pyramid.chameleon_text.get_template is deprecated '
    'as of Pyramid 1.0; instead use '
    'pyramid.renderers.get_renderer().implementation())')

def render_template(path, **kw):
    """ Render a :term:`Chameleon` text template using the template
    implied by the ``path`` argument.  The ``path`` argument may be a
    package-relative path, an absolute path, or a :term:`asset
    specification`.  The arguments in ``*kw`` are passed as top-level
    names to the template, and so may be used within the template
    itself.  Returns a string.

    .. warning::

       This API is deprecated in :app:`Pyramid` 1.0.  Use
       :func:`pyramid.renderers.render` instead.
    """
    package = caller_package()
    request = kw.pop('request', None)
    renderer = renderers.RendererHelper(path, package=package)
    return renderer.render(kw, None, request=request)

deprecated(
    'render_template',
    '(pyramid.chameleon_text.render_template is deprecated '
    'as of Pyramid 1.0; instead use pyramid.renderers.render)')

def render_template_to_response(path, **kw):
    """ Render a :term:`Chameleon` text template using the template
    implied by the ``path`` argument.  The ``path`` argument may be a
    package-relative path, an absolute path, or a :term:`asset
    specification`.  The arguments in ``*kw`` are passed as top-level
    names to the template, and so may be used within the template
    itself.  Returns a :term:`Response` object with the body as the
    template result.

    .. warning::

       This API is deprecated in :app:`Pyramid` 1.0.  Use
       :func:`pyramid.renderers.render_to_response` instead.
    """
    package = caller_package()
    request = kw.pop('request', None)
    renderer = renderers.RendererHelper(path, package=package)
    return renderer.render_to_response(kw, None, request=request)

deprecated(
    'render_template_to_response',
    '(pyramid.chameleon_text.render_template_to_response is deprecated '
    'as of Pyramid 1.0; instead use pyramid.renderers.render_to_response)')

