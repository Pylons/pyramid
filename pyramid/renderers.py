import os
import pkg_resources
import threading

from zope.interface import implements
from zope.deprecation import deprecated

from pyramid.interfaces import IChameleonLookup
from pyramid.interfaces import IChameleonTranslate
from pyramid.interfaces import IRendererGlobalsFactory
from pyramid.interfaces import IRendererFactory
from pyramid.interfaces import IResponseFactory
from pyramid.interfaces import ITemplateRenderer
from pyramid.interfaces import IRendererInfo

from pyramid.asset import asset_spec_from_abspath
from pyramid.compat import json
from pyramid.decorator import reify
from pyramid.events import BeforeRender
from pyramid.path import caller_package
from pyramid.path import package_path
from pyramid.response import Response
from pyramid.threadlocal import get_current_registry

# API

def render(renderer_name, value, request=None, package=None):
    """ Using the renderer specified as ``renderer_name`` (a template
    or a static renderer) render the value (or set of values) present
    in ``value``. Return the result of the renderer's ``__call__``
    method (usually a string or Unicode).

    If the renderer name refers to a file on disk (such as when the
    renderer is a template), it's usually best to supply the name as a
    :term:`asset specification`
    (e.g. ``packagename:path/to/template.pt``).

    You may supply a relative asset spec as ``renderer_name``.  If
    the ``package`` argument is supplied, a relative renderer path
    will be converted to an absolute asset specification by
    combining the package supplied as ``package`` with the relative
    asset specification supplied as ``renderer_name``.  If you do
    not supply a ``package`` (or ``package`` is ``None``) the package
    name of the *caller* of this function will be used as the package.

    The ``value`` provided will be supplied as the input to the
    renderer.  Usually, for template renderings, this should be a
    dictionary.  For other renderers, this will need to be whatever
    sort of value the renderer expects.

    The 'system' values supplied to the renderer will include a basic
    set of top-level system names, such as ``request``, ``context``,
    and ``renderer_name``.  If :term:`renderer globals` have been
    specified, these will also be used to agument the value.

    Supply a ``request`` parameter in order to provide the renderer
    with the most correct 'system' values (``request`` and ``context``
    in particular).

    """
    try:
        registry = request.registry
    except AttributeError:
        registry = None
    if package is None:
        package = caller_package()
    helper = RendererHelper(name=renderer_name, package=package,
                            registry=registry)
    return helper.render(value, None, request=request)

def render_to_response(renderer_name, value, request=None, package=None):
    """ Using the renderer specified as ``renderer_name`` (a template
    or a static renderer) render the value (or set of values) using
    the result of the renderer's ``__call__`` method (usually a string
    or Unicode) as the response body.

    If the renderer name refers to a file on disk (such as when the
    renderer is a template), it's usually best to supply the name as a
    :term:`asset specification`.

    You may supply a relative asset spec as ``renderer_name``.  If
    the ``package`` argument is supplied, a relative renderer name
    will be converted to an absolute asset specification by
    combining the package supplied as ``package`` with the relative
    asset specification supplied as ``renderer_name``.  If you do
    not supply a ``package`` (or ``package`` is ``None``) the package
    name of the *caller* of this function will be used as the package.

    The ``value`` provided will be supplied as the input to the
    renderer.  Usually, for template renderings, this should be a
    dictionary.  For other renderers, this will need to be whatever
    sort of value the renderer expects.

    The 'system' values supplied to the renderer will include a basic
    set of top-level system names, such as ``request``, ``context``,
    and ``renderer_name``.  If :term:`renderer globals` have been
    specified, these will also be used to agument the value.

    Supply a ``request`` parameter in order to provide the renderer
    with the most correct 'system' values (``request`` and ``context``
    in particular). Keep in mind that if the ``request`` parameter is
    not passed in, any changes to ``request.response`` attributes made
    before calling this function will be ignored.

    """
    try:
        registry = request.registry
    except AttributeError:
        registry = None
    if package is None:
        package = caller_package()
    helper = RendererHelper(name=renderer_name, package=package,
                            registry=registry)
    return helper.render_to_response(value, None, request=request)

def get_renderer(renderer_name, package=None):
    """ Return the renderer object for the renderer named as
    ``renderer_name``.

    You may supply a relative asset spec as ``renderer_name``.  If
    the ``package`` argument is supplied, a relative renderer name
    will be converted to an absolute asset specification by
    combining the package supplied as ``package`` with the relative
    asset specification supplied as ``renderer_name``.  If you do
    not supply a ``package`` (or ``package`` is ``None``) the package
    name of the *caller* of this function will be used as the package.
    """
    if package is None:
        package = caller_package()
    helper = RendererHelper(name=renderer_name, package=package)
    return helper.renderer

# concrete renderer factory implementations (also API)

def json_renderer_factory(info):
    def _render(value, system):
        request = system.get('request')
        if request is not None:
            response = request.response
            ct = response.content_type
            if ct == response.default_content_type:
                response.content_type = 'application/json'
        return json.dumps(value)
    return _render

def string_renderer_factory(info):
    def _render(value, system):
        if not isinstance(value, basestring):
            value = str(value)
        request = system.get('request')
        if request is not None:
            response = request.response
            ct = response.content_type
            if ct == response.default_content_type:
                response.content_type = 'text/plain'
        return value
    return _render

class JSONP(object):
    """ `JSONP <http://en.wikipedia.org/wiki/JSONP>`_ renderer factory helper
    which implements a hybrid json/jsonp renderer.  JSONP is useful for
    making cross-domain AJAX requests.

    Configure a JSONP renderer using the
    :meth:`pyramid.config.Configurator.add_renderer` API at application
    startup time:

    .. code-block:: python

       from pyramid.config import Configurator

       config = Configurator()
       config.add_renderer('jsonp', JSONP(param_name='callback'))

    Once this renderer is registered via
    :meth:`~pyramid.config.Configurator.add_renderer` as above, you can use
    ``jsonp`` as the ``renderer=`` parameter to ``@view_config`` or
    :meth:`pyramid.config.Configurator.add_view``:

    .. code-block:: python

       from pyramid.view import view_config

       @view_config(renderer='jsonp')
       def myview(request):
           return {'greeting':'Hello world'}

    When a view is called that uses the JSONP renderer:

    - If there is a parameter in the request's HTTP query string that matches
      the ``param_name`` of the registered JSONP renderer (by default,
      ``callback``), the renderer will return a JSONP response.

    - If there is no callback parameter in the request's query string, the
      renderer will return a 'plain' JSON response.

    .. note:: This feature is new in Pyramid 1.1.

    See also: :ref:`jsonp_renderer`.
    """
    
    def __init__(self, param_name='callback'):
        self.param_name = param_name

    def __call__(self, info):
        """ Returns JSONP-encoded string with content-type
        ``application/javascript`` if query parameter matching
        ``self.param_name`` is present in request.GET; otherwise returns
        plain-JSON encoded string with content-type ``application/json``"""
        def _render(value, system):
            request = system['request']
            val =  json.dumps(value)
            callback = request.GET.get(self.param_name)
            if callback is None:
                ct = 'application/json'
                body = val
            else:
                ct = 'application/javascript'
                body = '%s(%s)' % (callback, val)
            response = request.response
            if response.content_type == response.default_content_type:
                response.content_type = ct
            return body
        return _render

# utility functions, not API

class ChameleonRendererLookup(object):
    implements(IChameleonLookup)
    def __init__(self, impl, registry):
        self.impl = impl
        self.registry = registry
        self.lock = threading.Lock()

    def get_spec(self, name, package):
        if not package:
            # if there's no package, we can't do any conversion
            return name

        spec = name
        isabspath = os.path.isabs(name)
        colon_in_name = ':' in name
        isabsspec = colon_in_name and (not isabspath)
        isrelspec = (not isabsspec) and (not isabspath)

        # if it's already an absolute spec, we don't need to do anything,
        # but if it's a relative spec or an absolute path, we need to try
        # to convert it to an absolute spec

        if isrelspec:
            # convert relative asset spec to absolute asset spec
            pp = package_path(package)
            spec = os.path.join(pp, spec)
            spec = asset_spec_from_abspath(spec, package)

        elif isabspath:
            # convert absolute path to absolute asset spec
            spec = asset_spec_from_abspath(spec, package)

        return spec

    @property # wait until completely necessary to look up translator
    def translate(self):
        return self.registry.queryUtility(IChameleonTranslate)

    @property # wait until completely necessary to look up debug_templates
    def debug(self):
        settings = self.registry.settings
        if settings is None:
            return False
        return settings.get('debug_templates', False)

    @property # wait until completely necessary to look up reload_templates
    def auto_reload(self):
        settings = self.registry.settings
        if settings is None:
            return False
        return settings.get('reload_templates', False)

    def __call__(self, info):
        spec = self.get_spec(info.name, info.package)
        registry = info.registry

        if os.path.isabs(spec):
            # 'spec' is an absolute filename
            if not os.path.exists(spec):
                raise ValueError('Missing template file: %s' % spec)
            renderer = registry.queryUtility(ITemplateRenderer, name=spec)
            if renderer is None:
                renderer = self.impl(spec, self)
                # cache the template
                try:
                    self.lock.acquire()
                    registry.registerUtility(renderer,
                                             ITemplateRenderer, name=spec)
                finally:
                    self.lock.release()
        else:
            # spec is a package:relpath asset spec
            renderer = registry.queryUtility(ITemplateRenderer, name=spec)
            if renderer is None:
                try:
                    package_name, filename = spec.split(':', 1)
                except ValueError: # pragma: no cover
                    # somehow we were passed a relative pathname; this
                    # should die
                    package_name = caller_package(4).__name__
                    filename = spec
                abspath = pkg_resources.resource_filename(package_name,
                                                          filename)
                if not pkg_resources.resource_exists(package_name, filename):
                    raise ValueError(
                        'Missing template asset: %s (%s)' % (spec, abspath))
                renderer = self.impl(abspath, self)
                settings = info.settings
                if not settings.get('reload_assets'):
                    # cache the template
                    self.lock.acquire()
                    try:
                        registry.registerUtility(renderer, ITemplateRenderer,
                                                 name=spec)
                    finally:
                        self.lock.release()

        return renderer

registry_lock = threading.Lock()

def template_renderer_factory(info, impl, lock=registry_lock):
    registry = info.registry
    lookup = registry.queryUtility(IChameleonLookup, name=info.type)
    if lookup is None:
        lookup = ChameleonRendererLookup(impl, registry)
        lock.acquire()
        try:
            registry.registerUtility(lookup, IChameleonLookup, name=info.type)
        finally:
            lock.release()
    return lookup(info)

def renderer_from_name(path, package=None):
    return RendererHelper(name=path, package=package).renderer

deprecated(
    'renderer_from_name',
    'The "pyramid.renderers.renderer_from_name" function was never an API. '
    'However, its use has been observed "in the wild."  It will disappear in '
    'the next major release. To replace it, use the '
    '``pyramid.renderers.get_renderer`` API instead. ')

class RendererHelper(object):
    implements(IRendererInfo)
    def __init__(self, name=None, package=None, registry=None):
        if name and '.' in name:
            rtype = os.path.splitext(name)[1]
        else:
            # important.. must be a string; cannot be None; see issue 249
            rtype = name or ''

        if registry is None:
            registry = get_current_registry()

        self.name = name
        self.package = package
        self.type = rtype
        self.registry = registry

    @reify
    def settings(self):
        settings = self.registry.settings
        if settings is None:
            settings = {}
        return settings

    @reify
    def renderer(self):
        factory = self.registry.queryUtility(IRendererFactory, name=self.type)
        if factory is None:
            raise ValueError(
                'No such renderer factory %s' % str(self.type))
        return factory(self)

    def get_renderer(self):
        return self.renderer

    def render_view(self, request, response, view, context):
        system = {'view':view,
                  'renderer_name':self.name, # b/c
                  'renderer_info':self,
                  'context':context,
                  'request':request
                  }
        return self.render_to_response(response, system, request=request)

    def render(self, value, system_values, request=None):
        renderer = self.renderer
        if system_values is None:
            system_values = {
                'view':None,
                'renderer_name':self.name, # b/c
                'renderer_info':self,
                'context':getattr(request, 'context', None),
                'request':request,
                }

        system_values = BeforeRender(system_values, value)

        registry = self.registry
        globals_factory = registry.queryUtility(IRendererGlobalsFactory)

        if globals_factory is not None:
            renderer_globals = globals_factory(system_values)
            if renderer_globals:
                system_values.update(renderer_globals)

        registry.notify(system_values)

        result = renderer(value, system_values)
        return result

    def render_to_response(self, value, system_values, request=None):
        result = self.render(value, system_values, request=request)
        return self._make_response(result, request)

    def _make_response(self, result, request):
        # broken out of render_to_response as a separate method for testing
        # purposes
        response = getattr(request, 'response', None)
        if response is None:
            # request is None or request is not a pyramid.response.Response
            registry = self.registry
            response_factory = registry.queryUtility(IResponseFactory,
                                                     default=Response)

            response = response_factory()

        if result is None:
            result = ''

        if isinstance(result, unicode):
            response.unicode_body = result
        else:
            response.body = result

        if request is not None:
            # deprecated mechanism to set up request.response_* attrs, see
            # pyramid.request.Request
            attrs = request.__dict__
            content_type = attrs.get('_response_content_type', None)
            if content_type is not None:
                response.content_type = content_type
            headerlist = attrs.get('_response_headerlist', None)
            if headerlist is not None:
                for k, v in headerlist:
                    response.headers.add(k, v)
            status = attrs.get('_response_status', None)
            if status is not None:
                response.status = status
            charset = attrs.get('_response_charset', None)
            if charset is not None:
                response.charset = charset
            cache_for = attrs.get('_response_cache_for', None)
            if cache_for is not None:
                response.cache_expires = cache_for
        return response

    def clone(self, name=None, package=None, registry=None):
        if name is None:
            name = self.name
        if package is None:
            package = self.package
        if registry is None:
            registry = self.registry
        return self.__class__(name=name, package=package, registry=registry)

class NullRendererHelper(RendererHelper):
    """ Special renderer helper that has render_* methods which simply return
    the value they are fed rather than converting them to response objects;
    useful for testing purposes and special case view configuration
    registrations that want to use the view configuration machinery but do
    not want actual rendering to happen ."""
    def __init__(self, name=None, package=None, registry=None):
        # we override the initializer to avoid calling get_current_registry
        # (it will return a reference to the global registry when this
        # thing is called at module scope; we don't want that).
        self.name = None
        self.package = None
        self.type = ''
        self.registry = None

    @property
    def settings(self):
        return get_current_registry().settings or {}

    def render_view(self, request, value, view, context):
        return value

    def render(self, value, system_values, request=None):
        return value
    
    def render_to_response(self, value, system_values, request=None):
        return value

    def clone(self, name=None, package=None, registry=None):
        return self
    
null_renderer = NullRendererHelper()
