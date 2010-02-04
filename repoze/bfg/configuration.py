import os
import re
import sys
import threading
import inspect

from webob import Response

from zope.configuration import xmlconfig

from zope.interface import Interface
from zope.interface import implementedBy
from zope.interface.interfaces import IInterface
from zope.interface import implements

from repoze.bfg.interfaces import IAuthenticationPolicy
from repoze.bfg.interfaces import IAuthorizationPolicy
from repoze.bfg.interfaces import IDebugLogger
from repoze.bfg.interfaces import IDefaultRootFactory
from repoze.bfg.interfaces import IForbiddenView
from repoze.bfg.interfaces import IMultiView
from repoze.bfg.interfaces import INotFoundView
from repoze.bfg.interfaces import IPackageOverrides
from repoze.bfg.interfaces import IRendererFactory
from repoze.bfg.interfaces import IRequest
from repoze.bfg.interfaces import IResponseFactory
from repoze.bfg.interfaces import IRootFactory
from repoze.bfg.interfaces import IRouteRequest
from repoze.bfg.interfaces import IRoutesMapper
from repoze.bfg.interfaces import ISecuredView
from repoze.bfg.interfaces import ISettings
from repoze.bfg.interfaces import ITemplateRenderer
from repoze.bfg.interfaces import ITraverser
from repoze.bfg.interfaces import IView

from repoze.bfg import chameleon_text
from repoze.bfg import chameleon_zpt
from repoze.bfg import renderers
from repoze.bfg.authorization import ACLAuthorizationPolicy
from repoze.bfg.compat import all
from repoze.bfg.compat import walk_packages
from repoze.bfg.events import WSGIApplicationCreatedEvent
from repoze.bfg.exceptions import Forbidden
from repoze.bfg.exceptions import NotFound
from repoze.bfg.exceptions import ConfigurationError
from repoze.bfg.log import make_stream_logger
from repoze.bfg.path import caller_package
from repoze.bfg.registry import Registry
from repoze.bfg.request import route_request_iface
from repoze.bfg.resource import PackageOverrides
from repoze.bfg.resource import resolve_resource_spec
from repoze.bfg.settings import Settings
from repoze.bfg.static import StaticRootFactory
from repoze.bfg.threadlocal import get_current_registry
from repoze.bfg.threadlocal import manager
from repoze.bfg.traversal import traversal_path
from repoze.bfg.traversal import DefaultRootFactory
from repoze.bfg.traversal import find_interface
from repoze.bfg.urldispatch import RoutesMapper
from repoze.bfg.view import render_view_to_response
from repoze.bfg.view import static

MAX_WEIGHT = 10000

DEFAULT_RENDERERS = (
    ('.pt', chameleon_zpt.renderer_factory),
    ('.txt', chameleon_text.renderer_factory),
    ('json', renderers.json_renderer_factory),
    ('string', renderers.string_renderer_factory),
    )

class Configurator(object):
    """
    A Configurator is used to configure a :mod:`repoze.bfg`
    :term:`application registry`.

    The Configurator accepts a number of arguments: ``registry``,
    ``package``, ``settings``, ``root_factory``, ``zcml_file``,
    ``authentication_policy``, ``authorization_policy``, ``renderers``
    and ``debug_logger``.

    If the ``registry`` argument is passed as a non-``None`` value, it
    must be an instance of the :class:`repoze.bfg.registry.Registry`
    class representing the registry to configure.  If ``registry`` is
    ``None``, the configurator will create a
    :class:`repoze.bfg.registry.Registry` instance itself; it will
    also perform some default configuration that would not otherwise
    be done.  After construction, the configurator may be used to add
    configuration to the registry.  The overall state of a registry is
    called the 'configuration state'.

    .. warning:: If a ``registry`` is passed to the Configurator
       constructor, all other constructor arguments except ``package``
       are ignored.

    If the ``package`` argument is passed, it must be a reference to a
    Python :term:`package` (e.g. ``sys.modules['thepackage']``).  This
    value is used as a basis to convert relative paths passed to
    various configuration methods, such as methods which accept a
    ``renderer`` argument, into absolute paths.  If ``None`` is passed
    (the default), the package is assumed to be the Python package in
    which the *caller* of the ``Configurator`` constructor lives.

    If the ``settings`` argument is passed, it should be a Python
    dictionary representing the deployment settings for this
    application.  These are later retrievable using the
    :func:`repoze.bfg.settings.get_settings` API.

    If the ``root_factory`` argument is passed, it should be an object
    representing the default :term:`root factory` for your
    application.  If it is ``None``, a default root factory will be
    used.

    If ``authentication_policy`` is passed, it should be an instance
    of an :term:`authentication policy`.

    If ``authorization_policy`` is passed, it should be an instance
    of an :term:`authorization policy`.

    .. note:: A ``ConfigurationError`` will be raised when an
       authorization policy is supplied without also supplying an
       authentication policy (authorization requires authentication).

    If ``renderers`` is passed, it should be a list of tuples
    representing a set of :term:`renderer` factories which should be
    configured into this application.  If it is not passed, a default
    set of renderer factories is used.

    If ``debug_logger`` is not passed, a default debug logger that
    logs to stderr will be used.  If it is passed, it should be an
    instance of the :class:`logging.Logger` (PEP 282) standard library
    class.  The debug logger is used by :mod:`repoze.bfg` itself to
    log warnings and authorization debugging information.  """
    
    manager = manager # for testing injection
    def __init__(self, registry=None, package=None, settings=None,
                 root_factory=None, authentication_policy=None,
                 authorization_policy=None, renderers=DEFAULT_RENDERERS,
                 debug_logger=None):
        self.package = package or caller_package()
        self.registry = registry
        if registry is None:
            registry = Registry(self.package.__name__)
            self.registry = registry
            self.setup_registry(
                settings=settings,
                root_factory=root_factory,
                authentication_policy=authentication_policy,
                authorization_policy=authorization_policy,
                renderers=renderers,
                debug_logger=debug_logger)

    def _set_settings(self, mapping):
        settings = Settings(mapping or {})
        self.registry.registerUtility(settings, ISettings)
        return settings

    def _set_root_factory(self, factory):
        """ Add a :term:`root factory` to the current configuration
        state.  If the ``factory`` argument is ``None`` a default root
        factory will be registered."""
        if factory is None:
            factory = DefaultRootFactory
        self.registry.registerUtility(factory, IRootFactory)
        self.registry.registerUtility(factory, IDefaultRootFactory) # b/c
        
    def _renderer_from_name(self, path_or_spec):
        if path_or_spec is None:
            # check for global default renderer
            factory = self.registry.queryUtility(IRendererFactory)
            if factory is not None:
                return factory(path_or_spec)
            return None

        if '.' in path_or_spec:
            name = os.path.splitext(path_or_spec)[1]
            spec = self._make_spec(path_or_spec)
        else:
            name = path_or_spec
            spec = path_or_spec

        factory = self.registry.queryUtility(IRendererFactory, name=name)
        if factory is None:
            raise ValueError('No renderer for renderer name %r' % name)
        return factory(spec)

    def _set_authentication_policy(self, policy, _info=u''):
        """ Add a :mod:`repoze.bfg` :term:`authentication policy` to
        the current configuration."""
        self.registry.registerUtility(policy, IAuthenticationPolicy, info=_info)
        
    def _set_authorization_policy(self, policy, _info=u''):
        """ Add a :mod:`repoze.bfg` :term:`authorization policy` to
        the current configuration state."""
        self.registry.registerUtility(policy, IAuthorizationPolicy, info=_info)

    def _make_spec(self, path_or_spec):
        package, filename = resolve_resource_spec(path_or_spec,
                                                  self.package.__name__)
        if package is None:
            return filename # absolute filename
        return '%s:%s' % (package, filename)

    def _split_spec(self, path_or_spec):
        return resolve_resource_spec(path_or_spec, self.package.__name__)

    def _derive_view(self, view, permission=None, predicates=(),
                     attr=None, renderer_name=None, wrapper_viewname=None,
                     viewname=None, accept=None, score=MAX_WEIGHT):
        renderer = self._renderer_from_name(renderer_name)
        authn_policy = self.registry.queryUtility(IAuthenticationPolicy)
        authz_policy = self.registry.queryUtility(IAuthorizationPolicy)
        settings = self.registry.queryUtility(ISettings)
        logger = self.registry.queryUtility(IDebugLogger)
        mapped_view = _map_view(view, attr, renderer, renderer_name)
        owrapped_view = _owrap_view(mapped_view, viewname, wrapper_viewname)
        secured_view = _secure_view(owrapped_view, permission,
                                    authn_policy, authz_policy)
        debug_view = _authdebug_view(secured_view, permission, 
                                     authn_policy, authz_policy, settings,
                                     logger)
        predicated_view = _predicate_wrap(debug_view, predicates)
        derived_view = _attr_wrap(predicated_view, accept, score)
        return derived_view

    def _override(self, package, path, override_package, override_prefix,
                  _info=u'', PackageOverrides=PackageOverrides):
            pkg_name = package.__name__
            override_pkg_name = override_package.__name__
            override = self.registry.queryUtility(
                IPackageOverrides, name=pkg_name)
            if override is None:
                override = PackageOverrides(package)
                self.registry.registerUtility(override, IPackageOverrides,
                                              name=pkg_name, info=_info)
            override.insert(path, override_pkg_name, override_prefix)


    def _system_view(self, iface, view=None, attr=None, renderer=None,
                    wrapper=None, _info=u''):
        if not view:
            if renderer:
                def view(context, request):
                    return {}
            else:
                raise ConfigurationError(
                    '"view" argument was not specified and no renderer '
                    'specified')

        derived_view = self._derive_view(view, attr=attr,
                                         renderer_name=renderer,
                                         wrapper_viewname=wrapper)
        self.registry.registerUtility(derived_view, iface, '', info=_info)

    def _set_security_policies(self, authentication, authorization=None):
        if authorization is None:
            authorization = ACLAuthorizationPolicy() # default
        if authorization and not authentication:
            raise ConfigurationError(
                'If the "authorization" is passed a value, '
                'the "authentication" argument must also be '
                'passed a value; authorization requires authentication.')
        self._set_authentication_policy(authentication)
        self._set_authorization_policy(authorization)

    def _fix_registry(self):
        """ Fix up a ZCA component registry that is not a
        repoze.bfg.registry.Registry by adding analogues of
        ``has_listeners`` and ``notify`` through monkey-patching."""

        if not hasattr(self.registry, 'notify'):
            def notify(*events):
                [ _ for _ in self.registry.subscribers(events, None) ]
            self.registry.notify = notify

        if not hasattr(self.registry, 'has_listeners'):
            self.registry.has_listeners = True

    # API

    def setup_registry(self, settings=None, root_factory=None,
                       authentication_policy=None, authorization_policy=None,
                       renderers=DEFAULT_RENDERERS, debug_logger=None):
        """ When you pass a non-``None`` ``registry`` argument to the
        :term:`Configurator` constructor, no initial 'setup' is
        performed against the registry.  This is because the registry
        you pass in may have already been initialized for use under
        :mod:`repoze.bfg` via a different configurator.  However, in
        some circumstances, such as when you want to use the Zope
        'global` registry instead of a registry created as a result of
        the Configurator constructor, or when you want to reset the
        initial setup of a registry, you *do* want to explicitly
        initialize the registry associated with a Configurator for use
        under :mod:`repoze.bfg`.  Use ``setup_registry`` to do this
        initialization.

        ``setup_registry`` configures settings, a root factory,
        security policies, renderers, and a debug logger using the
        configurator's current registry, as per the descriptions in
        the Configurator constructor."""
        self._fix_registry()
        self._set_settings(settings)
        self._set_root_factory(root_factory)
        if debug_logger is None:
            debug_logger = make_stream_logger('repoze.bfg.debug', sys.stderr)
        registry = self.registry
        registry.registerUtility(debug_logger, IDebugLogger)
        registry.registerUtility(debug_logger, IDebugLogger,
                                 'repoze.bfg.debug') # b /c
        if authentication_policy or authorization_policy:
            self._set_security_policies(authentication_policy,
                                        authorization_policy)
        for name, renderer in renderers:
            self.add_renderer(name, renderer)

    # getSiteManager is a unit testing dep injection
    def hook_zca(self, getSiteManager=None):
        """ Call :func:`zope.component.getSiteManager.sethook` with
        the argument
        :data:`repoze.bfg.threadlocal.get_current_registry`, causing
        the :term:`Zope Component Architecture` 'global' APIs such as
        :func:`zope.component.getSiteManager`,
        :func:`zope.component.getAdapter` and others to use the
        :mod:`repoze.bfg` :term:`application registry` rather than the
        Zope 'global' registry.  If :mod:`zope.component` cannot be
        imported, this method will raise an :exc:`ImportError`."""
        if getSiteManager is None:
            from zope.component import getSiteManager
        getSiteManager.sethook(get_current_registry)

    # getSiteManager is a unit testing dep injection
    def unhook_zca(self, getSiteManager=None):
        """ Call :func:`zope.component.getSiteManager.reset` to undo
        the action of
        :meth:`repoze.bfg.configuration.Configurator.hook_zca`.  If
        :mod:`zope.component` cannot be imported, this method will
        raise an :exc:`ImportError`."""
        if getSiteManager is None: # pragma: no cover
            from zope.component import getSiteManager
        getSiteManager.reset()

    def begin(self, request=None):
        """ Indicate that application or test configuration has begun.
        This pushes a dictionary containing the :term:`application
        registry` implied by ``registry`` attribute of this
        configurator and the :term:`request` implied by the
        ``request`` argument on to the :term:`thread local` stack
        consulted by various :mod:`repoze.bfg.threadlocal` API
        functions."""
        self.manager.push({'registry':self.registry, 'request':request})

    def end(self):
        """ Indicate that application or test configuration has ended.
        This pops the last value pushed on to the :term:`thread local`
        stack (usually by the ``begin`` method) and returns that
        value.
        """
        return self.manager.pop()

    def add_subscriber(self, subscriber, iface=None, info=u''):
        """Add an event :term:`subscriber` for the event stream
        implied by the supplied ``iface`` interface.  The
        ``subscriber`` argument represents a callable object; it will
        be called with a single object ``event`` whenever
        :mod:`repoze.bfg` emits an :term:`event` associated with the
        ``iface``.  Using the default ``iface`` value, ``None`` will
        cause the subscriber to be registered for all event types. See
        :ref:`events_chapter` for more information about events and
        subscribers."""
        if iface is None:
            iface = (Interface,)
        if not isinstance(iface, (tuple, list)):
            iface = (iface,)
        self.registry.registerHandler(subscriber, iface, info=info)
        return subscriber

    def add_settings(self, settings=None, **kw):
        """Augment the ``settings`` argument passed in to the
        Configurator constructor with one or more 'setting' key/value
        pairs.  A setting is a single key/value pair in the
        dictionary-ish object returned from the API
        :func:`repoze.bfg.settings.get_settings`.

        You may pass a dictionary::

           config.add_settings({'external_uri':'http://example.com'})

        Or a set of key/value pairs::
    
           config.add_settings(external_uri='http://example.com')

        This function is useful when you need to test code that
        calls the :func:`repoze.bfg.settings.get_settings` API and which
        uses return values from that API.

        .. note:: This method is new as of :mod:`repoze.bfg` 1.2.
        """
        if settings is None:
            settings = {}
        utility = self.registry.queryUtility(ISettings)
        if utility is None:
            utility = self._set_settings(settings)
        utility.update(settings)
        utility.update(kw)

    def make_wsgi_app(self):
        """ Returns a :mod:`repoze.bfg` WSGI application representing
        the current configuration state and sends a
        :class:`repoze.bfg.interfaces.IWSGIApplicationCreatedEvent`
        event to all listeners."""
        from repoze.bfg.router import Router # avoid circdep
        app = Router(self.registry)
        # We push the registry on to the stack here in case any code
        # that depends on the registry threadlocal APIs used in
        # listeners subscribed to the WSGIApplicationCreatedEvent.
        self.manager.push({'registry':self.registry, 'request':None})
        try:
            self.registry.notify(WSGIApplicationCreatedEvent(app))
        finally:
            self.manager.pop()
        return app

    def load_zcml(self, spec='configure.zcml', lock=threading.Lock()):
        """ Load configuration from a :term:`ZCML` file into the
        current configuration state.  The ``spec`` argument is an
        absolute filename, a relative filename, or a :term:`resource
        specification`, defaulting to ``configure.zcml`` (relative to
        the package of the configurator's caller)."""
        package_name, filename = self._split_spec(spec)
        if package_name is None: # absolute filename
            package = self.package
        else:
            __import__(package_name)
            package = sys.modules[package_name]

        lock.acquire()
        self.manager.push({'registry':self.registry, 'request':None})
        try:
            xmlconfig.file(filename, package, execute=True)
        finally:
            lock.release()
            self.manager.pop()
        return self.registry

    def add_view(self, view=None, name="", for_=None, permission=None, 
                 request_type=None, route_name=None, request_method=None,
                 request_param=None, containment=None, attr=None,
                 renderer=None, wrapper=None, xhr=False, accept=None,
                 header=None, path_info=None, custom_predicates=(),
                 context=None, _info=u''):
        """ Add a :term:`view configuration` to the current
        configuration state.  Arguments to ``add_view`` are broken
        down below into *predicate* arguments and *non-predicate*
        arguments.  Predicate arguments narrow the circumstances in
        which the view callable will be invoked when a request is
        presented to :mod:`repoze.bfg`; non-predicate arguments are
        informational.

        Non-Predicate Arguments

        view

          A reference to a :term:`view callable`.  This argument is
          required unless a ``renderer`` argument also exists.  If a
          ``renderer`` argument is passed, and a ``view`` argument is
          not provided, the view callable defaults to a callable that
          returns an empty dictionary (see
          :ref:`views_which_use_a_renderer`).

        permission

          The name of a :term:`permission` that the user must possess
          in order to invoke the :term:`view callable`.  See
          :ref:`view_security_section` for more information about view
          security and permissions.

        attr

          The view machinery defaults to using the ``__call__`` method
          of the :term:`view callable` (or the function itself, if the
          view callable is a function) to obtain a response.  The
          ``attr`` value allows you to vary the method attribute used
          to obtain the response.  For example, if your view was a
          class, and the class has a method named ``index`` and you
          wanted to use this method instead of the class' ``__call__``
          method to return the response, you'd say ``attr="index"`` in the
          view configuration for the view.  This is
          most useful when the view definition is a class.

        renderer

          This is either a single string term (e.g. ``json``) or a
          string implying a path or :term:`resource specification`
          (e.g. ``templates/views.pt``) naming a :term:`renderer`
          implementation.  If the ``renderer`` value does not contain
          a dot ``.``, the specified string will be used to look up a
          renderer implementation, and that renderer implementation
          will be used to construct a response from the view return
          value.  If the ``renderer`` value contains a dot (``.``),
          the specified term will be treated as a path, and the
          filename extension of the last element in the path will be
          used to look up the renderer implementation, which will be
          passed the full path.  The renderer implementation will be
          used to construct a :term:`response` from the view return
          value.

          Note that if the view itself returns a :term:`response` (see
          :ref:`the_response`), the specified renderer implementation
          is never called.

          When the renderer is a path, although a path is usually just
          a simple relative pathname (e.g. ``templates/foo.pt``,
          implying that a template named "foo.pt" is in the
          "templates" directory relative to the directory of the
          current :term:`package` of the Configurator), a path can be
          absolute, starting with a slash on UNIX or a drive letter
          prefix on Windows.  The path can alternately be a
          :term:`resource specification` in the form
          ``some.dotted.package_name:relative/path``, making it
          possible to address template resources which live in a
          separate package.

          The ``renderer`` attribute is optional.  If it is not
          defined, the "null" renderer is assumed (no rendering is
          performed and the value is passed back to the upstream
          :mod:`repoze.bfg` machinery unmolested).

        wrapper

          The :term:`view name` of a different :term:`view
          configuration` which will receive the response body of this
          view as the ``request.wrapped_body`` attribute of its own
          :term:`request`, and the :term:`response` returned by this
          view as the ``request.wrapped_response`` attribute of its
          own request.  Using a wrapper makes it possible to "chain"
          views together to form a composite response.  The response
          of the outermost wrapper view will be returned to the user.
          The wrapper view will be found as any view is found: see
          :ref:`view_lookup`.  The "best" wrapper view will be found
          based on the lookup ordering: "under the hood" this wrapper
          view is looked up via
          ``repoze.bfg.view.render_view_to_response(context, request,
          'wrapper_viewname')``. The context and request of a wrapper
          view is the same context and request of the inner view.  If
          this attribute is unspecified, no view wrapping is done.

        Predicate Arguments

        name

          The :term:`view name`.  Read :ref:`traversal_chapter` to
          understand the concept of a view name.

        context

          An object representing Python class that the :term:`context`
          must be an instance of, *or* the :term:`interface` that the
          :term:`context` must provide in order for this view to be
          found and called.  This predicate is true when the
          :term:`context` is an instance of the represented class or
          if the :term:`context` provides the represented interface;
          it is otherwise false.  This argument may also be provided
          to ``add_view`` as ``for_`` (an older, still-supported
          spelling).

        route_name

          This value must match the ``name`` of a :term:`route
          configuration` declaration (see :ref:`urldispatch_chapter`)
          that must match before this view will be called.  Note that
          the ``route`` configuration referred to by ``route_name``
          usually has a ``*traverse`` token in the value of its
          ``path``, representing a part of the path that will be used
          by :term:`traversal` against the result of the route's
          :term:`root factory`.

          .. warning:: Using this argument services an advanced
             feature that isn't often used unless you want to perform
             traversal *after* a route has matched. See
             :ref:`hybrid_chapter` for more information on using this
             advanced feature.

        request_type

          This value should be an :term:`interface` that the
          :term:`request` must provide in order for this view to be
          found and called.  This value exists only for backwards
          compatibility purposes.

        request_method

          This value can either be one of the strings ``GET``,
          ``POST``, ``PUT``, ``DELETE``, or ``HEAD`` representing an
          HTTP ``REQUEST_METHOD``.  A view declaration with this
          argument ensures that the view will only be called when the
          request's ``method`` attribute (aka the ``REQUEST_METHOD`` of
          the WSGI environment) string matches the supplied value.

        request_param

          This value can be any string.  A view declaration with this
          argument ensures that the view will only be called when the
          :term:`request` has a key in the ``request.params``
          dictionary (an HTTP ``GET`` or ``POST`` variable) that has a
          name which matches the supplied value.  If the value
          supplied has a ``=`` sign in it,
          e.g. ``request_params="foo=123"``, then the key (``foo``)
          must both exist in the ``request.params`` dictionary, *and*
          the value must match the right hand side of the expression
          (``123``) for the view to "match" the current request.

        containment

          This value should be a reference to a Python class or
          :term:`interface` that a parent object in the
          :term:`lineage` must provide in order for this view to be
          found and called.  The nodes in your object graph must be
          "location-aware" to use this feature.  See
          :ref:`location_aware` for more information about
          location-awareness.

        xhr

          This value should be either ``True`` or ``False``.  If this
          value is specified and is ``True``, the :term:`request`
          must possess an ``HTTP_X_REQUESTED_WITH`` (aka
          ``X-Requested-With``) header that has the value
          ``XMLHttpRequest`` for this view to be found and called.
          This is useful for detecting AJAX requests issued from
          jQuery, Prototype and other Javascript libraries.

        accept

          The value of this argument represents a match query for one
          or more mimetypes in the ``Accept`` HTTP request header.  If
          this value is specified, it must be in one of the following
          forms: a mimetype match token in the form ``text/plain``, a
          wildcard mimetype match token in the form ``text/*`` or a
          match-all wildcard mimetype match token in the form ``*/*``.
          If any of the forms matches the ``Accept`` header of the
          request, this predicate will be true.

        header

          This value represents an HTTP header name or a header
          name/value pair.  If the value contains a ``:`` (colon), it
          will be considered a name/value pair
          (e.g. ``User-Agent:Mozilla/.*`` or ``Host:localhost``).  The
          value portion should be a regular expression.  If the value
          does not contain a colon, the entire value will be
          considered to be the header name
          (e.g. ``If-Modified-Since``).  If the value evaluates to a
          header name only without a value, the header specified by
          the name must be present in the request for this predicate
          to be true.  If the value evaluates to a header name/value
          pair, the header specified by the name must be present in
          the request *and* the regular expression specified as the
          value must match the header value.  Whether or not the value
          represents a header name or a header name/value pair, the
          case of the header name is not significant.

        path_info

          This value represents a regular expression pattern that will
          be tested against the ``PATH_INFO`` WSGI environment
          variable.  If the regex matches, this predicate will be
          ``True``.

        custom_predicates

          This value should be a sequence of references to custom
          predicate callables.  Use custom predicates when no set of
          predefined predicates do what you need.  Custom predicates
          can be combined with predefined predicates as necessary.
          Each custom predicate callable should accept two arguments:
          ``context`` and ``request`` and should return either
          ``True`` or ``False`` after doing arbitrary evaluation of
          the context and/or the request.  If all callables return
          ``True``, the associated view callable will be considered
          viable for a given request.

          .. note:: This feature is new as of :mod:`repoze.bfg` 1.2.
          """

        if not view:
            if renderer:
                def view(context, request):
                    return {}
            else:
                raise ConfigurationError('"view" was not specified and '
                                         'no "renderer" specified')

        if request_type in ('GET', 'HEAD', 'PUT', 'POST', 'DELETE'):
            # b/w compat for 1.0
            request_method = request_type
            request_type = None

        if request_type is not None:
            if not IInterface.providedBy(request_type):
                raise ConfigurationError(
                    'request_type must be an interface, not %s' % request_type)

        request_iface = IRequest

        if route_name is not None:
            request_iface = self.registry.queryUtility(IRouteRequest,
                                                       name=route_name)
            if request_iface is None:
                deferred_views = getattr(self.registry,
                                         'deferred_route_views', None)
                if deferred_views is None:
                    deferred_views = self.registry.deferred_route_views = {}
                info = dict(
                    view=view, name=name, for_=for_, permission=permission, 
                    request_type=request_type, route_name=route_name,
                    request_method=request_method, request_param=request_param,
                    containment=containment, attr=attr,
                    renderer=renderer, wrapper=wrapper, xhr=xhr, accept=accept,
                    header=header, path_info=path_info, custom_predicates=(),
                    context=context, _info=u''
                    )
                view_info = deferred_views.setdefault(route_name, [])
                view_info.append(info)
                return

        score, predicates = _make_predicates(
            xhr=xhr, request_method=request_method, path_info=path_info,
            request_param=request_param, header=header, accept=accept,
            containment=containment, request_type=request_type,
            custom=custom_predicates)

        derived_view = self._derive_view(view, permission, predicates, attr,
                                         renderer, wrapper, name, accept, score)

        if context is None:
            context = for_

        r_context = context
        if r_context is None:
            r_context = Interface
        if not IInterface.providedBy(r_context):
            r_context = implementedBy(r_context)

        registered = self.registry.adapters.registered

        # A multiviews is a set of views which are registered for
        # exactly the same context type/request type/name triad.  Each
        # consituent view in a multiview differs only by the
        # predicates which it possesses.

        # To find a previously registered view for a context
        # type/request type/name triad, we need to use the
        # ``registered`` method of the adapter registry rather than
        # ``lookup``.  ``registered`` ignores interface inheritance
        # for the required and provided arguments, returning only a
        # view registered previously with the *exact* triad we pass
        # in.

        # We need to do this three times, because we use three
        # different interfaces as the ``provided`` interface while
        # doing registrations, and ``registered`` performs exact
        # matches on all the arguments it receives.

        old_view = None

        for view_type in (IView, ISecuredView, IMultiView):
            old_view = registered((request_iface, r_context), view_type, name)
            if old_view is not None:
                break
        
        if old_view is None:
            # No component was registered for any of our I*View
            # interfaces exactly; this is the first view for this
            # triad.  We don't need a multiview.
            if hasattr(derived_view, '__call_permissive__'):
                view_iface = ISecuredView
            else:
                view_iface = IView
            self.registry.registerAdapter(derived_view,
                                          (request_iface, context),
                                          view_iface, name, info=_info)
        else:
            # XXX we could try to be more efficient here and register
            # a non-secured view for a multiview if none of the
            # multiview's consituent views have a permission
            # associated with them, but this code is getting pretty
            # rough already
            if IMultiView.providedBy(old_view):
                multiview = old_view
            else:
                multiview = MultiView(name)
                old_accept = getattr(old_view, '__accept__', None)
                old_score = getattr(old_view, '__score__', MAX_WEIGHT)
                multiview.add(old_view, old_score, old_accept)
            multiview.add(derived_view, score, accept)
            for view_type in (IView, ISecuredView):
                # unregister any existing views
                self.registry.adapters.unregister(
                    (request_iface, r_context), view_type, name=name)
            self.registry.registerAdapter(multiview, (request_iface, context),
                                          IMultiView, name, info=_info)

    def add_route(self,
                  name,
                  path,
                  view=None,
                  view_for=None,
                  permission=None,
                  factory=None,
                  for_=None,
                  header=None,
                  xhr=False,
                  accept=None,
                  path_info=None,
                  request_method=None,
                  request_param=None,
                  custom_predicates=(),
                  view_permission=None,
                  renderer=None,
                  view_renderer=None,
                  view_context=None,
                  view_attr=None,
                  use_global_views=False,
                  _info=u''):
        """ Add a :term:`route configuration` to the current
        configuration state, as well as possibly a :term:`view
        configuration` to be used to specify a :term:`view callable`
        that will be invoked when this route matches.  The arguments
        to this method are divided into *predicate*, *non-predicate*,
        and *view-related* types.  :term:`Route predicate` arguments
        narrow the circumstances in which a route will be match a
        request; non-predicate arguments are informational.

        Non-Predicate Arguments

        name

          The name of the route, e.g. ``myroute``.  This attribute is
          required.  It must be unique among all defined routes in a given
          application.

        factory

          A reference to a Python object (often a function or a class)
          that will generate a :mod:`repoze.bfg` :term:`context`
          object when this route matches. For example,
          ``mypackage.models.MyFactoryClass``.  If this argument is
          not specified, a default root factory will be used.

        Predicate Arguments

        path

          The path of the route e.g. ``ideas/:idea``.  This argument
          is required.  See :ref:`route_path_pattern_syntax` for
          information about the syntax of route paths.  If the path
          doesn't match the current URL, route matching continues.

        xhr

          This value should be either ``True`` or ``False``.  If this
          value is specified and is ``True``, the :term:`request` must
          possess an ``HTTP_X_REQUESTED_WITH`` (aka
          ``X-Requested-With``) header for this route to match.  This
          is useful for detecting AJAX requests issued from jQuery,
          Prototype and other Javascript libraries.  If this predicate
          returns ``False``, route matching continues.

        request_method

          A string representing an HTTP method name, e.g. ``GET``,
          ``POST``, ``HEAD``, ``DELETE``, ``PUT``.  If this argument
          is not specified, this route will match if the request has
          *any* request method.  If this predicate returns ``False``,
          route matching continues.

        path_info

          This value represents a regular expression pattern that will
          be tested against the ``PATH_INFO`` WSGI environment
          variable.  If the regex matches, this predicate will return
          ``True``.  If this predicate returns ``False``, route
          matching continues.

        request_param

          This value can be any string.  A view declaration with this
          argument ensures that the associated route will only match
          when the request has a key in the ``request.params``
          dictionary (an HTTP ``GET`` or ``POST`` variable) that has a
          name which matches the supplied value.  If the value
          supplied as the argument has a ``=`` sign in it,
          e.g. ``request_params="foo=123"``, then the key
          (``foo``) must both exist in the ``request.params`` dictionary, and
          the value must match the right hand side of the expression (``123``)
          for the route to "match" the current request.  If this predicate
          returns ``False``, route matching continues.

        header

          This argument represents an HTTP header name or a header
          name/value pair.  If the argument contains a ``:`` (colon),
          it will be considered a name/value pair
          (e.g. ``User-Agent:Mozilla/.*`` or ``Host:localhost``).  If
          the value contains a colon, the value portion should be a
          regular expression.  If the value does not contain a colon,
          the entire value will be considered to be the header name
          (e.g. ``If-Modified-Since``).  If the value evaluates to a
          header name only without a value, the header specified by
          the name must be present in the request for this predicate
          to be true.  If the value evaluates to a header name/value
          pair, the header specified by the name must be present in
          the request *and* the regular expression specified as the
          value must match the header value.  Whether or not the value
          represents a header name or a header name/value pair, the
          case of the header name is not significant.  If this
          predicate returns ``False``, route matching continues.

        accept

          This value represents a match query for one or more
          mimetypes in the ``Accept`` HTTP request header.  If this
          value is specified, it must be in one of the following
          forms: a mimetype match token in the form ``text/plain``, a
          wildcard mimetype match token in the form ``text/*`` or a
          match-all wildcard mimetype match token in the form ``*/*``.
          If any of the forms matches the ``Accept`` header of the
          request, this predicate will be true.  If this predicate
          returns ``False``, route matching continues.

        custom_predicates

          This value should be a sequence of references to custom
          predicate callables.  Use custom predicates when no set of
          predefined predicates does what you need.  Custom predicates
          can be combined with predefined predicates as necessary.
          Each custom predicate callable should accept two arguments:
          ``context`` and ``request`` and should return either
          ``True`` or ``False`` after doing arbitrary evaluation of
          the context and/or the request.  If all callables return
          ``True``, the associated route will be considered viable for
          a given request.  If any custom predicate returns ``False``,
          route matching continues.  Note that the value ``context``
          will always be ``None`` when passed to a custom route
          predicate.

          .. note:: This feature is new as of :mod:`repoze.bfg` 1.2.

        View-Related Arguments

        view

          A reference to a Python object that will be used as a view
          callable when this route
          matches. e.g. ``mypackage.views.my_view``.
          
        view_context

          A reference to a class or an :term:`interface` that the
          :term:`context` of the view should match for the view named
          by the route to be used.  This argument is only useful if
          the ``view`` attribute is used.  If this attribute is not
          specified, the default (``None``) will be used.

          If the ``view`` argument is not provided, this argument has
          no effect.

          This attribute can also be spelled as ``for_`` or ``view_for``.

        view_permission

          The permission name required to invoke the view associated
          with this route.  e.g. ``edit``. (see
          :ref:`using_security_with_urldispatch` for more information
          about permissions).

          If the ``view`` attribute is not provided, this argument has
          no effect.

          This argument can also be spelled as ``permission``.

        view_renderer

          This is either a single string term (e.g. ``json``) or a
          string implying a path or :term:`resource specification`
          (e.g. ``templates/views.pt``).  If the renderer value is a
          single term (does not contain a dot ``.``), the specified
          term will be used to look up a renderer implementation, and
          that renderer implementation will be used to construct a
          response from the view return value.  If the renderer term
          contains a dot (``.``), the specified term will be treated
          as a path, and the filename extension of the last element in
          the path will be used to look up the renderer
          implementation, which will be passed the full path.  The
          renderer implementation will be used to construct a response
          from the view return value.  See
          :ref:`views_which_use_a_renderer` for more information.

          If the ``view`` argument is not provided, this argument has
          no effect.

          This argument can also be spelled as ``renderer``.

        view_attr

          The view machinery defaults to using the ``__call__`` method
          of the view callable (or the function itself, if the view
          callable is a function) to obtain a response dictionary.
          The ``attr`` value allows you to vary the method attribute
          used to obtain the response.  For example, if your view was
          a class, and the class has a method named ``index`` and you
          wanted to use this method instead of the class' ``__call__``
          method to return the response, you'd say ``attr="index"`` in
          the view configuration for the view.  This is
          most useful when the view definition is a class.

          If the ``view`` argument is not provided, this argument has no
          effect.

        use_global_views

          When a request matches this route, and view lookup cannot
          find a view which has a ``route_name`` predicate argument
          that matches the route, try to fall back to using a view
          that otherwise matches the context, request, and view name
          (but which does not match the route_name predicate).

          .. note:: This feature is new as of :mod:`repoze.bfg` 1.2.

        """
        # these are route predicates; if they do not match, the next route
        # in the routelist will be tried
        _, predicates = _make_predicates(xhr=xhr,
                                         request_method=request_method,
                                         path_info=path_info,
                                         request_param=request_param,
                                         header=header,
                                         accept=accept,
                                         custom=custom_predicates)
        

        request_iface = self.registry.queryUtility(IRouteRequest, name=name)
        if request_iface is None:
            bases = use_global_views and (IRequest,) or ()
            request_iface = route_request_iface(name, bases)
            self.registry.registerUtility(
                request_iface, IRouteRequest, name=name)
            deferred_views = getattr(self.registry, 'deferred_route_views', {})
            view_info = deferred_views.pop(name, ())
            for info in view_info:
                self.add_view(**info)

        if view:
            if view_context is None:
                view_context = view_for
                if view_context is None:
                    view_context = for_
            view_permission = view_permission or permission
            view_renderer = view_renderer or renderer
            self.add_view(
                permission=view_permission,
                context=view_context,
                view=view,
                name='',
                route_name=name, 
                renderer=view_renderer,
                attr=view_attr,
                _info=_info,
                )

        mapper = self.registry.queryUtility(IRoutesMapper)
        if mapper is None:
            mapper = RoutesMapper()
            self.registry.registerUtility(mapper, IRoutesMapper)
        mapper.connect(path, name, factory, predicates=predicates)

    def scan(self, package=None, _info=u''):
        """ Scan a Python package and any of its subpackages for
        objects marked with :term:`configuration decoration` such as
        :class:`repoze.bfg.view.bfg_view`.  Any decorated object found
        will influence the current configuration state.

        The ``package`` argument should be a reference to a Python
        :term:`package` or module object.  If ``package`` is ``None``,
        the package of the *caller* is used.
        """
        if package is None: # pragma: no cover
            package = caller_package()

        def register_decorations(name, ob):
            settings = getattr(ob, '__bfg_view_settings__', None)
            if settings is not None:
                for setting in settings:
                    self.add_view(view=ob, _info=_info, **setting)
            
        for name, ob in inspect.getmembers(package):
            register_decorations(name, ob)

        if hasattr(package, '__path__'): # package, not module
            results = walk_packages(package.__path__, package.__name__+'.')

            for importer, modname, ispkg in results:
                __import__(modname)
                module = sys.modules[modname]
                for name, ob in inspect.getmembers(module, None):
                    register_decorations(name, ob)

    def add_renderer(self, name, factory, _info=u''):
        """ Add a :mod:`repoze.bfg` :term:`renderer` factory to the current
        configuration state.

        The ``name`` argument is the renderer name.

        The ``factory`` argument is Python reference to an
        implementation of a :term:`renderer` factory.

        Note that this function must be called *before* any
        ``add_view`` invocation that names the renderer name as an
        argument.  As a result, it's usually a better idea to pass
        globally used renderers into the ``Configurator`` constructor
        in the sequence of renderers passed as ``renderer`` than it is
        to use this method.
        """
        self.registry.registerUtility(
            factory, IRendererFactory, name=name, info=_info)

    def override_resource(self, to_override, override_with,
                          _info=u'', _override=None,):
        """ Add a :mod:`repoze.bfg` resource override to the current
        configuration state.

        ``to_override`` is a :term:`resource specification` to the
        resource being overridden.

        ``override_with`` is a :term:`resource specification` to the
        resource that is performing the override.

        See :ref:`resources_chapter` for more
        information about resource overrides."""
        if to_override == override_with:
            raise ConfigurationError('You cannot override a resource with '
                                     'itself')

        package = to_override
        path = ''
        if ':' in to_override:
            package, path = to_override.split(':', 1)

        override_package = override_with
        override_prefix = ''
        if ':' in override_with:
            override_package, override_prefix = override_with.split(':', 1)

        if path and path.endswith('/'):
            if override_prefix and (not override_prefix.endswith('/')):
                raise ConfigurationError(
                    'A directory cannot be overridden with a file (put a slash '
                    'at the end of override_with if necessary)')

        if override_prefix and override_prefix.endswith('/'):
            if path and (not path.endswith('/')):
                raise ConfigurationError(
                    'A file cannot be overridden with a directory (put a slash '
                    'at the end of to_override if necessary)')

        __import__(package)
        __import__(override_package)
        package = sys.modules[package]
        override_package = sys.modules[override_package]

        override = _override or self._override # test jig
        override(package, path, override_package, override_prefix,
                 _info=_info)

    def set_forbidden_view(self, *arg, **kw):
        """ Add a default forbidden view to the current configuration
        state.

        The ``view`` argument should be a :term:`view callable`.

        The ``attr`` argument should be the attribute of the view
        callable used to retrieve the response (see the ``add_view``
        method's ``attr`` argument for a description).

        The ``renderer`` argument should be the name of (or path to) a
        :term:`renderer` used to generate a response for this view
        (see the
        :meth:`repoze.bfg.configuration.Configurator.add_view`
        method's ``renderer`` argument for information about how a
        configurator relates to a renderer).

        The ``wrapper`` argument should be the name of another view
        which will wrap this view when rendered (see the ``add_view``
        method's ``wrapper`` argument for a description).

        See :ref:`changing_the_forbidden_view` for more
        information."""
        return self._system_view(IForbiddenView, *arg, **kw)

    def set_notfound_view(self, *arg, **kw):
        """ Add a default not found view to the current configuration
        state.

        The ``view`` argument should be a :term:`view callable`.

        The ``attr`` argument should be the attribute of the view
        callable used to retrieve the response (see the ``add_view``
        method's ``attr`` argument for a description).

        The ``renderer`` argument should be the name of (or path to) a
        :term:`renderer` used to generate a response for this view
        (see the
        :meth:`repoze.bfg.configuration.Configurator.add_view`
        method's ``renderer`` argument for information about how a
        configurator relates to a renderer).

        The ``wrapper`` argument should be the name of another view
        which will wrap this view when rendered (see the ``add_view``
        method's ``wrapper`` argument for a description).

        See :ref:`changing_the_notfound_view` for more
        information.
        """
        return self._system_view(INotFoundView, *arg, **kw)

    def add_static_view(self, name, path, cache_max_age=3600, _info=u''):
        """ Add a view used to render static resources to the current
        configuration state.

        The ``name`` argument is a string representing :term:`view
        name` of the view which is registered.

        The ``path`` argument is the path on disk where the static
        files reside.  This can be an absolute path, a
        package-relative path, or a :term:`resource specification`.

        See :ref:`static_resources_section` for more information.
        """
        spec = self._make_spec(path)
        view = static(spec, cache_max_age=cache_max_age)
        self.add_route(name, "%s*subpath" % name, view=view,
                       view_for=StaticRootFactory,
                       factory=StaticRootFactory(spec),
                       _info=_info)
    # testing API

    def testing_securitypolicy(self, userid=None, groupids=(),
                               permissive=True):
        """Unit/integration testing helper: Registers a pair of faux
        :mod:`repoze.bfg` security policies: a :term:`authentication
        policy` and a :term:`authorization policy`.

        The behavior of the registered :term:`authorization policy`
        depends on the ``permissive`` argument.  If ``permissive`` is
        true, a permissive :term:`authorization policy` is registered;
        this policy allows all access.  If ``permissive`` is false, a
        nonpermissive :term:`authorization policy` is registered; this
        policy denies all access.

        The behavior of the registered :term:`authentication policy`
        depends on the values provided for the ``userid`` and
        ``groupids`` argument.  The authentication policy will return
        the userid identifier implied by the ``userid`` argument and
        the group ids implied by the ``groupids`` argument when the
        :func:`repoze.bfg.security.authenticated_userid` or
        :func:`repoze.bfg.security.effective_principals` APIs are
        used.

        This function is most useful when testing code that uses
        the APIs named :func:`repoze.bfg.security.has_permission`,
        :func:`repoze.bfg.security.authenticated_userid`,
        :func:`repoze.bfg.security.effective_principals`, and
        :func:`repoze.bfg.security.principals_allowed_by_permission`.
        """
        from repoze.bfg.testing import DummySecurityPolicy
        policy = DummySecurityPolicy(userid, groupids, permissive)
        self.registry.registerUtility(policy, IAuthorizationPolicy)
        self.registry.registerUtility(policy, IAuthenticationPolicy)

    def testing_models(self, models):
        """Unit/integration testing helper: registers a dictionary of
        :term:`model` objects that can be resolved via the
        :func:`repoze.bfg.traversal.find_model` API.

        The :func:`repoze.bfg.traversal.find_model` API is called with
        a path as one of its arguments.  If the dictionary you
        register when calling this method contains that path as a
        string key (e.g. ``/foo/bar`` or ``foo/bar``), the
        corresponding value will be returned to ``find_model`` (and
        thus to your code) when
        :func:`repoze.bfg.traversal.find_model` is called with an
        equivalent path string or tuple.
        """
        class DummyTraverserFactory:
            def __init__(self, context):
                self.context = context

            def __call__(self, request):
                path = request['PATH_INFO']
                ob = models[path]
                traversed = traversal_path(path)
                return {'context':ob, 'view_name':'','subpath':(),
                        'traversed':traversed, 'virtual_root':ob,
                        'virtual_root_path':(), 'root':ob}
        self.registry.registerAdapter(DummyTraverserFactory, (Interface,),
                                      ITraverser)
        return models

    def testing_add_subscriber(self, event_iface=None):
        """Unit/integration testing helper: Registers a
        :term:`subscriber` which listens for events of the type
        ``event_iface``.  This method returns a list object which is
        appended to by the subscriber whenever an event is captured.

        When an event is dispatched that matches the value implied by
        the ``event_iface`` argument, that event will be appended to
        the list.  You can then compare the values in the list to
        expected event notifications.  This method is useful when
        testing code that wants to call
        :meth:`repoze.bfg.registry.Registry.notify`,
        :func:`zope.component.event.dispatch` or
        :func:`zope.component.event.objectEventNotify`.

        The default value of ``event_iface`` (``None``) implies a
        subscriber registered for *any* kind of event.
        """
        L = []
        def subscriber(*event):
            L.extend(event)
        self.add_subscriber(subscriber, event_iface)
        return L

    def testing_add_template(self, path, renderer=None):
        """Unit/integration testing helper: register a template
        renderer at ``path`` (usually a relative filename ala
        ``templates/foo.pt``) and return the renderer object.  If the
        ``renderer`` argument is None, a 'dummy' renderer will be
        used.  This function is useful when testing code that calls
        the
        :func:`repoze.bfg.chameleon_zpt.render_template_to_response`
        function or
        :func:`repoze.bfg.chameleon_text.render_template_to_response`
        function or any other ``render_template*`` API of any built-in
        templating system (see :mod:`repoze.bfg.chameleon_zpt` and
        :mod:`repoze.bfg.chameleon_text`).
        """
        from repoze.bfg.testing import DummyTemplateRenderer
        if renderer is None:
            renderer = DummyTemplateRenderer()
        self.registry.registerUtility(renderer, ITemplateRenderer, path)
        return renderer

def _make_predicates(xhr=None, request_method=None, path_info=None,
                     request_param=None, header=None, accept=None,
                     containment=None, request_type=None, custom=()):
    # Predicates are added to the predicate list in (presumed)
    # computation expense order.  All predicates associated with a
    # view must evaluate true for the view to "match" a request.
    # Elsewhere in the code, we evaluate them using a generator
    # expression.  The fastest predicate should be evaluated first,
    # then the next fastest, and so on, as if one returns false, the
    # remainder of the predicates won't need to be evaluated.

    # Each predicate is associated with a weight value.  The weight
    # symbolizes the relative potential "importance" of the predicate
    # to all other predicates.  A larger weight indicates greater
    # importance.  These weights are subtracted from an aggregate
    # 'weight' variable.  The aggregate weight is then divided by the
    # length of the predicate list to compute a "score" for this view.
    # The score represents the ordering in which a "multiview" ( a
    # collection of views that share the same context/request/name
    # triad but differ in other ways via predicates) will attempt to
    # call its set of views.  Views with lower scores will be tried
    # first.  The intent is to a) ensure that views with more
    # predicates are always evaluated before views with fewer
    # predicates and b) to ensure a stable call ordering of views that
    # share the same number of predicates.

    # Views which do not have any predicates get a score of
    # MAX_WEIGHT, meaning that they will be tried very last.

    predicates = []
    weight = MAX_WEIGHT

    if xhr:
        def xhr_predicate(context, request):
            return request.is_xhr
        weight = weight - 20
        predicates.append(xhr_predicate)

    if request_method is not None:
        def request_method_predicate(context, request):
            return request.method == request_method
        weight = weight - 30
        predicates.append(request_method_predicate)

    if path_info is not None:
        try:
            path_info_val = re.compile(path_info)
        except re.error, why:
            raise ConfigurationError(why[0])
        def path_info_predicate(context, request):
            return path_info_val.match(request.path_info) is not None
        weight = weight - 40
        predicates.append(path_info_predicate)

    if request_param is not None:
        request_param_val = None
        if '=' in request_param:
            request_param, request_param_val = request_param.split('=', 1)
        def request_param_predicate(context, request):
            if request_param_val is None:
                return request_param in request.params
            return request.params.get(request_param) == request_param_val
        weight = weight - 50
        predicates.append(request_param_predicate)

    if header is not None:
        header_name = header
        header_val = None
        if ':' in header:
            header_name, header_val = header.split(':', 1)
            try:
                header_val = re.compile(header_val)
            except re.error, why:
                raise ConfigurationError(why[0])
        def header_predicate(context, request):
            if header_val is None:
                return header_name in request.headers
            val = request.headers.get(header_name)
            return header_val.match(val) is not None
        weight = weight - 60
        predicates.append(header_predicate)

    if accept is not None:
        def accept_predicate(context, request):
            return accept in request.accept
        weight = weight - 70
        predicates.append(accept_predicate)

    if containment is not None:
        def containment_predicate(context, request):
            return find_interface(context, containment) is not None
        weight = weight - 80
        predicates.append(containment_predicate)

    if request_type is not None:
        def request_type_predicate(context, request):
            return request_type.providedBy(request)
        weight = weight - 90
        predicates.append(request_type_predicate)

    if custom:
        for predicate in custom:
            weight = weight - 100
            predicates.append(predicate)

    # this will be == MAX_WEIGHT if no predicates
    score = weight / (len(predicates) + 1)
    return score, predicates

class MultiView(object):
    implements(IMultiView)

    def __init__(self, name):
        self.name = name
        self.media_views = {}
        self.views = []
        self.accepts = []

    def add(self, view, score, accept=None):
        if accept is None or '*' in accept:
            self.views.append((score, view))
            self.views.sort()
        else:
            subset = self.media_views.setdefault(accept, [])
            subset.append((score, view))
            subset.sort()
            accepts = set(self.accepts)
            accepts.add(accept)
            self.accepts = list(accepts) # dedupe

    def get_views(self, request):
        if self.accepts and hasattr(request, 'accept'):
            accepts = self.accepts[:]
            views = []
            while accepts:
                match = request.accept.best_match(accepts)
                if match is None:
                    break
                subset = self.media_views[match]
                views.extend(subset)
                accepts.remove(match)
            views.extend(self.views)
            return views
        return self.views

    def match(self, context, request):
        for score, view in self.get_views(request):
            if not hasattr(view, '__predicated__'):
                return view
            if view.__predicated__(context, request):
                return view
        raise NotFound(self.name)

    def __permitted__(self, context, request):
        view = self.match(context, request)
        if hasattr(view, '__permitted__'):
            return view.__permitted__(context, request)
        return True

    def __call_permissive__(self, context, request):
        view = self.match(context, request)
        view = getattr(view, '__call_permissive__', view)
        return view(context, request)

    def __call__(self, context, request):
        for score, view in self.get_views(request):
            try:
                return view(context, request)
            except NotFound:
                continue
        raise NotFound(self.name)

def decorate_view(wrapped_view, original_view):
    if wrapped_view is original_view:
        return False
    wrapped_view.__module__ = original_view.__module__
    wrapped_view.__doc__ = original_view.__doc__
    try:
        wrapped_view.__name__ = original_view.__name__
    except AttributeError:
        wrapped_view.__name__ = repr(original_view)
    try:
        wrapped_view.__permitted__ = original_view.__permitted__
    except AttributeError:
        pass
    try:
        wrapped_view.__call_permissive__ = original_view.__call_permissive__
    except AttributeError:
        pass
    try:
        wrapped_view.__predicated__ = original_view.__predicated__
    except AttributeError:
        pass
    try:
        wrapped_view.__accept__ = original_view.__accept__
    except AttributeError:
        pass
    try:
        wrapped_view.__score__ = original_view.__score__
    except AttributeError:
        pass
    return True

def rendered_response(renderer, response, view, context, request,
                      renderer_name):
    if ( hasattr(response, 'app_iter') and hasattr(response, 'headerlist')
         and hasattr(response, 'status') ):
        return response
    result = renderer(response, {'view':view, 'renderer_name':renderer_name,
                                 'context':context, 'request':request})
    response_factory = Response
    reg = getattr(request, 'registry', None)
    if reg is not None:
        # be kind to old unit tests
        response_factory = reg.queryUtility(IResponseFactory, default=Response)
    response = response_factory(result)
    if request is not None: # in tests, it may be None
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

def requestonly(class_or_callable, attr=None):
    """ Return true of the class or callable accepts only a request argument,
    as opposed to something that accepts context, request """
    if attr is None:
        attr = '__call__'
    if inspect.isfunction(class_or_callable):
        fn = class_or_callable
    elif inspect.isclass(class_or_callable):
        try:
            fn = class_or_callable.__init__
        except AttributeError:
            return False
    else:
        try:
            fn = getattr(class_or_callable, attr)
        except AttributeError:
            return False

    try:
        argspec = inspect.getargspec(fn)
    except TypeError:
        return False

    args = argspec[0]
    defaults = argspec[3]

    if hasattr(fn, 'im_func'):
        # it's an instance method
        if not args:
            return False
        args = args[1:]
    if not args:
        return False

    if len(args) == 1:
        return True

    elif args[0] == 'request':
        if len(args) - len(defaults) == 1:
            return True

    return False

def _map_view(view, attr=None, renderer=None, renderer_name=None):
    wrapped_view = view

    if inspect.isclass(view):
        # If the object we've located is a class, turn it into a
        # function that operates like a Zope view (when it's invoked,
        # construct an instance using 'context' and 'request' as
        # position arguments, then immediately invoke the __call__
        # method of the instance with no arguments; __call__ should
        # return an IResponse).
        if requestonly(view, attr):
            # its __init__ accepts only a single request argument,
            # instead of both context and request
            def _bfg_class_requestonly_view(context, request):
                inst = view(request)
                if attr is None:
                    response = inst()
                else:
                    response = getattr(inst, attr)()
                if renderer is not None:
                    response = rendered_response(renderer, 
                                                 response, inst,
                                                 context, request,
                                                 renderer_name)
                return response
            wrapped_view = _bfg_class_requestonly_view
        else:
            # its __init__ accepts both context and request
            def _bfg_class_view(context, request):
                inst = view(context, request)
                if attr is None:
                    response = inst()
                else:
                    response = getattr(inst, attr)()
                if renderer is not None:
                    response = rendered_response(renderer, 
                                                 response, inst,
                                                 context, request,
                                                 renderer_name)
                return response
            wrapped_view = _bfg_class_view

    elif requestonly(view, attr):
        # its __call__ accepts only a single request argument,
        # instead of both context and request
        def _bfg_requestonly_view(context, request):
            if attr is None:
                response = view(request)
            else:
                response = getattr(view, attr)(request)

            if renderer is not None:
                response = rendered_response(renderer,
                                             response, view,
                                             context, request,
                                             renderer_name)
            return response
        wrapped_view = _bfg_requestonly_view

    elif attr:
        def _bfg_attr_view(context, request):
            response = getattr(view, attr)(context, request)
            if renderer is not None:
                response = rendered_response(renderer, 
                                             response, view,
                                             context, request,
                                             renderer_name)
            return response
        wrapped_view = _bfg_attr_view

    elif renderer is not None:
        def _rendered_view(context, request):
            response = view(context, request)
            response = rendered_response(renderer, 
                                         response, view,
                                         context, request,
                                         renderer_name)
            return response
        wrapped_view = _rendered_view

    decorate_view(wrapped_view, view)
    return wrapped_view

def _owrap_view(view, viewname, wrapper_viewname):
    if not wrapper_viewname:
        return view
    def _owrapped_view(context, request):
        response = view(context, request)
        request.wrapped_response = response
        request.wrapped_body = response.body
        request.wrapped_view = view
        wrapped_response = render_view_to_response(context, request,
                                                   wrapper_viewname)
        if wrapped_response is None:
            raise ValueError(
                'No wrapper view named %r found when executing view '
                'named %r' % (wrapper_viewname, viewname))
        return wrapped_response
    decorate_view(_owrapped_view, view)
    return _owrapped_view

def _predicate_wrap(view, predicates):
    if not predicates:
        return view
    def predicate_wrapper(context, request):
        if all((predicate(context, request) for predicate in predicates)):
            return view(context, request)
        raise NotFound('predicate mismatch for view %s' % view)
    def checker(context, request):
        return all((predicate(context, request) for predicate in
                    predicates))
    predicate_wrapper.__predicated__ = checker
    decorate_view(predicate_wrapper, view)
    return predicate_wrapper

def _secure_view(view, permission, authn_policy, authz_policy):
    wrapped_view = view
    if authn_policy and authz_policy and (permission is not None):
        def _secured_view(context, request):
            principals = authn_policy.effective_principals(request)
            if authz_policy.permits(context, principals, permission):
                return view(context, request)
            msg = getattr(request, 'authdebug_message',
                          'Unauthorized: %s failed permission check' % view)
            raise Forbidden(msg)
        _secured_view.__call_permissive__ = view
        def _permitted(context, request):
            principals = authn_policy.effective_principals(request)
            return authz_policy.permits(context, principals, permission)
        _secured_view.__permitted__ = _permitted
        wrapped_view = _secured_view
        decorate_view(wrapped_view, view)

    return wrapped_view

def _authdebug_view(view, permission, authn_policy, authz_policy, settings,
                    logger):
    wrapped_view = view
    if settings and settings.get('debug_authorization', False):
        def _authdebug_view(context, request):
            view_name = getattr(request, 'view_name', None)

            if authn_policy and authz_policy:
                if permission is None:
                    msg = 'Allowed (no permission registered)'
                else:
                    principals = authn_policy.effective_principals(request)
                    msg = str(authz_policy.permits(context, principals,
                                                   permission))
            else:
                msg = 'Allowed (no authorization policy in use)'

            view_name = getattr(request, 'view_name', None)
            url = getattr(request, 'url', None)
            msg = ('debug_authorization of url %s (view name %r against '
                   'context %r): %s' % (url, view_name, context, msg))
            logger and logger.debug(msg)
            if request is not None:
                request.authdebug_message = msg
            return view(context, request)

        wrapped_view = _authdebug_view
        decorate_view(wrapped_view, view)

    return wrapped_view

def _attr_wrap(view, accept, score):
    # this is a little silly but we don't want to decorate the original
    # function with attributes that indicate accept and score,
    # so we use a wrapper
    if (accept is None) and (score == MAX_WEIGHT):
        return view # defaults
    def attr_view(context, request):
        return view(context, request)
    attr_view.__accept__ = accept
    attr_view.__score__ = score
    decorate_view(attr_view, view)
    return attr_view

# note that ``options`` is a b/w compat alias for ``settings`` and
# ``Configurator`` is a testing dep inj
def make_app(root_factory, package=None, filename='configure.zcml',
             settings=None, options=None, Configurator=Configurator):
    """ Return a Router object, representing a fully configured
    :mod:`repoze.bfg` WSGI application.

    .. warning:: Use of this function is deprecated as of
       :mod:`repoze.bfg` 1.2.  You should instead use a
       :class:`repoze.bfg.configuration.Configurator` instance to
       perform startup configuration as shown in
       :ref:`configuration_narr`.

    ``root_factory`` must be a callable that accepts a :term:`request`
    object and which returns a traversal root object.  The traversal
    root returned by the root factory is the *default* traversal root;
    it can be overridden on a per-view basis.  ``root_factory`` may be
    ``None``, in which case a 'default default' traversal root is
    used.

    ``package`` is a Python :term:`package` or module representing the
    application's package.  It is optional, defaulting to ``None``.
    ``package`` may be ``None``.  If ``package`` is ``None``, the
    ``filename`` passed or the value in the ``options`` dictionary
    named ``configure_zcml`` must be a) absolute pathname to a
    :term:`ZCML` file that represents the application's configuration
    *or* b) a :term:`resource specification` to a :term:`ZCML` file in
    the form ``dotted.package.name:relative/file/path.zcml``.

    ``filename`` is the filesystem path to a ZCML file (optionally
    relative to the package path) that should be parsed to create the
    application registry.  It defaults to ``configure.zcml``.  It can
    also be a ;term:`resource specification` in the form
    ``dotted_package_name:relative/file/path.zcml``. Note that if any
    value for ``configure_zcml`` is passed within the ``settings``
    dictionary, the value passed as ``filename`` will be ignored,
    replaced with the ``configure_zcml`` value.

    ``settings``, if used, should be a dictionary containing runtime
    settings (e.g. the key/value pairs in an app section of a
    PasteDeploy file), with each key representing the option and the
    key's value representing the specific option value,
    e.g. ``{'reload_templates':True}``.  Note that the keyword
    parameter ``options`` is a backwards compatibility alias for the
    ``settings`` keyword parameter.
    """
    settings = settings or options or {}
    zcml_file = settings.get('configure_zcml', filename)
    config = Configurator(package=package, settings=settings,
                          root_factory=root_factory)
    config.hook_zca()
    config.begin()
    config.load_zcml(zcml_file)
    config.end()
    return config.make_wsgi_app()

