import os
import pkg_resources

from webob import Response

from zope.deprecation import deprecated

from repoze.bfg.interfaces import IRendererGlobalsFactory
from repoze.bfg.interfaces import IResponseFactory
from repoze.bfg.interfaces import ITemplateRenderer

from repoze.bfg.compat import json
from repoze.bfg.path import caller_package
from repoze.bfg.settings import get_settings
from repoze.bfg.threadlocal import get_current_registry

# API

def render(_renderer_name, **values):
    """ Using the renderer specified as ``renderer_name`` (a template
    or a static renderer) render the set of values present in
    ``**values``. Return the result of the renderer's ``__call__``
    method (usually a string or Unicode).

    If the renderer name refers to a file on disk (such as when the
    renderer is a template), it's usually best to supply the name as a
    :term:`resource specification`.  You may supply a relative
    filename as renderer name; it will be converted to a resource
    specification by combining the package name of the *caller* of
    this function with the relative filename.

    The ``values`` provided will be supplied as top-level names to the
    renderer.  These will be augmented by a basic set of top-level
    system names, such as ``request``, ``context``, and
    ``renderer_name` unless any of these names is already provided
    within ``*values``.  If :term:`renderer globals` have been
    specified, these will also be used to agument the value.

    Supply a ``request`` parameter containing the current
    :mod:`repoze.bfg` request as part of ``**values`` in order to
    provide the renderer with the most correct 'system' values
    (``request`` and ``context`` in particular).

    .. note:: This API is new in :mod:`repoze.bfg` 1.3.

    """
    package = caller_package()
    request = values.pop('request', None)
    return _render(_renderer_name, request, values, None, None, package)

def render_to_response(_renderer_name, **values):
    """ Using the renderer specified as ``renderer_name`` (a template
    or a static renderer) render the set of values present in
    ``**values``. Return a :term:`Response` object wrapping the result
    of of the renderer's ``__call__`` method.

    If the renderer name refers to a file on disk (such as when the
    renderer is a template), it's usually best to supply the name as a
    :term:`resource specification`.  You may supply a relative
    filename as renderer name; it will be converted to a resource
    specification by combining the package name of the *caller* of
    this function with the relative filename.

    The ``values`` provided will be supplied as top-level names to the
    renderer.  These will be augmented by a basic set of top-level
    system names, such as ``request``, ``context``, and
    ``renderer_name` unless any of these names is already provided
    within ``*values``.  If :term:`renderer globals` have been
    specified, these will also be used to agument the value.

    Supply a ``request`` parameter containing the current
    :mod:`repoze.bfg` request as part of ``**values`` in order to
    provide the renderer with the most correct 'system' values
    (``request`` and ``context`` in particular).

    .. note:: This API is new in :mod:`repoze.bfg` 1.3.
    """
    package = caller_package()
    request = values.pop('request', None)
    return _render_to_response(_renderer_name, request, values, None, None,
                               package)

def get_renderer(spec):
    """ Return the renderer object for the renderer named as ``spec`` """
    package = caller_package()
    return renderer_from_name(spec, package)

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
    from repoze.bfg.configuration import Configurator
    reg = get_current_registry()
    config = Configurator(reg, package=package)
    return config._renderer_from_name(path)

def _render(renderer_name, request, values, system_values, renderer, package):
    try:
        registry = request.registry
    except AttributeError:
        registry = get_current_registry()

    if renderer is None:
        from repoze.bfg.configuration import Configurator
        config = Configurator(registry, package=package)
        renderer = config._renderer_from_name(renderer_name)

    if system_values is None:
        system_values = {
            'view':None,
            'renderer_name':renderer_name,
            'context':getattr(request, 'context', None),
            'request':request,
            }

    globals_factory = registry.queryUtility(IRendererGlobalsFactory)

    if globals_factory is not None:
        renderer_globals = globals_factory(system_values)
        if renderer_globals:
            system_values.update(renderer_globals)

    result = renderer(values, system_values)
    return result

def _render_to_response(renderer_name, request, values, system_values,
                        renderer, package):
    result = _render(renderer_name, request, values, system_values, renderer,
                     package)
    return _make_response(request, result)

def rendered_response(renderer, result, view, context, request, renderer_name):
    # XXX: deprecated, left here only to not break old code; use
    # render_to_response instead
    if ( hasattr(result, 'app_iter') and hasattr(result, 'headerlist')
         and hasattr(result, 'status') ):
        return result

    system = {'view':view, 'renderer_name':renderer_name,
              'context':context, 'request':request}

    return _render_to_response(renderer_name, request, result, system, renderer,
                               None)

deprecated('rendered_response',
    "('repoze.bfg.renderers.rendered_response' is not a public API; it is  "
    "officially deprecated as of repoze.bfg 1.3; "
    "use repoze.bfg.renderers.render_to_response instead')",
    )

def _make_response(request, result):
    try:
        registry = request.registry
    except AttributeError:
        registry = get_current_registry()

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

