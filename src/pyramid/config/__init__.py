import inspect
import logging
import os
import threading
import venusian

from webob.exc import WSGIHTTPException as WebobWSGIHTTPException

from pyramid.interfaces import (
    IDebugLogger,
    IExceptionResponse,
    PHASE0_CONFIG,
    PHASE1_CONFIG,
    PHASE2_CONFIG,
    PHASE3_CONFIG,
)

from pyramid.asset import resolve_asset_spec

from pyramid.authorization import ACLAuthorizationPolicy

from pyramid.compat import text_, string_types

from pyramid.events import ApplicationCreated

from pyramid.exceptions import ConfigurationError

from pyramid.httpexceptions import default_exceptionresponse_view

from pyramid.path import caller_package, package_of

from pyramid.registry import Introspectable, Introspector, Registry

from pyramid.router import Router

from pyramid.settings import aslist

from pyramid.threadlocal import manager

from pyramid.util import WeakOrderedSet, object_description

from pyramid.config.actions import action_method, ActionState
from pyramid.config.predicates import not_

from pyramid.config.actions import ActionConfiguratorMixin
from pyramid.config.adapters import AdaptersConfiguratorMixin
from pyramid.config.assets import AssetsConfiguratorMixin
from pyramid.config.factories import FactoriesConfiguratorMixin
from pyramid.config.i18n import I18NConfiguratorMixin
from pyramid.config.predicates import PredicateConfiguratorMixin
from pyramid.config.rendering import RenderingConfiguratorMixin
from pyramid.config.routes import RoutesConfiguratorMixin
from pyramid.config.security import SecurityConfiguratorMixin
from pyramid.config.settings import SettingsConfiguratorMixin
from pyramid.config.testing import TestingConfiguratorMixin
from pyramid.config.tweens import TweensConfiguratorMixin
from pyramid.config.views import ViewsConfiguratorMixin
from pyramid.config.zca import ZCAConfiguratorMixin

from pyramid.path import DottedNameResolver

empty = text_('')
_marker = object()

not_ = not_  # api

PHASE0_CONFIG = PHASE0_CONFIG  # api
PHASE1_CONFIG = PHASE1_CONFIG  # api
PHASE2_CONFIG = PHASE2_CONFIG  # api
PHASE3_CONFIG = PHASE3_CONFIG  # api

ActionState = ActionState  # bw-compat for pyramid_zcml


class Configurator(
    ActionConfiguratorMixin,
    PredicateConfiguratorMixin,
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

    The Configurator lifecycle can be managed by using a context manager to
    automatically handle calling :meth:`pyramid.config.Configurator.begin` and
    :meth:`pyramid.config.Configurator.end` as well as
    :meth:`pyramid.config.Configurator.commit`.

    .. code-block:: python

        with Configurator(settings=settings) as config:
            config.add_route('home', '/')
            app = config.make_wsgi_app()

    If the ``registry`` argument is not ``None``, it must
    be an instance of the :class:`pyramid.registry.Registry` class
    representing the registry to configure.  If ``registry`` is ``None``, the
    configurator will create a :class:`pyramid.registry.Registry` instance
    itself; it will also perform some default configuration that would not
    otherwise be done.  After its construction, the configurator may be used
    to add further configuration to the registry.

    .. warning:: If ``registry`` is assigned the above-mentioned class
       instance, all other constructor arguments are ignored,
       with the exception of ``package``.

    If the ``package`` argument is passed, it must be a reference to a Python
    :term:`package` (e.g. ``sys.modules['thepackage']``) or a :term:`dotted
    Python name` to the same.  This value is used as a basis to convert
    relative paths passed to various configuration methods, such as methods
    which accept a ``renderer`` argument, into absolute paths.  If ``None``
    is passed (the default), the package is assumed to be the Python package
    in which the *caller* of the ``Configurator`` constructor lives.

    If the ``root_package`` is passed, it will propagate through the
    configuration hierarchy as a way for included packages to locate
    resources relative to the package in which the main ``Configurator`` was
    created. If ``None`` is passed (the default), the ``root_package`` will
    be derived from the ``package`` argument. The ``package`` attribute is
    always pointing at the package being included when using :meth:`.include`,
    whereas the ``root_package`` does not change.

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

    If ``renderers`` is ``None`` (the default), a default set of
    :term:`renderer` factories is used. Else, it should be a list of
    tuples representing a set of renderer factories which should be
    configured into this application, and each tuple representing a set of
    positional values that should be passed to
    :meth:`pyramid.config.Configurator.add_renderer`.

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

    If ``response_factory`` is passed, it should be a :term:`response
    factory` implementation or a :term:`dotted Python name` to the same.
    See :ref:`changing_the_response_factory`.  By default it is ``None``,
    which means use the default response factory.

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
    authorization policy in effect is ignored).

    .. seealso::

        See also :ref:`setting_a_default_permission`.

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
    ``autocommit`` is ``True``.  If a conflict is detected, a
    ``ConfigurationConflictError`` will be raised.  Calling
    :meth:`pyramid.config.Configurator.make_wsgi_app` always implies a final
    commit.

    If ``default_view_mapper`` is passed, it will be used as the default
    :term:`view mapper` factory for view configurations that don't otherwise
    specify one (see :class:`pyramid.interfaces.IViewMapperFactory`).  If
    ``default_view_mapper`` is not passed, a superdefault view mapper will be
    used.

    If ``exceptionresponse_view`` is passed, it must be a :term:`view
    callable` or ``None``.  If it is a view callable, it will be used as an
    exception view callable when an :term:`exception response` is raised. If
    ``exceptionresponse_view`` is ``None``, no exception response view will
    be registered, and all raised exception responses will be bubbled up to
    Pyramid's caller.  By
    default, the ``pyramid.httpexceptions.default_exceptionresponse_view``
    function is used as the ``exceptionresponse_view``.

    If ``route_prefix`` is passed, all routes added with
    :meth:`pyramid.config.Configurator.add_route` will have the specified path
    prepended to their pattern.

    If ``introspection`` is passed, it must be a boolean value.  If it's
    ``True``, introspection values during actions will be kept for use
    for tools like the debug toolbar.  If it's ``False``, introspection
    values provided by registrations will be ignored.  By default, it is
    ``True``.

    .. versionadded:: 1.1
       The ``exceptionresponse_view`` argument.

    .. versionadded:: 1.2
       The ``route_prefix`` argument.

    .. versionadded:: 1.3
       The ``introspection`` argument.

    .. versionadded:: 1.6
       The ``root_package`` argument.
       The ``response_factory`` argument.

    .. versionadded:: 1.9
       The ability to use the configurator as a context manager with the
       ``with``-statement to make threadlocal configuration available for
       further configuration with an implicit commit.
    """

    manager = manager  # for testing injection
    venusian = venusian  # for testing injection
    _ainfo = None
    basepath = None
    includepath = ()
    info = ''
    object_description = staticmethod(object_description)
    introspectable = Introspectable
    inspect = inspect

    def __init__(
        self,
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
        response_factory=None,
        default_permission=None,
        session_factory=None,
        default_view_mapper=None,
        autocommit=False,
        exceptionresponse_view=default_exceptionresponse_view,
        route_prefix=None,
        introspection=True,
        root_package=None,
    ):
        if package is None:
            package = caller_package()
        if root_package is None:
            root_package = package
        name_resolver = DottedNameResolver(package)
        self.name_resolver = name_resolver
        self.package_name = name_resolver.get_package_name()
        self.package = name_resolver.get_package()
        self.root_package = root_package
        self.registry = registry
        self.autocommit = autocommit
        self.route_prefix = route_prefix
        self.introspection = introspection
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
                response_factory=response_factory,
                default_permission=default_permission,
                session_factory=session_factory,
                default_view_mapper=default_view_mapper,
                exceptionresponse_view=exceptionresponse_view,
            )

    def setup_registry(
        self,
        settings=None,
        root_factory=None,
        authentication_policy=None,
        authorization_policy=None,
        renderers=None,
        debug_logger=None,
        locale_negotiator=None,
        request_factory=None,
        response_factory=None,
        default_permission=None,
        session_factory=None,
        default_view_mapper=None,
        exceptionresponse_view=default_exceptionresponse_view,
    ):
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

        if isinstance(debug_logger, string_types):
            debug_logger = logging.getLogger(debug_logger)

        if debug_logger is None:
            debug_logger = logging.getLogger(self.package_name)

        registry.registerUtility(debug_logger, IDebugLogger)

        self.add_default_response_adapters()
        self.add_default_renderers()
        self.add_default_accept_view_order()
        self.add_default_view_predicates()
        self.add_default_view_derivers()
        self.add_default_route_predicates()
        self.add_default_tweens()
        self.add_default_security()

        if exceptionresponse_view is not None:
            exceptionresponse_view = self.maybe_dotted(exceptionresponse_view)
            self.add_view(exceptionresponse_view, context=IExceptionResponse)
            self.add_view(
                exceptionresponse_view, context=WebobWSGIHTTPException
            )

        # commit below because:
        #
        # - the default exceptionresponse_view requires the superdefault view
        #   mapper, so we need to configure it before adding
        #   default_view_mapper
        #
        # - superdefault renderers should be overrideable without requiring
        #   the user to commit before calling config.add_renderer

        self.commit()

        # self.commit() should not be called within this method after this
        # point because the following registrations should be treated as
        # analogues of methods called by the user after configurator
        # construction.  Rationale: user-supplied implementations should be
        # preferred rather than add-on author implementations with the help of
        # automatic conflict resolution.

        if authentication_policy and not authorization_policy:
            authorization_policy = ACLAuthorizationPolicy()  # default

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

        if response_factory:
            self.set_response_factory(response_factory)

        if default_permission:
            self.set_default_permission(default_permission)

        if session_factory is not None:
            self.set_session_factory(session_factory)

        tweens = aslist(registry.settings.get('pyramid.tweens', []))
        for factory in tweens:
            self._add_tween(factory, explicit=True)

        includes = aslist(registry.settings.get('pyramid.includes', []))
        for inc in includes:
            self.include(inc)

    def _make_spec(self, path_or_spec):
        package, filename = resolve_asset_spec(path_or_spec, self.package_name)
        if package is None:
            return filename  # absolute filename
        return '%s:%s' % (package, filename)

    def _fix_registry(self):
        """ Fix up a ZCA component registry that is not a
        pyramid.registry.Registry by adding analogues of ``has_listeners``,
        ``notify``, ``queryAdapterOrSelf``, and ``registerSelfAdapter``
        through monkey-patching."""

        _registry = self.registry

        if not hasattr(_registry, 'notify'):

            def notify(*events):
                [_ for _ in _registry.subscribers(events, None)]

            _registry.notify = notify

        if not hasattr(_registry, 'has_listeners'):
            _registry.has_listeners = True

        if not hasattr(_registry, 'queryAdapterOrSelf'):

            def queryAdapterOrSelf(object, interface, default=None):
                if not interface.providedBy(object):
                    return _registry.queryAdapter(
                        object, interface, default=default
                    )
                return object

            _registry.queryAdapterOrSelf = queryAdapterOrSelf

        if not hasattr(_registry, 'registerSelfAdapter'):

            def registerSelfAdapter(
                required=None,
                provided=None,
                name=empty,
                info=empty,
                event=True,
            ):
                return _registry.registerAdapter(
                    lambda x: x,
                    required=required,
                    provided=provided,
                    name=name,
                    info=info,
                    event=event,
                )

            _registry.registerSelfAdapter = registerSelfAdapter

        if not hasattr(_registry, '_lock'):
            _registry._lock = threading.Lock()

        if not hasattr(_registry, '_clear_view_lookup_cache'):

            def _clear_view_lookup_cache():
                _registry._view_lookup_cache = {}

            _registry._clear_view_lookup_cache = _clear_view_lookup_cache

    # API

    def _get_introspector(self):
        introspector = getattr(self.registry, 'introspector', _marker)
        if introspector is _marker:
            introspector = Introspector()
            self._set_introspector(introspector)
        return introspector

    def _set_introspector(self, introspector):
        self.registry.introspector = introspector

    def _del_introspector(self):
        del self.registry.introspector

    introspector = property(
        _get_introspector, _set_introspector, _del_introspector
    )

    def include(self, callable, route_prefix=None):
        """Include a configuration callable, to support imperative
        application extensibility.

        .. warning:: In versions of :app:`Pyramid` prior to 1.2, this
            function accepted ``*callables``, but this has been changed
            to support only a single callable.

        A configuration callable should be a callable that accepts a single
        argument named ``config``, which will be an instance of a
        :term:`Configurator`.  However, be warned that it will not be the same
        configurator instance on which you call this method.  The
        code which runs as a result of calling the callable should invoke
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

        You might cause it to be included within your Pyramid application like
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
        different location than the included callable's author intended, while
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

        .. versionadded:: 1.2
           The ``route_prefix`` parameter.

        .. versionchanged:: 1.9
           The included function is wrapped with a call to
           :meth:`pyramid.config.Configurator.begin` and
           :meth:`pyramid.config.Configurator.end` while it is executed.

        """
        # """ <-- emacs

        action_state = self.action_state

        c = self.maybe_dotted(callable)
        module = self.inspect.getmodule(c)
        if module is c:
            try:
                c = getattr(module, 'includeme')
            except AttributeError:
                raise ConfigurationError(
                    "module %r has no attribute 'includeme'"
                    % (module.__name__)
                )

        spec = module.__name__ + ':' + c.__name__
        sourcefile = self.inspect.getsourcefile(c)

        if sourcefile is None:
            raise ConfigurationError(
                'No source file for module %r (.py file must exist, '
                'refusing to use orphan .pyc or .pyo file).' % module.__name__
            )

        if action_state.processSpec(spec):
            with self.route_prefix_context(route_prefix):
                configurator = self.__class__(
                    registry=self.registry,
                    package=package_of(module),
                    root_package=self.root_package,
                    autocommit=self.autocommit,
                    route_prefix=self.route_prefix,
                )
                configurator.basepath = os.path.dirname(sourcefile)
                configurator.includepath = self.includepath + (spec,)

                self.begin()
                try:
                    c(configurator)
                finally:
                    self.end()

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
        # Create a bound method (works on both Py2 and Py3)
        # http://stackoverflow.com/a/1015405/209039
        m = c.__get__(self, self.__class__)
        return m

    def with_package(self, package):
        """ Return a new Configurator instance with the same registry
        as this configurator. ``package`` may be an actual Python package
        object or a :term:`dotted Python name` representing a package."""
        configurator = self.__class__(
            registry=self.registry,
            package=package,
            root_package=self.root_package,
            autocommit=self.autocommit,
            route_prefix=self.route_prefix,
            introspection=self.introspection,
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
        if not isinstance(relative_spec, string_types):
            return relative_spec
        return self._make_spec(relative_spec)

    absolute_resource_spec = absolute_asset_spec  # b/w compat forever

    def begin(self, request=_marker):
        """ Indicate that application or test configuration has begun.
        This pushes a dictionary containing the :term:`application
        registry` implied by ``registry`` attribute of this
        configurator and the :term:`request` implied by the
        ``request`` argument onto the :term:`thread local` stack
        consulted by various :mod:`pyramid.threadlocal` API
        functions.

        If ``request`` is not specified and the registry owned by the
        configurator is already pushed as the current threadlocal registry
        then this method will keep the current threadlocal request unchanged.

        .. versionchanged:: 1.8
           The current threadlocal request is propagated if the current
           threadlocal registry remains unchanged.

        """
        if request is _marker:
            current = self.manager.get()
            if current['registry'] == self.registry:
                request = current['request']
            else:
                request = None
        self.manager.push({'registry': self.registry, 'request': request})

    def end(self):
        """ Indicate that application or test configuration has ended.
        This pops the last value pushed onto the :term:`thread local`
        stack (usually by the ``begin`` method) and returns that
        value.
        """
        return self.manager.pop()

    def __enter__(self):
        self.begin()
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.end()

        if exc_value is None:
            self.commit()

    # this is *not* an action method (uses caller_package)
    def scan(
        self, package=None, categories=None, onerror=None, ignore=None, **kw
    ):
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

        The ``ignore`` argument, if provided, should be a Venusian ``ignore``
        value.  Providing an ``ignore`` argument allows the scan to ignore
        particular modules, packages, or global objects during a scan.
        ``ignore`` can be a string or a callable, or a list containing
        strings or callables.  The simplest usage of ``ignore`` is to provide
        a module or package by providing a full path to its dotted name.  For
        example: ``config.scan(ignore='my.module.subpackage')`` would ignore
        the ``my.module.subpackage`` package during a scan, which would
        prevent the subpackage and any of its submodules from being imported
        and scanned.  See the :term:`Venusian` documentation for more
        information about the ``ignore`` argument.

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

        .. versionadded:: 1.1
           The ``**kw`` argument.

        .. versionadded:: 1.3
           The ``ignore`` argument.

        """
        package = self.maybe_dotted(package)
        if package is None:  # pragma: no cover
            package = caller_package()

        ctorkw = {'config': self}
        ctorkw.update(kw)

        scanner = self.venusian.Scanner(**ctorkw)

        scanner.scan(
            package, categories=categories, onerror=onerror, ignore=ignore
        )

    def make_wsgi_app(self):
        """ Commits any pending configuration statements, sends a
        :class:`pyramid.events.ApplicationCreated` event to all listeners,
        adds this configuration's registry to
        :attr:`pyramid.config.global_registries`, and returns a
        :app:`Pyramid` WSGI application representing the committed
        configuration state."""
        self.commit()
        app = Router(self.registry)

        # Allow tools like "pshell development.ini" to find the 'last'
        # registry configured.
        global_registries.add(self.registry)

        # Push the registry onto the stack in case any code that depends on
        # the registry threadlocal APIs used in listeners subscribed to the
        # IApplicationCreated event.
        self.begin()
        try:
            self.registry.notify(ApplicationCreated(app))
        finally:
            self.end()

        return app


global_registries = WeakOrderedSet()
