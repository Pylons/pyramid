import inspect
import logging
import os
import sys
import types
import warnings
import venusian

from webob.exc import WSGIHTTPException as WebobWSGIHTTPException

from pyramid.interfaces import IDebugLogger
from pyramid.interfaces import IExceptionResponse

from pyramid.asset import resolve_asset_spec
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.events import ApplicationCreated
from pyramid.exceptions import ConfigurationConflictError
from pyramid.exceptions import ConfigurationError
from pyramid.exceptions import ConfigurationExecutionError
from pyramid.httpexceptions import default_exceptionresponse_view
from pyramid.path import caller_package
from pyramid.path import package_of
from pyramid.registry import Registry
from pyramid.router import Router
from pyramid.settings import aslist
from pyramid.threadlocal import manager
from pyramid.util import DottedNameResolver
from pyramid.util import WeakOrderedSet

from pyramid.config.adapters import AdaptersConfiguratorMixin
from pyramid.config.assets import AssetsConfiguratorMixin
from pyramid.config.factories import FactoriesConfiguratorMixin
from pyramid.config.i18n import I18NConfiguratorMixin
from pyramid.config.rendering import DEFAULT_RENDERERS
from pyramid.config.rendering import RenderingConfiguratorMixin
from pyramid.config.routes import RoutesConfiguratorMixin
from pyramid.config.security import SecurityConfiguratorMixin
from pyramid.config.settings import SettingsConfiguratorMixin
from pyramid.config.testing import TestingConfiguratorMixin
from pyramid.config.tweens import TweensConfiguratorMixin
from pyramid.config.util import action_method
from pyramid.config.views import ViewsConfiguratorMixin
from pyramid.config.zca import ZCAConfiguratorMixin

ConfigurationError = ConfigurationError # pyflakes

class Configurator(
    TestingConfiguratorMixin,
    TweensConfiguratorMixin,
    SecurityConfiguratorMixin,
    ViewsConfiguratorMixin,
    RoutesConfiguratorMixin,
    ZCAConfiguratorMixin,
    I18NConfiguratorMixin,
    RenderingConfiguratorMixin,
    AssetsConfiguratorMixin,
    SettingsConfiguratorMixin,
    FactoriesConfiguratorMixin,
    AdaptersConfiguratorMixin,
    ):
    """
    A Configurator is used to configure a :app:`Pyramid`
    :term:`application registry`.

    The Configurator accepts a number of arguments: ``registry``,
    ``package``, ``settings``, ``root_factory``, ``authentication_policy``,
    ``authorization_policy``, ``renderers``, ``debug_logger``,
    ``locale_negotiator``, ``request_factory``, ``renderer_globals_factory``,
    ``default_permission``, ``session_factory``, ``default_view_mapper``,
    ``autocommit``, ``exceptionresponse_view`` and ``route_prefix``.

    If the ``registry`` argument is passed as a non-``None`` value, it must
    be an instance of the :class:`pyramid.registry.Registry` class
    representing the registry to configure.  If ``registry`` is ``None``, the
    configurator will create a :class:`pyramid.registry.Registry` instance
    itself; it will also perform some default configuration that would not
    otherwise be done.  After its construction, the configurator may be used
    to add further configuration to the registry.

    .. warning:: If a ``registry`` is passed to the Configurator
       constructor, all other constructor arguments except ``package``
       are ignored.

    If the ``package`` argument is passed, it must be a reference to a Python
    :term:`package` (e.g. ``sys.modules['thepackage']``) or a :term:`dotted
    Python name` to the same.  This value is used as a basis to convert
    relative paths passed to various configuration methods, such as methods
    which accept a ``renderer`` argument, into absolute paths.  If ``None``
    is passed (the default), the package is assumed to be the Python package
    in which the *caller* of the ``Configurator`` constructor lives.

    If the ``settings`` argument is passed, it should be a Python dictionary
    representing the :term:`deployment settings` for this application.  These
    are later retrievable using the
    :attr:`pyramid.registry.Registry.settings` attribute (aka
    ``request.registry.settings``).

    If the ``root_factory`` argument is passed, it should be an object
    representing the default :term:`root factory` for your application or a
    :term:`dotted Python name` to the same.  If it is ``None``, a default
    root factory will be used.

    If ``authentication_policy`` is passed, it should be an instance
    of an :term:`authentication policy` or a :term:`dotted Python
    name` to the same.

    If ``authorization_policy`` is passed, it should be an instance of
    an :term:`authorization policy` or a :term:`dotted Python name` to
    the same.

    .. note:: A ``ConfigurationError`` will be raised when an
       authorization policy is supplied without also supplying an
       authentication policy (authorization requires authentication).

    If ``renderers`` is passed, it should be a list of tuples
    representing a set of :term:`renderer` factories which should be
    configured into this application (each tuple representing a set of
    positional values that should be passed to
    :meth:`pyramid.config.Configurator.add_renderer`).  If
    it is not passed, a default set of renderer factories is used.

    If ``debug_logger`` is not passed, a default debug logger that logs to a
    logger will be used (the logger name will be the package name of the
    *caller* of this configurator).  If it is passed, it should be an
    instance of the :class:`logging.Logger` (PEP 282) standard library class
    or a Python logger name.  The debug logger is used by :app:`Pyramid`
    itself to log warnings and authorization debugging information.

    If ``locale_negotiator`` is passed, it should be a :term:`locale
    negotiator` implementation or a :term:`dotted Python name` to
    same.  See :ref:`custom_locale_negotiator`.

    If ``request_factory`` is passed, it should be a :term:`request
    factory` implementation or a :term:`dotted Python name` to the same.
    See :ref:`changing_the_request_factory`.  By default it is ``None``,
    which means use the default request factory.

    If ``renderer_globals_factory`` is passed, it should be a :term:`renderer
    globals` factory implementation or a :term:`dotted Python name` to the
    same.  See :ref:`adding_renderer_globals`.  By default, it is ``None``,
    which means use no renderer globals factory.

    .. warning::

       as of Pyramid 1.1, ``renderer_globals_factory`` is deprecated.  Instead,
       use a BeforeRender event subscriber as per :ref:`beforerender_event`.

    If ``default_permission`` is passed, it should be a
    :term:`permission` string to be used as the default permission for
    all view configuration registrations performed against this
    Configurator.  An example of a permission string:``'view'``.
    Adding a default permission makes it unnecessary to protect each
    view configuration with an explicit permission, unless your
    application policy requires some exception for a particular view.
    By default, ``default_permission`` is ``None``, meaning that view
    configurations which do not explicitly declare a permission will
    always be executable by entirely anonymous users (any
    authorization policy in effect is ignored).  See also
    :ref:`setting_a_default_permission`.

    If ``session_factory`` is passed, it should be an object which
    implements the :term:`session factory` interface.  If a nondefault
    value is passed, the ``session_factory`` will be used to create a
    session object when ``request.session`` is accessed.  Note that
    the same outcome can be achieved by calling
    :meth:`pyramid.config.Configurator.set_session_factory`.  By
    default, this argument is ``None``, indicating that no session
    factory will be configured (and thus accessing ``request.session``
    will throw an error) unless ``set_session_factory`` is called later
    during configuration.

    If ``autocommit`` is ``True``, every method called on the configurator
    will cause an immediate action, and no configuration conflict detection
    will be used. If ``autocommit`` is ``False``, most methods of the
    configurator will defer their action until
    :meth:`pyramid.config.Configurator.commit` is called.  When
    :meth:`pyramid.config.Configurator.commit` is called, the actions implied
    by the called methods will be checked for configuration conflicts unless
    ``autocommit`` is ``True``.  If a conflict is detected a
    ``ConfigurationConflictError`` will be raised.  Calling
    :meth:`pyramid.config.Configurator.make_wsgi_app` always implies a final
    commit.

    If ``default_view_mapper`` is passed, it will be used as the default
    :term:`view mapper` factory for view configurations that don't otherwise
    specify one (see :class:`pyramid.interfaces.IViewMapperFactory`).  If a
    default_view_mapper is not passed, a superdefault view mapper will be
    used.

    If ``exceptionresponse_view`` is passed, it must be a :term:`view
    callable` or ``None``.  If it is a view callable, it will be used as an
    exception view callable when an :term:`exception response` is raised. If
    ``exceptionresponse_view`` is ``None``, no exception response view will
    be registered, and all raised exception responses will be bubbled up to
    Pyramid's caller.  By
    default, the ``pyramid.httpexceptions.default_exceptionresponse_view``
    function is used as the ``exceptionresponse_view``.  This argument is new
    in Pyramid 1.1.

    If ``route_prefix`` is passed, all routes added with
    :meth:`pyramid.config.Configurator.add_route` will have the specified path
    prepended to their pattern. This parameter is new in Pyramid 1.2."""

    manager = manager # for testing injection
    venusian = venusian # for testing injection
    _ainfo = None
    basepath = None
    includepath = ()
    info = ''

    def __init__(self,
                 registry=None,
                 package=None,
                 settings=None,
                 root_factory=None,
                 authentication_policy=None,
                 authorization_policy=None,
                 renderers=None,
                 debug_logger=None,
                 locale_negotiator=None,
                 request_factory=None,
                 renderer_globals_factory=None,
                 default_permission=None,
                 session_factory=None,
                 default_view_mapper=None,
                 autocommit=False,
                 exceptionresponse_view=default_exceptionresponse_view,
                 route_prefix=None,
                 ):
        if package is None:
            package = caller_package()
        name_resolver = DottedNameResolver(package)
        self.name_resolver = name_resolver
        self.package_name = name_resolver.package_name
        self.package = name_resolver.package
        self.registry = registry
        self.autocommit = autocommit
        self.route_prefix = route_prefix
        if registry is None:
            registry = Registry(self.package_name)
            self.registry = registry
            self.setup_registry(
                settings=settings,
                root_factory=root_factory,
                authentication_policy=authentication_policy,
                authorization_policy=authorization_policy,
                renderers=renderers,
                debug_logger=debug_logger,
                locale_negotiator=locale_negotiator,
                request_factory=request_factory,
                renderer_globals_factory=renderer_globals_factory,
                default_permission=default_permission,
                session_factory=session_factory,
                default_view_mapper=default_view_mapper,
                exceptionresponse_view=exceptionresponse_view,
                )

    def setup_registry(self, settings=None, root_factory=None,
                       authentication_policy=None, authorization_policy=None,
                       renderers=None, debug_logger=None,
                       locale_negotiator=None, request_factory=None,
                       renderer_globals_factory=None, default_permission=None,
                       session_factory=None, default_view_mapper=None,
                       exceptionresponse_view=default_exceptionresponse_view):
        """ When you pass a non-``None`` ``registry`` argument to the
        :term:`Configurator` constructor, no initial setup is performed
        against the registry.  This is because the registry you pass in may
        have already been initialized for use under :app:`Pyramid` via a
        different configurator.  However, in some circumstances (such as when
        you want to use a global registry instead of a registry created as a
        result of the Configurator constructor), or when you want to reset
        the initial setup of a registry, you *do* want to explicitly
        initialize the registry associated with a Configurator for use under
        :app:`Pyramid`.  Use ``setup_registry`` to do this initialization.

        ``setup_registry`` configures settings, a root factory, security
        policies, renderers, a debug logger, a locale negotiator, and various
        other settings using the configurator's current registry, as per the
        descriptions in the Configurator constructor."""

        registry = self.registry

        self._fix_registry()
        self._set_settings(settings)
        self._register_response_adapters()

        if isinstance(debug_logger, basestring):
            debug_logger = logging.getLogger(debug_logger)

        if debug_logger is None:
            debug_logger = logging.getLogger(self.package_name)

        registry.registerUtility(debug_logger, IDebugLogger)

        for name, renderer in DEFAULT_RENDERERS:
            self.add_renderer(name, renderer)

        if exceptionresponse_view is not None:
            exceptionresponse_view = self.maybe_dotted(exceptionresponse_view)
            self.add_view(exceptionresponse_view, context=IExceptionResponse)
            self.add_view(exceptionresponse_view,context=WebobWSGIHTTPException)

        # commit below because:
        #
        # - the default exceptionresponse_view requires the superdefault view
        #   mapper, so we need to configure it before adding default_view_mapper
        #
        # - superdefault renderers should be overrideable without requiring
        #   the user to commit before calling config.add_renderer

        self.commit()

        # self.commit() should not be called after this point because the
        # following registrations should be treated as analogues of methods
        # called by the user after configurator construction.  Rationale:
        # user-supplied implementations should be preferred rather than
        # add-on author implementations with the help of automatic conflict
        # resolution.

        if authentication_policy and not authorization_policy:
            authorization_policy = ACLAuthorizationPolicy() # default

        if authorization_policy:
            self.set_authorization_policy(authorization_policy)

        if authentication_policy:
            self.set_authentication_policy(authentication_policy)

        if default_view_mapper is not None:
            self.set_view_mapper(default_view_mapper)

        if renderers:
            for name, renderer in renderers:
                self.add_renderer(name, renderer)

        if root_factory is not None:
            self.set_root_factory(root_factory)

        if locale_negotiator:
            self.set_locale_negotiator(locale_negotiator)

        if request_factory:
            self.set_request_factory(request_factory)

        if renderer_globals_factory:
            warnings.warn(
                'Passing ``renderer_globals_factory`` as a Configurator '
                'constructor parameter is deprecated as of Pyramid 1.1. '
                'Use a BeforeRender event subscriber as documented in the '
                '"Hooks" chapter of the Pyramid narrative documentation '
                'instead',
                DeprecationWarning,
                2)
            self.set_renderer_globals_factory(renderer_globals_factory,
                                              warn=False)
        if default_permission:
            self.set_default_permission(default_permission)

        if session_factory is not None:
            self.set_session_factory(session_factory)

        tweens   = aslist(registry.settings.get('pyramid.tweens', []))
        for factory in tweens:
            self._add_tween(factory, explicit=True)

        includes = aslist(registry.settings.get('pyramid.includes', []))
        for inc in includes:
            self.include(inc)

    def _make_spec(self, path_or_spec):
        package, filename = resolve_asset_spec(path_or_spec, self.package_name)
        if package is None:
            return filename # absolute filename
        return '%s:%s' % (package, filename)

    def _split_spec(self, path_or_spec):
        return resolve_asset_spec(path_or_spec, self.package_name)

    def _fix_registry(self):
        """ Fix up a ZCA component registry that is not a
        pyramid.registry.Registry by adding analogues of ``has_listeners``,
        ``notify``, ``queryAdapterOrSelf``, and ``registerSelfAdapter``
        through monkey-patching."""

        _registry = self.registry

        if not hasattr(_registry, 'notify'):
            def notify(*events):
                [ _ for _ in _registry.subscribers(events, None) ]
            _registry.notify = notify

        if not hasattr(_registry, 'has_listeners'):
            _registry.has_listeners = True

        if not hasattr(_registry, 'queryAdapterOrSelf'):
            def queryAdapterOrSelf(object, interface, default=None):
                if not interface.providedBy(object):
                    return _registry.queryAdapter(object, interface,
                                                  default=default)
                return object
            _registry.queryAdapterOrSelf = queryAdapterOrSelf

        if not hasattr(_registry, 'registerSelfAdapter'):
            def registerSelfAdapter(required=None, provided=None,
                                    name=u'', info=u'', event=True):
                return _registry.registerAdapter(lambda x: x,
                                                 required=required,
                                                 provided=provided, name=name,
                                                 info=info, event=event)
            _registry.registerSelfAdapter = registerSelfAdapter

    # API

    def action(self, discriminator, callable=None, args=(), kw=None, order=0):
        """ Register an action which will be executed when
        :meth:`pyramid.config.Configurator.commit` is called (or executed
        immediately if ``autocommit`` is ``True``).

        .. warning:: This method is typically only used by :app:`Pyramid`
           framework extension authors, not by :app:`Pyramid` application
           developers.

        The ``discriminator`` uniquely identifies the action.  It must be
        given, but it can be ``None``, to indicate that the action never
        conflicts.  It must be a hashable value.

        The ``callable`` is a callable object which performs the action.  It
        is optional.  ``args`` and ``kw`` are tuple and dict objects
        respectively, which are passed to ``callable`` when this action is
        executed.

        ``order`` is a crude order control mechanism, only rarely used (has
        no effect when autocommit is ``True``).
        """
        if kw is None:
            kw = {}

        autocommit = self.autocommit

        if autocommit:
            if callable is not None:
                callable(*args, **kw)

        else:
            info = self.info # usually a ZCML action if self.info has data
            if not info:
                # Try to provide more accurate info for conflict reports
                if self._ainfo:
                    info = self._ainfo[0]
                else:
                    info = ''
            self.action_state.action(
                discriminator,
                callable,
                args,
                kw,
                order,
                info=info,
                includepath=self.includepath,
                )

    def _get_action_state(self):
        registry = self.registry
        try:
            state = registry.action_state
        except AttributeError:
            state = ActionState()
            registry.action_state = state
        return state

    def _set_action_state(self, state):
        self.registry.action_state = state

    action_state = property(_get_action_state, _set_action_state)

    _ctx = action_state # bw compat

    def commit(self):
        """ Commit any pending configuration actions. If a configuration
        conflict is detected in the pending configuration actions, this method
        will raise a :exc:`ConfigurationConflictError`; within the traceback
        of this error will be information about the source of the conflict,
        usually including file names and line numbers of the cause of the
        configuration conflicts."""
        self.action_state.execute_actions()
        self.action_state = ActionState() # old actions have been processed

    def include(self, callable, route_prefix=None):
        """Include a configuration callables, to support imperative
        application extensibility.

        .. warning:: In versions of :app:`Pyramid` prior to 1.2, this
            function accepted ``*callables``, but this has been changed
            to support only a single callable.

        A configuration callable should be a callable that accepts a single
        argument named ``config``, which will be an instance of a
        :term:`Configurator`  (be warned that it will not be the same
        configurator instance on which you call this method, however).  The
        code which runs as the result of calling the callable should invoke
        methods on the configurator passed to it which add configuration
        state.  The return value of a callable will be ignored.

        Values allowed to be presented via the ``callable`` argument to
        this method: any callable Python object or any :term:`dotted Python
        name` which resolves to a callable Python object.  It may also be a
        Python :term:`module`, in which case, the module will be searched for
        a callable named ``includeme``, which will be treated as the
        configuration callable.

        For example, if the ``includeme`` function below lives in a module
        named ``myapp.myconfig``:

        .. code-block:: python
           :linenos:

           # myapp.myconfig module

           def my_view(request):
               from pyramid.response import Response
               return Response('OK')

           def includeme(config):
               config.add_view(my_view)

        You might cause it be included within your Pyramid application like
        so:

        .. code-block:: python
           :linenos:

           from pyramid.config import Configurator

           def main(global_config, **settings):
               config = Configurator()
               config.include('myapp.myconfig.includeme')

        Because the function is named ``includeme``, the function name can
        also be omitted from the dotted name reference:

        .. code-block:: python
           :linenos:

           from pyramid.config import Configurator

           def main(global_config, **settings):
               config = Configurator()
               config.include('myapp.myconfig')

        Included configuration statements will be overridden by local
        configuration statements if an included callable causes a
        configuration conflict by registering something with the same
        configuration parameters.

        If the ``route_prefix`` is supplied, it must be a string.  Any calls
        to :meth:`pyramid.config.Configurator.add_route` within the included
        callable will have their pattern prefixed with the value of
        ``route_prefix``. This can be used to help mount a set of routes at a
        different location than the included callable's author intended while
        still maintaining the same route names.  For example:

        .. code-block:: python
           :linenos:

           from pyramid.config import Configurator

           def included(config):
               config.add_route('show_users', '/show')

           def main(global_config, **settings):
               config = Configurator()
               config.include(included, route_prefix='/users')

        In the above configuration, the ``show_users`` route will have an
        effective route pattern of ``/users/show``, instead of ``/show``
        because the ``route_prefix`` argument will be prepended to the
        pattern.

        The ``route_prefix`` parameter is new as of Pyramid 1.2.
        """
        # """ <-- emacs

        action_state = self.action_state

        if route_prefix is None:
            route_prefix = ''

        old_route_prefix = self.route_prefix
        if old_route_prefix is None:
            old_route_prefix = ''

        route_prefix = '%s/%s' % (
            old_route_prefix.rstrip('/'),
            route_prefix.lstrip('/')
            )
        route_prefix = route_prefix.strip('/')
        if not route_prefix:
            route_prefix = None

        c = self.maybe_dotted(callable)
        module = inspect.getmodule(c)
        if module is c:
            c = getattr(module, 'includeme')
        spec = module.__name__ + ':' + c.__name__
        sourcefile = inspect.getsourcefile(c)

        if action_state.processSpec(spec):
            configurator = self.__class__(
                registry=self.registry,
                package=package_of(module),
                autocommit=self.autocommit,
                route_prefix=route_prefix,
                )
            configurator.basepath = os.path.dirname(sourcefile)
            configurator.includepath = self.includepath + (spec,)
            c(configurator)

    def add_directive(self, name, directive, action_wrap=True):
        """
        Add a directive method to the configurator.

        .. warning:: This method is typically only used by :app:`Pyramid`
           framework extension authors, not by :app:`Pyramid` application
           developers.

        Framework extenders can add directive methods to a configurator by
        instructing their users to call ``config.add_directive('somename',
        'some.callable')``.  This will make ``some.callable`` accessible as
        ``config.somename``.  ``some.callable`` should be a function which
        accepts ``config`` as a first argument, and arbitrary positional and
        keyword arguments following.  It should use config.action as
        necessary to perform actions.  Directive methods can then be invoked
        like 'built-in' directives such as ``add_view``, ``add_route``, etc.

        The ``action_wrap`` argument should be ``True`` for directives which
        perform ``config.action`` with potentially conflicting
        discriminators.  ``action_wrap`` will cause the directive to be
        wrapped in a decorator which provides more accurate conflict
        cause information.

        ``add_directive`` does not participate in conflict detection, and
        later calls to ``add_directive`` will override earlier calls.
        """
        c = self.maybe_dotted(directive)
        if not hasattr(self.registry, '_directives'):
            self.registry._directives = {}
        self.registry._directives[name] = (c, action_wrap)

    def __getattr__(self, name):
        # allow directive extension names to work
        directives = getattr(self.registry, '_directives', {})
        c = directives.get(name)
        if c is None:
            raise AttributeError(name)
        c, action_wrap = c
        if action_wrap:
            c = action_method(c)
        m = types.MethodType(c, self, self.__class__)
        return m

    @classmethod
    def with_context(cls, context):
        """A classmethod used by ZCML directives,
        :meth:`pyramid.config.Configurator.with_package`, and
        :meth:`pyramid.config.Configurator.include` to obtain a configurator
        with 'the right' context.  Returns a new Configurator instance."""
        configurator = cls(
            registry=context.registry,
            package=context.package,
            autocommit=context.autocommit,
            route_prefix=context.route_prefix
            )
        configurator.basepath = context.basepath
        configurator.includepath = context.includepath
        configurator.info = context.info
        return configurator

    def with_package(self, package):
        """ Return a new Configurator instance with the same registry
        as this configurator using the package supplied as the
        ``package`` argument to the new configurator.  ``package`` may
        be an actual Python package object or a :term:`dotted Python name`
        representing a package."""
        configurator = self.__class__(
            registry=self.registry,
            package=package,
            autocommit=self.autocommit,
            route_prefix=self.route_prefix,
            )
        configurator.basepath = self.basepath
        configurator.includepath = self.includepath
        configurator.info = self.info
        return configurator

    def maybe_dotted(self, dotted):
        """ Resolve the :term:`dotted Python name` ``dotted`` to a
        global Python object.  If ``dotted`` is not a string, return
        it without attempting to do any name resolution.  If
        ``dotted`` is a relative dotted name (e.g. ``.foo.bar``,
        consider it relative to the ``package`` argument supplied to
        this Configurator's constructor."""
        return self.name_resolver.maybe_resolve(dotted)

    def absolute_asset_spec(self, relative_spec):
        """ Resolve the potentially relative :term:`asset
        specification` string passed as ``relative_spec`` into an
        absolute asset specification string and return the string.
        Use the ``package`` of this configurator as the package to
        which the asset specification will be considered relative
        when generating an absolute asset specification.  If the
        provided ``relative_spec`` argument is already absolute, or if
        the ``relative_spec`` is not a string, it is simply returned."""
        if not isinstance(relative_spec, basestring):
            return relative_spec
        return self._make_spec(relative_spec)

    absolute_resource_spec = absolute_asset_spec # b/w compat forever

    def begin(self, request=None):
        """ Indicate that application or test configuration has begun.
        This pushes a dictionary containing the :term:`application
        registry` implied by ``registry`` attribute of this
        configurator and the :term:`request` implied by the
        ``request`` argument on to the :term:`thread local` stack
        consulted by various :mod:`pyramid.threadlocal` API
        functions."""
        self.manager.push({'registry':self.registry, 'request':request})

    def end(self):
        """ Indicate that application or test configuration has ended.
        This pops the last value pushed on to the :term:`thread local`
        stack (usually by the ``begin`` method) and returns that
        value.
        """
        return self.manager.pop()

    # this is *not* an action method (uses caller_package)
    def scan(self, package=None, categories=None, onerror=None, **kw):
        """Scan a Python package and any of its subpackages for objects
        marked with :term:`configuration decoration` such as
        :class:`pyramid.view.view_config`.  Any decorated object found will
        influence the current configuration state.

        The ``package`` argument should be a Python :term:`package` or module
        object (or a :term:`dotted Python name` which refers to such a
        package or module).  If ``package`` is ``None``, the package of the
        *caller* is used.

        The ``categories`` argument, if provided, should be the
        :term:`Venusian` 'scan categories' to use during scanning.  Providing
        this argument is not often necessary; specifying scan categories is
        an extremely advanced usage.  By default, ``categories`` is ``None``
        which will execute *all* Venusian decorator callbacks including
        :app:`Pyramid`-related decorators such as
        :class:`pyramid.view.view_config`.  See the :term:`Venusian`
        documentation for more information about limiting a scan by using an
        explicit set of categories.

        The ``onerror`` argument, if provided, should be a Venusian
        ``onerror`` callback function.  The onerror function is passed to
        :meth:`venusian.Scanner.scan` to influence error behavior when an
        exception is raised during the scanning process.  See the
        :term:`Venusian` documentation for more information about ``onerror``
        callbacks.

        To perform a ``scan``, Pyramid creates a Venusian ``Scanner`` object.
        The ``kw`` argument represents a set of keyword arguments to pass to
        the Venusian ``Scanner`` object's constructor.  See the
        :term:`venusian` documentation (its ``Scanner`` class) for more
        information about the constructor.  By default, the only keyword
        arguments passed to the Scanner constructor are ``{'config':self}``
        where ``self`` is this configurator object.  This services the
        requirement of all built-in Pyramid decorators, but extension systems
        may require additional arguments.  Providing this argument is not
        often necessary; it's an advanced usage.

        .. note:: the ``**kw`` argument is new in Pyramid 1.1
        """
        package = self.maybe_dotted(package)
        if package is None: # pragma: no cover
            package = caller_package()

        ctorkw = {'config':self}
        ctorkw.update(kw)

        scanner = self.venusian.Scanner(**ctorkw)
        scanner.scan(package, categories=categories, onerror=onerror)

    def make_wsgi_app(self):
        """ Commits any pending configuration statements, sends a
        :class:`pyramid.events.ApplicationCreated` event to all listeners,
        adds this configuration's registry to
        :attr:`pyramid.config.global_registries`, and returns a
        :app:`Pyramid` WSGI application representing the committed
        configuration state."""
        self.commit()
        app = Router(self.registry)

        # Allow tools like "paster pshell development.ini" to find the 'last'
        # registry configured.
        global_registries.add(self.registry)

        # Push the registry on to the stack in case any code that depends on
        # the registry threadlocal APIs used in listeners subscribed to the
        # IApplicationCreated event.
        self.manager.push({'registry':self.registry, 'request':None})
        try:
            self.registry.notify(ApplicationCreated(app))
        finally:
            self.manager.pop()

        return app

# this class is licensed under the ZPL (stolen from Zope)
class ActionState(object):
    def __init__(self):
        self.actions = [] # NB "actions" is an API, dep'd upon by pyramid_zcml
        self._seen_files = set()

    def processSpec(self, spec):
        """Check whether a callable needs to be processed.  The ``spec``
        refers to a unique identifier for the callable.

        Return True if processing is needed and False otherwise. If
        the callable needs to be processed, it will be marked as
        processed, assuming that the caller will procces the callable if
        it needs to be processed.
        """
        if spec in self._seen_files:
            return False
        self._seen_files.add(spec)
        return True

    def action(self, discriminator, callable=None, args=(), kw=None, order=0,
               includepath=(), info=''):
        """Add an action with the given discriminator, callable and arguments
        """
        # NB: note that the ordering and composition of the action tuple should
        # not change without first ensuring that ``pyramid_zcml`` appends
        # similarly-composed actions to our .actions variable (as silly as
        # the composition and ordering is).
        if kw is None:
            kw = {}
        action = (discriminator, callable, args, kw, includepath, info, order)
        # remove trailing false items
        while (len(action) > 2) and not action[-1]:
            action = action[:-1]
        self.actions.append(action)

    def execute_actions(self, clear=True):
        """Execute the configuration actions

        This calls the action callables after resolving conflicts

        For example:

        >>> output = []
        >>> def f(*a, **k):
        ...    output.append(('f', a, k))
        >>> context = ActionState()
        >>> context.actions = [
        ...   (1, f, (1,)),
        ...   (1, f, (11,), {}, ('x', )),
        ...   (2, f, (2,)),
        ...   ]
        >>> context.execute_actions()
        >>> output
        [('f', (1,), {}), ('f', (2,), {})]

        If the action raises an error, we convert it to a
        ConfigurationExecutionError.

        >>> output = []
        >>> def bad():
        ...    bad.xxx
        >>> context.actions = [
        ...   (1, f, (1,)),
        ...   (1, f, (11,), {}, ('x', )),
        ...   (2, f, (2,)),
        ...   (3, bad, (), {}, (), 'oops')
        ...   ]
        >>> try:
        ...    v = context.execute_actions()
        ... except ConfigurationExecutionError, v:
        ...    pass
        >>> print v
        exceptions.AttributeError: 'function' object has no attribute 'xxx'
          in:
          oops


        Note that actions executed before the error still have an effect:

        >>> output
        [('f', (1,), {}), ('f', (2,), {})]


        """
        try:
            for action in resolveConflicts(self.actions):
                _, callable, args, kw, _, info, _ = expand_action(*action)
                if callable is None:
                    continue
                try:
                    callable(*args, **kw)
                except (KeyboardInterrupt, SystemExit): # pragma: no cover
                    raise
                except:
                    t, v, tb = sys.exc_info()
                    try:
                        raise ConfigurationExecutionError(t, v, info), None, tb
                    finally:
                       del t, v, tb
        finally:
            if clear:
                del self.actions[:]

# this function is licensed under the ZPL (stolen from Zope)
def resolveConflicts(actions):
    """Resolve conflicting actions

    Given an actions list, identify and try to resolve conflicting actions.
    Actions conflict if they have the same non-null discriminator.
    Conflicting actions can be resolved if the include path of one of
    the actions is a prefix of the includepaths of the other
    conflicting actions and is unequal to the include paths in the
    other conflicting actions.

    Here are some examples to illustrate how this works:

    >>> from zope.configmachine.tests.directives import f
    >>> from pprint import PrettyPrinter
    >>> pprint=PrettyPrinter(width=60).pprint
    >>> pprint(resolveConflicts([
    ...    (None, f),
    ...    (1, f, (1,), {}, (), 'first'),
    ...    (1, f, (2,), {}, ('x',), 'second'),
    ...    (1, f, (3,), {}, ('y',), 'third'),
    ...    (4, f, (4,), {}, ('y',), 'should be last', 99999),
    ...    (3, f, (3,), {}, ('y',)),
    ...    (None, f, (5,), {}, ('y',)),
    ... ]))
    [(None, f),
     (1, f, (1,), {}, (), 'first'),
     (3, f, (3,), {}, ('y',)),
     (None, f, (5,), {}, ('y',)),
     (4, f, (4,), {}, ('y',), 'should be last')]

    >>> try:
    ...     v = resolveConflicts([
    ...        (None, f),
    ...        (1, f, (2,), {}, ('x',), 'eek'),
    ...        (1, f, (3,), {}, ('y',), 'ack'),
    ...        (4, f, (4,), {}, ('y',)),
    ...        (3, f, (3,), {}, ('y',)),
    ...        (None, f, (5,), {}, ('y',)),
    ...     ])
    ... except ConfigurationConflictError, v:
    ...    pass
    >>> print v
    Conflicting configuration actions
      For: 1
        eek
        ack

    """

    # organize actions by discriminators
    unique = {}
    output = []
    for i in range(len(actions)):
        action = actions[i]
        if isinstance(action, dict): # z.config 3.8.0+
            discriminator = action['discriminator']
            callable = action['callable']
            args = action['args']
            kw = action['kw']
            includepath = action['includepath']
            info = action['info']
            order = action['order']
        else:
            (discriminator, callable, args, kw, includepath, info, order
             ) = expand_action(*(actions[i]))

        order = order or i
        if discriminator is None:
            # The discriminator is None, so this directive can
            # never conflict. We can add it directly to the
            # configuration actions.
            output.append(
                (order, discriminator, callable, args, kw, includepath, info)
                )
            continue


        a = unique.setdefault(discriminator, [])
        a.append(
            (includepath, order, callable, args, kw, info)
            )

    # Check for conflicts
    conflicts = {}
    for discriminator, dups in unique.items():

        # We need to sort the actions by the paths so that the shortest
        # path with a given prefix comes first:
        dups.sort()
        (basepath, i, callable, args, kw, baseinfo) = dups[0]
        output.append(
            (i, discriminator, callable, args, kw, basepath, baseinfo)
            )
        for includepath, i, callable, args, kw, info in dups[1:]:
            # Test whether path is a prefix of opath
            if (includepath[:len(basepath)] != basepath # not a prefix
                or
                (includepath == basepath)
                ):
                if discriminator not in conflicts:
                    conflicts[discriminator] = [baseinfo]
                conflicts[discriminator].append(info)


    if conflicts:
        raise ConfigurationConflictError(conflicts)

    # Now put the output back in the original order, and return it:
    output.sort()
    r = []
    for o in output:
        action = o[1:]
        while len(action) > 2 and not action[-1]:
            action = action[:-1]
        r.append(action)

    return r

# this function is licensed under the ZPL (stolen from Zope)
def expand_action(discriminator, callable=None, args=(), kw=None,
                   includepath=(), info='', order=0):
    if kw is None:
        kw = {}
    return (discriminator, callable, args, kw, includepath, info, order)

global_registries = WeakOrderedSet()

