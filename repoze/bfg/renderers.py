import os
import pkg_resources

from webob import Response

from zope.deprecation import deprecated

from repoze.bfg.interfaces import IRendererGlobalsFactory
from repoze.bfg.interfaces import IRendererFactory
from repoze.bfg.interfaces import IResponseFactory
from repoze.bfg.interfaces import ITemplateRenderer

from repoze.bfg.compat import json
from repoze.bfg.path import caller_package
from repoze.bfg.settings import get_settings
from repoze.bfg.threadlocal import get_current_registry
from repoze.bfg.resource import resolve_resource_spec
from repoze.bfg.decorator import reify

# API

def render(renderer_name, value, request=None, package=None):
    """ Using the renderer specified as ``renderer_name`` (a template
    or a static renderer) render the value (or set of values) present
    in ``value``. Return the result of the renderer's ``__call__``
    method (usually a string or Unicode).

    If the renderer name refers to a file on disk (such as when the
    renderer is a template), it's usually best to supply the name as a
    :term:`resource specification`.

    You may supply a relative resource spec as ``renderer_name``.  If
    the ``package`` argument is supplied, a relative renderer name
    will be converted to an absolute resource specification by
    combining the package supplied as ``package`` with the relative
    resource specification supplied as ``renderer_name``.  If you do
    not supply a ``package`` (or ``package`` is ``None``) the package
    name of the *caller* of this function will be used as the package.

    The ``value`` provided will be supplied as the input to the
    renderer.  Usually, for template renderings, this should be a
    dictionary.  For other renderers, this will need to be whatever
    sort of value the renderer expects.

    The 'system' values supplied to the renderer will include a basic
    set of top-level system names, such as ``request``, ``context``,
    and ``renderer_name`.  If :term:`renderer globals` have been
    specified, these will also be used to agument the value.

    Supply a ``request`` parameter in order to provide the renderer
    with the most correct 'system' values (``request`` and ``context``
    in particular).

    .. note:: This API is new in :mod:`repoze.bfg` 1.3.

    """
    try:
        registry = request.registry
    except AttributeError:
        registry = None
    if package is None:
        package = caller_package()
    renderer = RendererHelper(renderer_name, package=package, registry=registry)
    return renderer.render(value, None, request=request)

def render_to_response(renderer_name, value, request=None, package=None):
    """ Using the renderer specified as ``renderer_name`` (a template
    or a static renderer) render the value (or set of values) using
    the result of the renderer's ``__call__`` method (usually a string
    or Unicode) as the response body.

    If the renderer name refers to a file on disk (such as when the
    renderer is a template), it's usually best to supply the name as a
    :term:`resource specification`.

    You may supply a relative resource spec as ``renderer_name``.  If
    the ``package`` argument is supplied, a relative renderer name
    will be converted to an absolute resource specification by
    combining the package supplied as ``package`` with the relative
    resource specification supplied as ``renderer_name``.  If you do
    not supply a ``package`` (or ``package`` is ``None``) the package
    name of the *caller* of this function will be used as the package.

    The ``value`` provided will be supplied as the input to the
    renderer.  Usually, for template renderings, this should be a
    dictionary.  For other renderers, this will need to be whatever
    sort of value the renderer expects.

    The 'system' values supplied to the renderer will include a basic
    set of top-level system names, such as ``request``, ``context``,
    and ``renderer_name`.  If :term:`renderer globals` have been
    specified, these will also be used to agument the value.

    Supply a ``request`` parameter in order to provide the renderer
    with the most correct 'system' values (``request`` and ``context``
    in particular).

    .. note:: This API is new in :mod:`repoze.bfg` 1.3.

    """
    try:
        registry = request.registry
    except AttributeError:
        registry = None
    if package is None:
        package = caller_package()
    renderer = RendererHelper(renderer_name, package=package, registry=registry)
    return renderer.render_to_response(value, None, request=request)

def get_renderer(renderer_name, package=None):
    """ Return the renderer object for the renderer named as
    ``renderer_name``.

    You may supply a relative resource spec as ``renderer_name``.  If
    the ``package`` argument is supplied, a relative renderer name
    will be converted to an absolute resource specification by
    combining the package supplied as ``package`` with the relative
    resource specification supplied as ``renderer_name``.  If you do
    not supply a ``package`` (or ``package`` is ``None``) the package
    name of the *caller* of this function will be used as the package.
    """
    if package is None:
        package = caller_package()
    renderer = RendererHelper(renderer_name, package=package)
    return renderer.get_renderer()


# concrete renderer factory implementations (also API)

def json_renderer_factory(name):
    def _render(value, system):
        request = system.get('request')
        if request is not None:
            if not hasattr(request, 'response_content_type'):
                request.response_content_type = 'application/json'
        return json.dumps(value)
    return _render

def string_renderer_factory(name):
    def _render(value, system):
        if not isinstance(value, basestring):
            value = str(value)
        request = system.get('request')
        if request is not None:
            if not hasattr(request, 'response_content_type'):
                request.response_content_type = 'text/plain'
        return value
    return _render

# utility functions, not API

def template_renderer_factory(spec, impl):
    reg = get_current_registry()
    if os.path.isabs(spec):
        # 'spec' is an absolute filename
        if not os.path.exists(spec):
            raise ValueError('Missing template file: %s' % spec)
        renderer = reg.queryUtility(ITemplateRenderer, name=spec)
        if renderer is None:
            renderer = impl(spec)
            reg.registerUtility(renderer, ITemplateRenderer, name=spec)
    else:
        # spec is a package:relpath resource spec
        renderer = reg.queryUtility(ITemplateRenderer, name=spec)
        if renderer is None:
            try:
                package_name, filename = spec.split(':', 1)
            except ValueError: # pragma: no cover
                # somehow we were passed a relative pathname; this
                # should die
                package_name = caller_package(4).__name__
                filename = spec
            abspath = pkg_resources.resource_filename(package_name, filename)
            if not pkg_resources.resource_exists(package_name, filename):
                raise ValueError(
                    'Missing template resource: %s (%s)' % (spec, abspath))
            renderer = impl(abspath)
            if not _reload_resources():
                # cache the template
                reg.registerUtility(renderer, ITemplateRenderer, name=spec)
        
    return renderer

def _reload_resources():
    settings = get_settings()
    return settings and settings.get('reload_resources')

def renderer_from_name(path, package=None):
    return RendererHelper(path, package=package).get_renderer()

def rendered_response(renderer, result, view, context, request, renderer_name):
    # XXX: deprecated, left here only to not break old code; use
    # render_to_response instead
    if ( hasattr(result, 'app_iter') and hasattr(result, 'headerlist')
         and hasattr(result, 'status') ):
        return result

    system = {'view':view, 'renderer_name':renderer_name,
              'context':context, 'request':request}

    helper = RendererHelper(renderer_name)
    helper.renderer = renderer
    return helper.render_to_response(result, system, request=request)

deprecated('rendered_response',
    "('repoze.bfg.renderers.rendered_response' is not a public API; it is  "
    "officially deprecated as of repoze.bfg 1.3; "
    "use repoze.bfg.renderers.render_to_response instead')",
    )

class RendererHelper(object):
    def __init__(self, renderer_name, registry=None, package=None):
        if registry is None:
            registry = get_current_registry()
        self.registry = registry
        self.package = package
        if renderer_name is None:
            factory = registry.queryUtility(IRendererFactory)
            renderer_type = None
        else:
            if '.' in renderer_name:
                renderer_type = os.path.splitext(renderer_name)[1]
                renderer_name = self.resolve_spec(renderer_name)
            else:
                renderer_type = renderer_name
                renderer_name = renderer_name
            factory = registry.queryUtility(IRendererFactory,
                                            name=renderer_type)
        self.renderer_name = renderer_name
        self.renderer_type = renderer_type
        self.factory = factory

    @reify
    def renderer(self):
        if self.factory is None:
            raise ValueError('No such renderer factory %s' % self.renderer_type)
        return self.factory(self.renderer_name)

    def resolve_spec(self, path_or_spec):
        if path_or_spec is None:
            return path_or_spec

        package, filename = resolve_resource_spec(path_or_spec,
                                                  self.package)
        if package is None:
            return filename # absolute filename
        return '%s:%s' % (package, filename)

    def get_renderer(self):
        return self.renderer

    def render(self, value, system_values, request=None):
        renderer = self.renderer
        if system_values is None:
            system_values = {
                'view':None,
                'renderer_name':self.renderer_name,
                'context':getattr(request, 'context', None),
                'request':request,
                }

        registry = self.registry
        globals_factory = registry.queryUtility(IRendererGlobalsFactory)

        if globals_factory is not None:
            renderer_globals = globals_factory(system_values)
            if renderer_globals:
                system_values.update(renderer_globals)

        result = renderer(value, system_values)
        return result

    def render_to_response(self, value, system_values, request=None):
        result = self.render(value, system_values, request=request)
        return self._make_response(result, request)

    def _make_response(self, result, request):
        registry = self.registry
        response_factory = registry.queryUtility(IResponseFactory,
                                                 default=Response)

        response = response_factory(result)

        if request is not None:
            attrs = request.__dict__
            content_type = attrs.get('response_content_type', None)
            if content_type is not None:
                response.content_type = content_type
            headerlist = attrs.get('response_headerlist', None)
            if headerlist is not None:
                for k, v in headerlist:
                    response.headers.add(k, v)
            status = attrs.get('response_status', None)
            if status is not None:
                response.status = status
            charset = attrs.get('response_charset', None)
            if charset is not None:
                response.charset = charset
            cache_for = attrs.get('response_cache_for', None)
            if cache_for is not None:
                response.cache_expires = cache_for

        return response

