import inspect
import logging
import os
import re
import sys
import types
import traceback
import warnings
from hashlib import md5

import venusian

from translationstring import ChameleonTranslate

from zope.configuration.config import GroupingContextDecorator
from zope.configuration.config import ConfigurationMachine
from zope.configuration.xmlconfig import registerCommonDirectives

from zope.interface import Interface
from zope.interface import implementedBy
from zope.interface.interfaces import IInterface
from zope.interface import implements
from zope.interface import classProvides

from pyramid.interfaces import IAuthenticationPolicy
from pyramid.interfaces import IAuthorizationPolicy
from pyramid.interfaces import IChameleonTranslate
from pyramid.interfaces import IDebugLogger
from pyramid.interfaces import IDefaultPermission
from pyramid.interfaces import IDefaultRootFactory
from pyramid.interfaces import IException
from pyramid.interfaces import IExceptionResponse
from pyramid.interfaces import IExceptionViewClassifier
from pyramid.interfaces import ILocaleNegotiator
from pyramid.interfaces import IMultiView
from pyramid.interfaces import IPackageOverrides
from pyramid.interfaces import IRendererFactory
from pyramid.interfaces import IRendererGlobalsFactory
from pyramid.interfaces import IRequest
from pyramid.interfaces import IRequestFactory
from pyramid.interfaces import ITweens
from pyramid.interfaces import IResponse
from pyramid.interfaces import IRootFactory
from pyramid.interfaces import IRouteRequest
from pyramid.interfaces import IRoutesMapper
from pyramid.interfaces import ISecuredView
from pyramid.interfaces import ISessionFactory
from pyramid.interfaces import IStaticURLInfo
from pyramid.interfaces import ITranslationDirectories
from pyramid.interfaces import ITraverser
from pyramid.interfaces import IView
from pyramid.interfaces import IViewClassifier
from pyramid.interfaces import IViewMapper
from pyramid.interfaces import IViewMapperFactory

from pyramid import renderers
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.events import ApplicationCreated
from pyramid.exceptions import ConfigurationError
from pyramid.exceptions import PredicateMismatch
from pyramid.httpexceptions import default_exceptionresponse_view
from pyramid.httpexceptions import HTTPForbidden
from pyramid.httpexceptions import HTTPNotFound
from pyramid.i18n import get_localizer
from pyramid.mako_templating import renderer_factory as mako_renderer_factory
from pyramid.path import caller_package
from pyramid.path import package_path
from pyramid.path import package_of
from pyramid.registry import Registry
from pyramid.renderers import RendererHelper
from pyramid.request import route_request_iface
from pyramid.asset import PackageOverrides
from pyramid.asset import resolve_asset_spec
from pyramid.security import NO_PERMISSION_REQUIRED
from pyramid.settings import Settings
from pyramid.static import StaticURLInfo
from pyramid.threadlocal import get_current_registry
from pyramid.threadlocal import get_current_request
from pyramid.threadlocal import manager
from pyramid.traversal import DefaultRootFactory
from pyramid.traversal import find_interface
from pyramid.traversal import traversal_path
from pyramid.tweens import excview_tween_factory
from pyramid.tweens import Tweens
from pyramid.tweens import tween_factory_name
from pyramid.tweens import MAIN, INGRESS, EXCVIEW
from pyramid.urldispatch import RoutesMapper
from pyramid.util import DottedNameResolver
from pyramid.util import WeakOrderedSet
from pyramid.view import render_view_to_response

DEFAULT_RENDERERS = (
    ('.mak', mako_renderer_factory),
    ('.mako', mako_renderer_factory),
    ('json', renderers.json_renderer_factory),
    ('string', renderers.string_renderer_factory),
    )

try:
    from pyramid import chameleon_text
    DEFAULT_RENDERERS += (('.txt', chameleon_text.renderer_factory),)
except TypeError:  # pragma: no cover
    pass # pypy

try: 
    from pyramid import chameleon_zpt
    DEFAULT_RENDERERS += (('.pt', chameleon_zpt.renderer_factory),)
except TypeError: # pragma: no cover
    pass #pypy

MAX_ORDER = 1 << 30
DEFAULT_PHASH = md5().hexdigest()

def action_method(wrapped):
    """ Wrapper to provide the right conflict info report data when a method
    that calls Configurator.action calls another that does the same"""
    def wrapper(self, *arg, **kw):
        if self._ainfo is None:
            self._ainfo = []
        info = kw.pop('_info', None)
        if info is None:
            try:
                f = traceback.extract_stack(limit=3)
                info = f[-2]
            except: # pragma: no cover
                info = ''
        self._ainfo.append(info)
        try:
            result = wrapped(self, *arg, **kw)
        finally:
            self._ainfo.pop()
        return result
    wrapper.__name__ = wrapped.__name__
    wrapper.__doc__ = wrapped.__doc__
    wrapper.__docobj__ = wrapped # for sphinx
    return wrapper

class Configurator(object):
    """
    A Configurator is used to configure a :app:`Pyramid`
    :term:`application registry`.

    The Configurator accepts a number of arguments: ``registry``,
    ``package``, ``settings``, ``root_factory``, ``authentication_policy``,
    ``authorization_policy``, ``renderers``, ``debug_logger``,
    ``locale_negotiator``, ``request_factory``, ``renderer_globals_factory``,
    ``default_permission``, ``session_factory``, ``default_view_mapper``,
    ``autocommit``, and ``exceptionresponse_view``.

    If the ``registry`` argument is passed as a non-``None`` value, it
    must be an instance of the :class:`pyramid.registry.Registry`
    class representing the registry to configure.  If ``registry`` is
    ``None``, the configurator will create a
    :class:`pyramid.registry.Registry` instance itself; it will
    also perform some default configuration that would not otherwise
    be done.  After construction, the configurator may be used to add
    configuration to the registry.  The overall state of a registry is
    called the 'configuration state'.

    .. warning:: If a ``registry`` is passed to the Configurator
       constructor, all other constructor arguments except ``package``
       are ignored.

    If the ``package`` argument is passed, it must be a reference to a
    Python :term:`package` (e.g. ``sys.modules['thepackage']``) or a
    :term:`dotted Python name` to same.  This value is used as a basis
    to convert relative paths passed to various configuration methods,
    such as methods which accept a ``renderer`` argument, into
    absolute paths.  If ``None`` is passed (the default), the package
    is assumed to be the Python package in which the *caller* of the
    ``Configurator`` constructor lives.

    If the ``settings`` argument is passed, it should be a Python dictionary
    representing the deployment settings for this application.  These are
    later retrievable using the :attr:`pyramid.registry.Registry.settings`
    attribute (aka ``request.registry.settings``).

    If the ``root_factory`` argument is passed, it should be an object
    representing the default :term:`root factory` for your application
    or a :term:`dotted Python name` to same.  If it is ``None``, a
    default root factory will be used.

    If ``authentication_policy`` is passed, it should be an instance
    of an :term:`authentication policy` or a :term:`dotted Python
    name` to same.

    If ``authorization_policy`` is passed, it should be an instance of
    an :term:`authorization policy` or a :term:`dotted Python name` to
    same.

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
    factory` implementation or a :term:`dotted Python name` to same.
    See :ref:`changing_the_request_factory`.  By default it is ``None``,
    which means use the default request factory.

    If ``renderer_globals_factory`` is passed, it should be a :term:`renderer
    globals` factory implementation or a :term:`dotted Python name` to same.
    See :ref:`adding_renderer_globals`.  By default, it is ``None``, which
    means use no renderer globals factory.

    .. warning:: as of Pyramid 1.1, ``renderer_globals_factory`` is
       deprecated.  Instead, use a BeforeRender event subscriber as per
       :ref:`beforerender_event`.

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
    _ctx = None
    _ainfo = None

    def __init__(self,
                 registry=None,
                 package=None,
                 settings=None,
                 root_factory=None,
                 authentication_policy=None,
                 authorization_policy=None,
                 renderers=DEFAULT_RENDERERS,
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

    def _set_settings(self, mapping):
        if not mapping:
            mapping = {}
        settings = Settings(mapping)
        self.registry.settings = settings
        return settings

    @action_method
    def _set_root_factory(self, factory):
        """ Add a :term:`root factory` to the current configuration
        state.  If the ``factory`` argument is ``None`` a default root
        factory will be registered."""
        factory = self.maybe_dotted(factory)
        if factory is None:
            factory = DefaultRootFactory
        def register():
            self.registry.registerUtility(factory, IRootFactory)
            self.registry.registerUtility(factory, IDefaultRootFactory) # b/c
        self.action(IRootFactory, register)

    @action_method
    def _set_authentication_policy(self, policy):
        """ Add a :app:`Pyramid` :term:`authentication policy` to
        the current configuration."""
        policy = self.maybe_dotted(policy)
        self.registry.registerUtility(policy, IAuthenticationPolicy)
        self.action(IAuthenticationPolicy)

    @action_method
    def _set_authorization_policy(self, policy):
        """ Add a :app:`Pyramid` :term:`authorization policy` to
        the current configuration state (also accepts a :term:`dotted
        Python name`."""
        policy = self.maybe_dotted(policy)
        self.registry.registerUtility(policy, IAuthorizationPolicy)
        self.action(IAuthorizationPolicy, None)
            
    def _make_spec(self, path_or_spec):
        package, filename = resolve_asset_spec(path_or_spec,
                                               self.package_name)
        if package is None:
            return filename # absolute filename
        return '%s:%s' % (package, filename)

    def _split_spec(self, path_or_spec):
        return resolve_asset_spec(path_or_spec, self.package_name)

    # b/w compat
    def _derive_view(self, view, permission=None, predicates=(),
                     attr=None, renderer=None, wrapper_viewname=None,
                     viewname=None, accept=None, order=MAX_ORDER,
                     phash=DEFAULT_PHASH, decorator=None,
                     mapper=None, http_cache=None):
        view = self.maybe_dotted(view)
        mapper = self.maybe_dotted(mapper)
        if isinstance(renderer, basestring):
            renderer = RendererHelper(name=renderer, package=self.package,
                                      registry = self.registry)
        if renderer is None:
            # use default renderer if one exists
            if self.registry.queryUtility(IRendererFactory) is not None:
                renderer = RendererHelper(name=None,
                                          package=self.package,
                                          registry=self.registry)

        deriver = ViewDeriver(registry=self.registry,
                              permission=permission,
                              predicates=predicates,
                              attr=attr,
                              renderer=renderer,
                              wrapper_viewname=wrapper_viewname,
                              viewname=viewname,
                              accept=accept,
                              order=order,
                              phash=phash,
                              package=self.package,
                              mapper=mapper,
                              decorator=decorator,
                              http_cache=http_cache)
        
        return deriver(view)

    @action_method
    def _set_security_policies(self, authentication, authorization=None):
        if (authorization is not None) and (not authentication):
            raise ConfigurationError(
                'If the "authorization" is passed a value, '
                'the "authentication" argument must also be '
                'passed a value; authorization requires authentication.')
        if authorization is None:
            authorization = ACLAuthorizationPolicy() # default
        self._set_authentication_policy(authentication)
        self._set_authorization_policy(authorization)

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

    def _make_context(self, autocommit=False):
        context = PyramidConfigurationMachine()
        registerCommonDirectives(context)
        context.registry = self.registry
        context.autocommit = autocommit
        context.route_prefix = self.route_prefix
        return context

    # API

    def action(self, discriminator, callable=None, args=(), kw=None, order=0):
        """ Register an action which will be executed when
        :meth:`pyramid.config.Configuration.commit` is called (or executed
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

        context = self._ctx

        if context is None:
            autocommit = self.autocommit
        else:
            autocommit = context.autocommit

        if autocommit:
            if callable is not None:
                callable(*args, **kw)
        else:
            if context is None: # defer expensive creation of context
                context = self._ctx = self._make_context(self.autocommit)
            if not context.info:
                # Try to provide more accurate info for conflict reports by
                # wrapping the context in a decorator and attaching caller info
                # to it, unless the context already has info (if it already has
                # info, it's likely a context generated by a ZCML directive).
                context = GroupingContextDecorator(context)
                if self._ainfo:
                    info = self._ainfo[0]
                else:
                    info = ''
                context.info = info
            context.action(discriminator, callable, args, kw, order)

    def commit(self):
        """ Commit any pending configuration actions. If a configuration
        conflict is detected in the pending configuration actins, this method
        will raise a :exc:`ConfigurationConflictError`; within the traceback
        of this error will be information about the source of the conflict,
        usually including file names and line numbers of the cause of the
        configuration conflicts."""
        if self._ctx is None:
            return
        self._ctx.execute_actions()
        # unwrap and reset the context
        self._ctx = None

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

        _context = self._ctx
        if _context is None:
            _context = self._ctx = self._make_context(self.autocommit)

        if self.route_prefix:
            old_prefix = self.route_prefix.rstrip('/') + '/'
        else:
            old_prefix = ''

        if route_prefix:
            route_prefix = old_prefix + route_prefix.lstrip('/')

        c = self.maybe_dotted(callable)
        module = inspect.getmodule(c)
        if module is c:
            c = getattr(module, 'includeme')
        spec = module.__name__ + ':' + c.__name__
        sourcefile = inspect.getsourcefile(c)
        if _context.processSpec(spec):
            context = GroupingContextDecorator(_context)
            context.basepath = os.path.dirname(sourcefile)
            context.includepath = _context.includepath + (spec,)
            context.package = package_of(module)
            context.route_prefix = route_prefix
            config = self.__class__.with_context(context)
            c(config)

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
        configurator = cls(registry=context.registry, package=context.package,
                           autocommit=context.autocommit,
                           route_prefix=context.route_prefix)
        configurator._ctx = context
        return configurator

    def with_package(self, package):
        """ Return a new Configurator instance with the same registry
        as this configurator using the package supplied as the
        ``package`` argument to the new configurator.  ``package`` may
        be an actual Python package object or a :term:`dotted Python name`
        representing a package."""
        context = self._ctx
        if context is None:
            context = self._ctx = self._make_context(self.autocommit)
        context = GroupingContextDecorator(context)
        context.package = package
        return self.__class__.with_context(context)

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

    def setup_registry(self, settings=None, root_factory=None,
                       authentication_policy=None, authorization_policy=None,
                       renderers=DEFAULT_RENDERERS, debug_logger=None,
                       locale_negotiator=None, request_factory=None,
                       renderer_globals_factory=None, default_permission=None,
                       session_factory=None, default_view_mapper=None,
                       exceptionresponse_view=default_exceptionresponse_view):
        """ When you pass a non-``None`` ``registry`` argument to the
        :term:`Configurator` constructor, no initial 'setup' is performed
        against the registry.  This is because the registry you pass in may
        have already been initialized for use under :app:`Pyramid` via a
        different configurator.  However, in some circumstances (such as when
        you want to use the Zope 'global` registry instead of a registry
        created as a result of the Configurator constructor), or when you
        want to reset the initial setup of a registry, you *do* want to
        explicitly initialize the registry associated with a Configurator for
        use under :app:`Pyramid`.  Use ``setup_registry`` to do this
        initialization.

        ``setup_registry`` configures settings, a root factory, security
        policies, renderers, a debug logger, a locale negotiator, and various
        other settings using the configurator's current registry, as per the
        descriptions in the Configurator constructor."""
        tweens = []
        includes = []
        if settings:
            includes = [x.strip() for x in
                        settings.get('pyramid.include', '').splitlines()]
            tweens =   [x.strip() for x in
                        settings.get('pyramid.tweens','').splitlines()]
        registry = self.registry
        self._fix_registry()
        self._set_settings(settings)
        self._set_root_factory(root_factory)
        # cope with WebOb response objects that aren't decorated with IResponse
        from webob import Response as WebobResponse
        # cope with WebOb exc objects not decoratored with IExceptionResponse
        from webob.exc import WSGIHTTPException as WebobWSGIHTTPException
        registry.registerSelfAdapter((WebobResponse,), IResponse)

        if debug_logger is None:
            debug_logger = logging.getLogger(self.package_name)
        elif isinstance(debug_logger, basestring):
            debug_logger = logging.getLogger(debug_logger)
                
        registry.registerUtility(debug_logger, IDebugLogger)
        if authentication_policy or authorization_policy:
            self._set_security_policies(authentication_policy,
                                        authorization_policy)
        for name, renderer in renderers:
            self.add_renderer(name, renderer)
        if exceptionresponse_view is not None:
            exceptionresponse_view = self.maybe_dotted(exceptionresponse_view)
            self.add_view(exceptionresponse_view, context=IExceptionResponse)
            self.add_view(exceptionresponse_view,context=WebobWSGIHTTPException)
        if locale_negotiator:
            locale_negotiator = self.maybe_dotted(locale_negotiator)
            registry.registerUtility(locale_negotiator, ILocaleNegotiator)
        if request_factory:
            request_factory = self.maybe_dotted(request_factory)
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
            renderer_globals_factory = self.maybe_dotted(
                renderer_globals_factory)
            self.set_renderer_globals_factory(renderer_globals_factory,
                                              warn=False)
        if default_permission:
            self.set_default_permission(default_permission)
        if session_factory is not None:
            self.set_session_factory(session_factory)
        # commit before adding default_view_mapper, as the
        # exceptionresponse_view above requires the superdefault view
        # mapper
        self.commit()
        if default_view_mapper is not None:
            self.set_view_mapper(default_view_mapper)
            self.commit()
        for inc in includes:
            self.include(inc)
        for factory in tweens:
            self._add_tween(factory, explicit=True)
        
    def hook_zca(self):
        """ Call :func:`zope.component.getSiteManager.sethook` with
        the argument
        :data:`pyramid.threadlocal.get_current_registry`, causing
        the :term:`Zope Component Architecture` 'global' APIs such as
        :func:`zope.component.getSiteManager`,
        :func:`zope.component.getAdapter` and others to use the
        :app:`Pyramid` :term:`application registry` rather than the
        Zope 'global' registry.  If :mod:`zope.component` cannot be
        imported, this method will raise an :exc:`ImportError`."""
        from zope.component import getSiteManager
        getSiteManager.sethook(get_current_registry)

    def unhook_zca(self):
        """ Call :func:`zope.component.getSiteManager.reset` to undo
        the action of
        :meth:`pyramid.config.Configurator.hook_zca`.  If
        :mod:`zope.component` cannot be imported, this method will
        raise an :exc:`ImportError`."""
        from zope.component import getSiteManager
        getSiteManager.reset()

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

    def derive_view(self, view, attr=None, renderer=None):
        """
        Create a :term:`view callable` using the function, instance,
        or class (or :term:`dotted Python name` referring to the same)
        provided as ``view`` object.

        .. warning:: This method is typically only used by :app:`Pyramid`
           framework extension authors, not by :app:`Pyramid` application
           developers.

        This is API is useful to framework extenders who create
        pluggable systems which need to register 'proxy' view
        callables for functions, instances, or classes which meet the
        requirements of being a :app:`Pyramid` view callable.  For
        example, a ``some_other_framework`` function in another
        framework may want to allow a user to supply a view callable,
        but he may want to wrap the view callable in his own before
        registering the wrapper as a :app:`Pyramid` view callable.
        Because a :app:`Pyramid` view callable can be any of a
        number of valid objects, the framework extender will not know
        how to call the user-supplied object.  Running it through
        ``derive_view`` normalizes it to a callable which accepts two
        arguments: ``context`` and ``request``.

        For example:

        .. code-block:: python

           def some_other_framework(user_supplied_view):
               config = Configurator(reg)
               proxy_view = config.derive_view(user_supplied_view)
               def my_wrapper(context, request):
                   do_something_that_mutates(request)
                   return proxy_view(context, request)
               config.add_view(my_wrapper)

        The ``view`` object provided should be one of the following:

        - A function or another non-class callable object that accepts
          a :term:`request` as a single positional argument and which
          returns a :term:`response` object.

        - A function or other non-class callable object that accepts
          two positional arguments, ``context, request`` and which
          returns a :term:`response` object.

        - A class which accepts a single positional argument in its
          constructor named ``request``, and which has a ``__call__``
          method that accepts no arguments that returns a
          :term:`response` object.

        - A class which accepts two positional arguments named
          ``context, request``, and which has a ``__call__`` method
          that accepts no arguments that returns a :term:`response`
          object.

        - A :term:`dotted Python name` which refers to any of the
          kinds of objects above.

        This API returns a callable which accepts the arguments
        ``context, request`` and which returns the result of calling
        the provided ``view`` object.

        The ``attr`` keyword argument is most useful when the view
        object is a class.  It names the method that should be used as
        the callable.  If ``attr`` is not provided, the attribute
        effectively defaults to ``__call__``.  See
        :ref:`class_as_view` for more information.

        The ``renderer`` keyword argument should be a renderer
        name. If supplied, it will cause the returned callable to use
        a :term:`renderer` to convert the user-supplied view result to
        a :term:`response` object.  If a ``renderer`` argument is not
        supplied, the user-supplied view must itself return a
        :term:`response` object.  """
        return self._derive_view(view, attr=attr, renderer=renderer)

    @action_method
    def add_tween(self, tween_factory, alias=None, under=None, over=None):
        """
        Add a 'tween factory'.  A :term:`tween` (a contraction of 'between')
        is a bit of code that sits between the Pyramid router's main request
        handling function and the upstream WSGI component that uses
        :app:`Pyramid` as its 'app'.  This is a feature that may be used by
        Pyramid framework extensions, to provide, for example,
        Pyramid-specific view timing support, bookkeeping code that examines
        exceptions before they are returned to the upstream WSGI application,
        or a variety of other features.  Tweens behave a bit like
        :term:`WSGI` 'middleware' but they have the benefit of running in a
        context in which they have access to the Pyramid :term:`application
        registry` as well as the Pyramid rendering machinery.

        .. note:: You can view the tween ordering configured into a given
                  Pyramid application by using the ``paster ptweens``
                  command.  See :ref:`displaying_tweens`.

        The ``alias`` argument, if it is not ``None``, should be a string.
        The string will represent a value that other callers of ``add_tween``
        may pass as an ``under`` and ``over`` argument instead of a dotted
        name to a tween factory.

        The ``under`` and ``over`` arguments allow the caller of
        ``add_tween`` to provide a hint about where in the tween chain this
        tween factory should be placed when an implicit tween chain is used.
        These hints are only used used when an explicit tween chain is not
        used (when the ``pyramid.tweens`` configuration value is not set).
        Allowable values for ``under`` or ``over`` (or both) are:

        - ``None`` (the default).

        - A :term:`dotted Python name` to a tween factory: a string
          representing the predicted dotted name of a tween factory added in
          a call to ``add_tween`` in the same configuration session.

        - A tween alias: a string representing the predicted value of
          ``alias`` in a separate call to ``add_tween`` in the same
          configuration session
        
        - One of the constants :attr:`pyramid.tweens.MAIN`,
          :attr:`pyramid.tweens.INGRESS`, or :attr:`pyramid.tweens.EXCVIEW`.
        
        ``under`` means 'closer to the main Pyramid application than',
        ``over`` means 'closer to the request ingress than'.

        For example, calling ``add_tween(factory, over=pyramid.tweens.MAIN)``
        will attempt to place the tween factory represented by ``factory``
        directly 'above' (in ``paster ptweens`` order) the main Pyramid
        request handler.  Likewise, calling ``add_tween(factory,
        over=pyramid.tweens.MAIN, under='someothertween')`` will attempt to
        place this tween factory 'above' the main handler but 'below' (a
        fictional) 'someothertween' tween factory (which was presumably added
        via ``add_tween(factory, alias='someothertween')``).

        If an ``under`` or ``over`` value is provided that does not match a
        tween factory dotted name or alias in the current configuration, that
        value will be ignored.  It is not an error to provide an ``under`` or
        ``over`` value that matches an unused tween factory.

        Specifying neither ``over`` nor ``under`` is equivalent to specifying
        ``under=INGRESS``.

        Implicit tween ordering is obviously only best-effort.  Pyramid will
        attempt to present an implicit order of tweens as best it can, but
        the only surefire way to get any particular ordering is to use an
        explicit tween order.  A user may always override the implicit tween
        ordering by using an explicit ``pyramid.tweens`` configuration value
        setting.

        ``alias``, ``under``, and ``over`` arguments are ignored when an
        explicit tween chain is specified using the ``pyramid.tweens``
        configuration value.

        For more information, see :ref:`registering_tweens`.

        .. note:: This feature is new as of Pyramid 1.2.
        """
        return self._add_tween(tween_factory, alias=alias, under=under,
                               over=over, explicit=False)

    def _add_tween(self, tween_factory, alias=None, under=None, over=None,
                   explicit=False):
        tween_factory = self.maybe_dotted(tween_factory)
        name = tween_factory_name(tween_factory)
        if alias in (MAIN, INGRESS):
            raise ConfigurationError('%s is a reserved tween name' % alias)

        if over is INGRESS:
            raise ConfigurationError('%s cannot be over INGRESS' % name)

        if under is MAIN:
            raise ConfigurationError('%s cannot be under MAIN' % name)

        registry = self.registry
        tweens = registry.queryUtility(ITweens)
        if tweens is None:
            tweens = Tweens()
            registry.registerUtility(tweens, ITweens)
            tweens.add_implicit(tween_factory_name(excview_tween_factory),
                                excview_tween_factory, alias=EXCVIEW,
                                over=MAIN)
        if explicit:
            tweens.add_explicit(name, tween_factory)
        else:
            tweens.add_implicit(name, tween_factory, alias=alias, under=under,
                                over=over)
        self.action(('tween', name, explicit))
        if not explicit and alias is not None:
            self.action(('tween', alias, explicit))

    @action_method
    def add_request_handler(self, factory, name): # pragma: no cover
        # XXX bw compat for debugtoolbar
        return self._add_tween(factory, explicit=False)
        
    @action_method
    def add_subscriber(self, subscriber, iface=None):
        """Add an event :term:`subscriber` for the event stream
        implied by the supplied ``iface`` interface.  The
        ``subscriber`` argument represents a callable object (or a
        :term:`dotted Python name` which identifies a callable); it
        will be called with a single object ``event`` whenever
        :app:`Pyramid` emits an :term:`event` associated with the
        ``iface``, which may be an :term:`interface` or a class or a
        :term:`dotted Python name` to a global object representing an
        interface or a class.  Using the default ``iface`` value,
        ``None`` will cause the subscriber to be registered for all
        event types. See :ref:`events_chapter` for more information
        about events and subscribers."""
        dotted = self.maybe_dotted
        subscriber, iface = dotted(subscriber), dotted(iface)
        if iface is None:
            iface = (Interface,)
        if not isinstance(iface, (tuple, list)):
            iface = (iface,)
        def register():
            self.registry.registerHandler(subscriber, iface)
        self.action(None, register)
        return subscriber

    @action_method
    def add_response_adapter(self, adapter, type_or_iface):
        """ When an object of type (or interface) ``type_or_iface`` is
        returned from a view callable, Pyramid will use the adapter
        ``adapter`` to convert it into an object which implements the
        :class:`pyramid.interfaces.IResponse` interface.  If ``adapter`` is
        None, an object returned of type (or interface) ``type_or_iface``
        will itself be used as a response object.

        ``adapter`` and ``type_or_interface`` may be Python objects or
        strings representing dotted names to importable Python global
        objects.

        See :ref:`using_iresponse` for more information."""
        adapter = self.maybe_dotted(adapter)
        type_or_iface = self.maybe_dotted(type_or_iface)
        def register():
            reg = self.registry
            if adapter is None:
                reg.registerSelfAdapter((type_or_iface,), IResponse)
            else:
                reg.registerAdapter(adapter, (type_or_iface,), IResponse)
        self.action((IResponse, type_or_iface), register)

    def add_settings(self, settings=None, **kw):
        """Augment the ``settings`` argument passed in to the Configurator
        constructor with one or more 'setting' key/value pairs.  A setting is
        a single key/value pair in the dictionary-ish object returned from
        the API :attr:`pyramid.registry.Registry.settings` and
        :meth:`pyramid.config.Configurator.get_settings`.

        You may pass a dictionary::

           config.add_settings({'external_uri':'http://example.com'})

        Or a set of key/value pairs::

           config.add_settings(external_uri='http://example.com')

        This function is useful when you need to test code that accesses the
        :attr:`pyramid.registry.Registry.settings` API (or the
        :meth:`pyramid.config.Configurator.get_settings` API) and
        which uses values from that API.
        """
        if settings is None:
            settings = {}
        utility = self.registry.settings
        if utility is None:
            utility = self._set_settings(settings)
        utility.update(settings)
        utility.update(kw)

    def get_settings(self):
        """
        Return a :term:`deployment settings` object for the current
        application.  A deployment settings object is a dictionary-like
        object that contains key/value pairs based on the dictionary passed
        as the ``settings`` argument to the
        :class:`pyramid.config.Configurator` constructor or the
        :func:`pyramid.router.make_app` API.

        .. note:: For backwards compatibility, dictionary keys can also be
           looked up as attributes of the settings object.

        .. note:: the :attr:`pyramid.registry.Registry.settings` API
           performs the same duty.
           """
        return self.registry.settings

    def make_wsgi_app(self):
        """ Commits any pending configuration statements, sends a
        :class:`pyramid.events.ApplicationCreated` event to all listeners,
        adds this configuration's registry to
        :attr:`pyramid.config.global_registries`, and returns a
        :app:`Pyramid` WSGI application representing the committed
        configuration state."""
        self.commit()
        from pyramid.router import Router # avoid circdep
        app = Router(self.registry)
        global_registries.add(self.registry)
        # We push the registry on to the stack here in case any code
        # that depends on the registry threadlocal APIs used in
        # listeners subscribed to the IApplicationCreated event.
        self.manager.push({'registry':self.registry, 'request':None})
        try:
            self.registry.notify(ApplicationCreated(app))
        finally:
            self.manager.pop()

        return app

    @action_method
    def add_view(self, view=None, name="", for_=None, permission=None,
                 request_type=None, route_name=None, request_method=None,
                 request_param=None, containment=None, attr=None,
                 renderer=None, wrapper=None, xhr=False, accept=None,
                 header=None, path_info=None, custom_predicates=(),
                 context=None, decorator=None, mapper=None, http_cache=None):
        """ Add a :term:`view configuration` to the current
        configuration state.  Arguments to ``add_view`` are broken
        down below into *predicate* arguments and *non-predicate*
        arguments.  Predicate arguments narrow the circumstances in
        which the view callable will be invoked when a request is
        presented to :app:`Pyramid`; non-predicate arguments are
        informational.

        Non-Predicate Arguments

        view

          A :term:`view callable` or a :term:`dotted Python name`
          which refers to a view callable.  This argument is required
          unless a ``renderer`` argument also exists.  If a
          ``renderer`` argument is passed, and a ``view`` argument is
          not provided, the view callable defaults to a callable that
          returns an empty dictionary (see
          :ref:`views_which_use_a_renderer`).

        permission

          The name of a :term:`permission` that the user must possess
          in order to invoke the :term:`view callable`.  See
          :ref:`view_security_section` for more information about view
          security and permissions.  If ``permission`` is omitted, a
          *default* permission may be used for this view registration
          if one was named as the
          :class:`pyramid.config.Configurator` constructor's
          ``default_permission`` argument, or if
          :meth:`pyramid.config.Configurator.set_default_permission`
          was used prior to this view registration.  Pass the string
          :data:`pyramid.security.NO_PERMISSION_REQUIRED` as the
          permission argument to explicitly indicate that the view should
          always be executable by entirely anonymous users, regardless of
          the default permission, bypassing any :term:`authorization
          policy` that may be in effect.

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
          string implying a path or :term:`asset specification`
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
          :term:`asset specification` in the form
          ``some.dotted.package_name:relative/path``, making it
          possible to address template assets which live in a
          separate package.

          The ``renderer`` attribute is optional.  If it is not
          defined, the "null" renderer is assumed (no rendering is
          performed and the value is passed back to the upstream
          :app:`Pyramid` machinery unmodified).

        http_cache

          .. note:: This feature is new as of Pyramid 1.1.

          When you supply an ``http_cache`` value to a view configuration,
          the ``Expires`` and ``Cache-Control`` headers of a response
          generated by the associated view callable are modified.  The value
          for ``http_cache`` may be one of the following:

          - A nonzero integer.  If it's a nonzero integer, it's treated as a
            number of seconds.  This number of seconds will be used to
            compute the ``Expires`` header and the ``Cache-Control:
            max-age`` parameter of responses to requests which call this view.
            For example: ``http_cache=3600`` instructs the requesting browser
            to 'cache this response for an hour, please'.

          - A ``datetime.timedelta`` instance.  If it's a
            ``datetime.timedelta`` instance, it will be converted into a
            number of seconds, and that number of seconds will be used to
            compute the ``Expires`` header and the ``Cache-Control:
            max-age`` parameter of responses to requests which call this view.
            For example: ``http_cache=datetime.timedelta(days=1)`` instructs
            the requesting browser to 'cache this response for a day, please'.

          - Zero (``0``).  If the value is zero, the ``Cache-Control`` and
            ``Expires`` headers present in all responses from this view will
            be composed such that client browser cache (and any intermediate
            caches) are instructed to never cache the response.

          - A two-tuple.  If it's a two tuple (e.g. ``http_cache=(1,
            {'public':True})``), the first value in the tuple may be a
            nonzero integer or a ``datetime.timedelta`` instance; in either
            case this value will be used as the number of seconds to cache
            the response.  The second value in the tuple must be a
            dictionary.  The values present in the dictionary will be used as
            input to the ``Cache-Control`` response header.  For example:
            ``http_cache=(3600, {'public':True})`` means 'cache for an hour,
            and add ``public`` to the Cache-Control header of the response'.
            All keys and values supported by the
            ``webob.cachecontrol.CacheControl`` interface may be added to the
            dictionary.  Supplying ``{'public':True}`` is equivalent to
            calling ``response.cache_control.public = True``.

          Providing a non-tuple value as ``http_cache`` is equivalent to
          calling ``response.cache_expires(value)`` within your view's body.

          Providing a two-tuple value as ``http_cache`` is equivalent to
          calling ``response.cache_expires(value[0], **value[1])`` within your
          view's body.

          If you wish to avoid influencing, the ``Expires`` header, and
          instead wish to only influence ``Cache-Control`` headers, pass a
          tuple as ``http_cache`` with the first element of ``None``, e.g.:
          ``(None, {'public':True})``.

          If you wish to prevent a view that uses ``http_cache`` in its
          configuration from having its caching response headers changed by
          this machinery, set ``response.cache_control.prevent_auto = True``
          before returning the response from the view.  This effectively
          disables any HTTP caching done by ``http_cache`` for that response.

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
          ``pyramid.view.render_view_to_response(context, request,
          'wrapper_viewname')``. The context and request of a wrapper
          view is the same context and request of the inner view.  If
          this attribute is unspecified, no view wrapping is done.

        decorator

          A :term:`dotted Python name` to function (or the function itself)
          which will be used to decorate the registered :term:`view
          callable`.  The decorator function will be called with the view
          callable as a single argument.  The view callable it is passed will
          accept ``(context, request)``.  The decorator must return a
          replacement view callable which also accepts ``(context,
          request)``.
          
        mapper

          A Python object or :term:`dotted Python name` which refers to a
          :term:`view mapper`, or ``None``.  By default it is ``None``, which
          indicates that the view should use the default view mapper.  This
          plug-point is useful for Pyramid extension developers, but it's not
          very useful for 'civilians' who are just developing stock Pyramid
          applications. Pay no attention to the man behind the curtain.
          
        Predicate Arguments

        name

          The :term:`view name`.  Read :ref:`traversal_chapter` to
          understand the concept of a view name.

        context

          An object or a :term:`dotted Python name` referring to an
          interface or class object that the :term:`context` must be
          an instance of, *or* the :term:`interface` that the
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
          that must match before this view will be called.

        request_type

          This value should be an :term:`interface` that the
          :term:`request` must provide in order for this view to be
          found and called.  This value exists only for backwards
          compatibility purposes.

        request_method

          This value can be one of the strings ``GET``,
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
          e.g. ``request_param="foo=123"``, then the key (``foo``)
          must both exist in the ``request.params`` dictionary, *and*
          the value must match the right hand side of the expression
          (``123``) for the view to "match" the current request.

        containment

          This value should be a Python class or :term:`interface` (or a
          :term:`dotted Python name`) that an object in the
          :term:`lineage` of the context must provide in order for this view
          to be found and called.  The nodes in your object graph must be
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

        """
        view = self.maybe_dotted(view)
        context = self.maybe_dotted(context)
        for_ = self.maybe_dotted(for_)
        containment = self.maybe_dotted(containment)
        mapper = self.maybe_dotted(mapper)
        decorator = self.maybe_dotted(decorator)

        if not view:
            if renderer:
                def view(context, request):
                    return {}
            else:
                raise ConfigurationError('"view" was not specified and '
                                         'no "renderer" specified')

        if request_type is not None:
            request_type = self.maybe_dotted(request_type)
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
                    header=header, path_info=path_info,
                    custom_predicates=custom_predicates, context=context,
                    mapper = mapper, http_cache = http_cache,
                    )
                view_info = deferred_views.setdefault(route_name, [])
                view_info.append(info)
                return

        order, predicates, phash = _make_predicates(xhr=xhr,
            request_method=request_method, path_info=path_info,
            request_param=request_param, header=header, accept=accept,
            containment=containment, request_type=request_type,
            custom=custom_predicates)

        if context is None:
            context = for_

        r_context = context
        if r_context is None:
            r_context = Interface
        if not IInterface.providedBy(r_context):
            r_context = implementedBy(r_context)

        if isinstance(renderer, basestring):
            renderer = RendererHelper(name=renderer, package=self.package,
                                      registry = self.registry)

        def register(permission=permission, renderer=renderer):
            if renderer is None:
                # use default renderer if one exists
                if self.registry.queryUtility(IRendererFactory) is not None:
                    renderer = RendererHelper(name=None,
                                              package=self.package,
                                              registry=self.registry)

            if permission is None:
                # intent: will be None if no default permission is registered
                permission = self.registry.queryUtility(IDefaultPermission)

            # __no_permission_required__ handled by _secure_view
            deriver = ViewDeriver(registry=self.registry,
                                  permission=permission,
                                  predicates=predicates,
                                  attr=attr,
                                  renderer=renderer,
                                  wrapper_viewname=wrapper,
                                  viewname=name,
                                  accept=accept,
                                  order=order,
                                  phash=phash,
                                  package=self.package,
                                  mapper=mapper,
                                  decorator=decorator,
                                  http_cache=http_cache)
            derived_view = deriver(view)

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
                old_view = registered((IViewClassifier, request_iface,
                                       r_context), view_type, name)
                if old_view is not None:
                    break

            isexc = isexception(context)

            def regclosure():
                if hasattr(derived_view, '__call_permissive__'):
                    view_iface = ISecuredView
                else:
                    view_iface = IView
                self.registry.registerAdapter(
                    derived_view,
                    (IViewClassifier, request_iface, context), view_iface, name
                    )
                if isexc:
                    self.registry.registerAdapter(
                        derived_view,
                        (IExceptionViewClassifier, request_iface, context),
                        view_iface, name)

            is_multiview = IMultiView.providedBy(old_view)
            old_phash = getattr(old_view, '__phash__', DEFAULT_PHASH)

            if old_view is None:
                # - No component was yet registered for any of our I*View
                #   interfaces exactly; this is the first view for this
                #   triad.
                regclosure()

            elif (not is_multiview) and (old_phash == phash):
                # - A single view component was previously registered with
                #   the same predicate hash as this view; this registration
                #   is therefore an override.
                regclosure()

            else:
                # - A view or multiview was already registered for this
                #   triad, and the new view is not an override.

                # XXX we could try to be more efficient here and register
                # a non-secured view for a multiview if none of the
                # multiview's consituent views have a permission
                # associated with them, but this code is getting pretty
                # rough already
                if is_multiview:
                    multiview = old_view
                else:
                    multiview = MultiView(name)
                    old_accept = getattr(old_view, '__accept__', None)
                    old_order = getattr(old_view, '__order__', MAX_ORDER)
                    multiview.add(old_view, old_order, old_accept, old_phash)
                multiview.add(derived_view, order, accept, phash)
                for view_type in (IView, ISecuredView):
                    # unregister any existing views
                    self.registry.adapters.unregister(
                        (IViewClassifier, request_iface, r_context),
                        view_type, name=name)
                    if isexc:
                        self.registry.adapters.unregister(
                            (IExceptionViewClassifier, request_iface,
                             r_context), view_type, name=name)
                self.registry.registerAdapter(
                    multiview,
                    (IViewClassifier, request_iface, context),
                    IMultiView, name=name)
                if isexc:
                    self.registry.registerAdapter(
                        multiview,
                        (IExceptionViewClassifier, request_iface, context),
                        IMultiView, name=name)

        discriminator = [
            'view', context, name, request_type, IView, containment,
            request_param, request_method, route_name, attr,
            xhr, accept, header, path_info]
        discriminator.extend(sorted(custom_predicates))
        discriminator = tuple(discriminator)
        self.action(discriminator, register)

    def _add_view_from_route(self,
                             route_name,
                             view,
                             context,
                             permission,
                             renderer,
                             attr,
                             ):
        if view:
            self.add_view(
                permission=permission,
                context=context,
                view=view,
                name='',
                route_name=route_name,
                renderer=renderer,
                attr=attr,
                )
        else:
            # prevent mistakes due to misunderstanding of how hybrid calls to
            # add_route and add_view interact
            if attr:
                raise ConfigurationError(
                    'view_attr argument not permitted without view '
                    'argument')
            if context:
                raise ConfigurationError(
                    'view_context argument not permitted without view '
                    'argument')
            if permission:
                raise ConfigurationError(
                    'view_permission argument not permitted without view '
                    'argument')
            if renderer:
                raise ConfigurationError(
                    'view_renderer argument not permitted without '
                    'view argument')

        warnings.warn(
            'Passing view-related arguments to add_route() is deprecated as of '
            'Pyramid 1.1.  Use add_view() to associate a view with a route '
            'instead.  See "Deprecations" in "What\'s New in Pyramid 1.1" '
            'within the general Pyramid documentation for further details.',
            DeprecationWarning,
            4)


    @action_method
    def add_route(self,
                  name,
                  pattern=None,
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
                  traverse=None,
                  custom_predicates=(),
                  view_permission=None,
                  renderer=None,
                  view_renderer=None,
                  view_context=None,
                  view_attr=None,
                  use_global_views=False,
                  path=None,
                  pregenerator=None,
                  static=False,
                  ):
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

          A Python object (often a function or a class) or a :term:`dotted
          Python name` which refers to the same object that will generate a
          :app:`Pyramid` root resource object when this route matches. For
          example, ``mypackage.resources.MyFactory``.  If this argument is
          not specified, a default root factory will be used.

        traverse

          If you would like to cause the :term:`context` to be
          something other than the :term:`root` object when this route
          matches, you can spell a traversal pattern as the
          ``traverse`` argument.  This traversal pattern will be used
          as the traversal path: traversal will begin at the root
          object implied by this route (either the global root, or the
          object returned by the ``factory`` associated with this
          route).

          The syntax of the ``traverse`` argument is the same as it is
          for ``pattern``. For example, if the ``pattern`` provided to
          ``add_route`` is ``articles/{article}/edit``, and the
          ``traverse`` argument provided to ``add_route`` is
          ``/{article}``, when a request comes in that causes the route
          to match in such a way that the ``article`` match value is
          '1' (when the request URI is ``/articles/1/edit``), the
          traversal path will be generated as ``/1``.  This means that
          the root object's ``__getitem__`` will be called with the
          name ``1`` during the traversal phase.  If the ``1`` object
          exists, it will become the :term:`context` of the request.
          :ref:`traversal_chapter` has more information about
          traversal.

          If the traversal path contains segment marker names which
          are not present in the ``pattern`` argument, a runtime error
          will occur.  The ``traverse`` pattern should not contain
          segment markers that do not exist in the ``pattern``
          argument.

          A similar combining of routing and traversal is available
          when a route is matched which contains a ``*traverse``
          remainder marker in its pattern (see
          :ref:`using_traverse_in_a_route_pattern`).  The ``traverse``
          argument to add_route allows you to associate route patterns
          with an arbitrary traversal path without using a a
          ``*traverse`` remainder marker; instead you can use other
          match information.

          Note that the ``traverse`` argument to ``add_route`` is
          ignored when attached to a route that has a ``*traverse``
          remainder marker in its pattern.

        pregenerator

           This option should be a callable object that implements the
           :class:`pyramid.interfaces.IRoutePregenerator`
           interface.  A :term:`pregenerator` is a callable called by
           the :mod:`pyramid.url.route_url` function to augment or
           replace the arguments it is passed when generating a URL
           for the route.  This is a feature not often used directly
           by applications, it is meant to be hooked by frameworks
           that use :app:`Pyramid` as a base.

        use_global_views

          When a request matches this route, and view lookup cannot
          find a view which has a ``route_name`` predicate argument
          that matches the route, try to fall back to using a view
          that otherwise matches the context, request, and view name
          (but which does not match the route_name predicate).

        static

          If ``static`` is ``True``, this route will never match an incoming
          request; it will only be useful for URL generation.  By default,
          ``static`` is ``False``.  See :ref:`static_route_narr`.

          .. note:: New in :app:`Pyramid` 1.1.

        Predicate Arguments

        pattern

          The pattern of the route e.g. ``ideas/{idea}``.  This
          argument is required.  See :ref:`route_pattern_syntax`
          for information about the syntax of route patterns.  If the
          pattern doesn't match the current URL, route matching
          continues.

          .. note:: For backwards compatibility purposes (as of
             :app:`Pyramid` 1.0), a ``path`` keyword argument passed
             to this function will be used to represent the pattern
             value if the ``pattern`` argument is ``None``.  If both
             ``path`` and ``pattern`` are passed, ``pattern`` wins.
        
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
          e.g. ``request_param="foo=123"``, then the key
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
          ``info`` and ``request`` and should return either ``True``
          or ``False`` after doing arbitrary evaluation of the info
          and/or the request.  If all custom and non-custom predicate
          callables return ``True`` the associated route will be
          considered viable for a given request.  If any predicate
          callable returns ``False``, route matching continues.  Note
          that the value ``info`` passed to a custom route predicate
          is a dictionary containing matching information; see
          :ref:`custom_route_predicates` for more information about
          ``info``.

        View-Related Arguments

        .. warning:: The arguments described below have been deprecated as of
           :app:`Pyramid` 1.1. *Do not use these for new development; they
           should only be used to support older code bases which depend upon
           them.* Use a separate call to
           :meth:`pyramid.config.Configurator.add_view` to associate a view
           with a route using the ``route_name`` argument.

        view

          .. warning:: Deprecated as of :app:`Pyramid` 1.1.

          A Python object or :term:`dotted Python name` to the same
          object that will be used as a view callable when this route
          matches. e.g. ``mypackage.views.my_view``.

        view_context

          .. warning:: Deprecated as of :app:`Pyramid` 1.1.
          
          A class or an :term:`interface` or :term:`dotted Python
          name` to the same object which the :term:`context` of the
          view should match for the view named by the route to be
          used.  This argument is only useful if the ``view``
          attribute is used.  If this attribute is not specified, the
          default (``None``) will be used.

          If the ``view`` argument is not provided, this argument has
          no effect.

          This attribute can also be spelled as ``for_`` or ``view_for``.

        view_permission

          .. warning:: Deprecated as of :app:`Pyramid` 1.1.

          The permission name required to invoke the view associated
          with this route.  e.g. ``edit``. (see
          :ref:`using_security_with_urldispatch` for more information
          about permissions).

          If the ``view`` attribute is not provided, this argument has
          no effect.

          This argument can also be spelled as ``permission``.

        view_renderer

          .. warning:: Deprecated as of :app:`Pyramid` 1.1.

          This is either a single string term (e.g. ``json``) or a
          string implying a path or :term:`asset specification`
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

          .. warning:: Deprecated as of :app:`Pyramid` 1.1.

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

        """
        # these are route predicates; if they do not match, the next route
        # in the routelist will be tried
        ignored, predicates, ignored = _make_predicates(
            xhr=xhr,
            request_method=request_method,
            path_info=path_info,
            request_param=request_param,
            header=header,
            accept=accept,
            traverse=traverse,
            custom=custom_predicates
            )

        request_iface = self.registry.queryUtility(IRouteRequest, name=name)
        if request_iface is None:
            if use_global_views:
                bases = (IRequest,)
            else:
                bases = ()
            request_iface = route_request_iface(name, bases)
            self.registry.registerUtility(
                request_iface, IRouteRequest, name=name)
            deferred_views = getattr(self.registry, 'deferred_route_views', {})
            view_info = deferred_views.pop(name, ())
            for info in view_info:
                self.add_view(**info)

        # deprecated adding views from add_route
        if any([view, view_context, view_permission, view_renderer,
                view_for, for_, permission, renderer, view_attr]):
            self._add_view_from_route(
                route_name=name,
                view=view,
                permission=view_permission or permission,
                context=view_context or view_for or for_,
                renderer=view_renderer or renderer,
                attr=view_attr,
            )

        mapper = self.get_routes_mapper()

        factory = self.maybe_dotted(factory)
        if pattern is None:
            pattern = path
        if pattern is None:
            raise ConfigurationError('"pattern" argument may not be None')

        if self.route_prefix:
            pattern = self.route_prefix.rstrip('/') + '/' + pattern.lstrip('/')

        discriminator = ('route', name)
        self.action(discriminator, None)

        return mapper.connect(name, pattern, factory, predicates=predicates,
                              pregenerator=pregenerator, static=static)

    def get_routes_mapper(self):
        """ Return the :term:`routes mapper` object associated with
        this configurator's :term:`registry`."""
        mapper = self.registry.queryUtility(IRoutesMapper)
        if mapper is None:
            mapper = RoutesMapper()
            self.registry.registerUtility(mapper, IRoutesMapper)
        return mapper

    # this is *not* an action method (uses caller_package)
    def scan(self, package=None, categories=None, **kw):
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

        scankw = {'config':self}
        scankw.update(kw)

        scanner = self.venusian.Scanner(**scankw)
        scanner.scan(package, categories=categories)

    @action_method
    def add_renderer(self, name, factory):
        """
        Add a :app:`Pyramid` :term:`renderer` factory to the
        current configuration state.

        The ``name`` argument is the renderer name.  Use ``None`` to
        represent the default renderer (a renderer which will be used for all
        views unless they name another renderer specifically).

        The ``factory`` argument is Python reference to an
        implementation of a :term:`renderer` factory or a
        :term:`dotted Python name` to same.

        Note that this function must be called *before* any
        ``add_view`` invocation that names the renderer name as an
        argument.  As a result, it's usually a better idea to pass
        globally used renderers into the ``Configurator`` constructor
        in the sequence of renderers passed as ``renderer`` than it is
        to use this method.
        """
        factory = self.maybe_dotted(factory)
        # if name is None or the empty string, we're trying to register
        # a default renderer, but registerUtility is too dumb to accept None
        # as a name
        if not name: 
            name = ''
        # we need to register renderers eagerly because they are used during
        # view configuration
        self.registry.registerUtility(factory, IRendererFactory, name=name)
        self.action((IRendererFactory, name), None)

    def _override(self, package, path, override_package, override_prefix,
                  PackageOverrides=PackageOverrides):
        pkg_name = package.__name__
        override_pkg_name = override_package.__name__
        override = self.registry.queryUtility(IPackageOverrides, name=pkg_name)
        if override is None:
            override = PackageOverrides(package)
            self.registry.registerUtility(override, IPackageOverrides,
                                          name=pkg_name)
        override.insert(path, override_pkg_name, override_prefix)

    @action_method
    def override_asset(self, to_override, override_with, _override=None):
        """ Add a :app:`Pyramid` asset override to the current
        configuration state.

        ``to_override`` is a :term:`asset specification` to the
        asset being overridden.

        ``override_with`` is a :term:`asset specification` to the
        asset that is performing the override.

        See :ref:`assets_chapter` for more
        information about asset overrides."""
        if to_override == override_with:
            raise ConfigurationError('You cannot override an asset with itself')

        package = to_override
        path = ''
        if ':' in to_override:
            package, path = to_override.split(':', 1)

        override_package = override_with
        override_prefix = ''
        if ':' in override_with:
            override_package, override_prefix = override_with.split(':', 1)

        # *_isdir = override is package or directory
        overridden_isdir = path=='' or path.endswith('/') 
        override_isdir = override_prefix=='' or override_prefix.endswith('/')

        if overridden_isdir and (not override_isdir):
            raise ConfigurationError(
                'A directory cannot be overridden with a file (put a '
                'slash at the end of override_with if necessary)')

        if (not overridden_isdir) and override_isdir:
            raise ConfigurationError(
                'A file cannot be overridden with a directory (put a '
                'slash at the end of to_override if necessary)')

        override = _override or self._override # test jig

        def register():
            __import__(package)
            __import__(override_package)
            from_package = sys.modules[package]
            to_package = sys.modules[override_package]
            override(from_package, path, to_package, override_prefix)
        self.action(None, register)

    override_resource = override_asset # bw compat

    @action_method
    def set_forbidden_view(self, view=None, attr=None, renderer=None,
                           wrapper=None):
        """ Add a default forbidden view to the current configuration
        state.

        .. warning:: This method has been deprecated in :app:`Pyramid`
           1.0.  *Do not use it for new development; it should only be
           used to support older code bases which depend upon it.* See
           :ref:`changing_the_forbidden_view` to see how a forbidden
           view should be registered in new projects.

        The ``view`` argument should be a :term:`view callable` or a
        :term:`dotted Python name` which refers to a view callable.

        The ``attr`` argument should be the attribute of the view
        callable used to retrieve the response (see the ``add_view``
        method's ``attr`` argument for a description).

        The ``renderer`` argument should be the name of (or path to) a
        :term:`renderer` used to generate a response for this view
        (see the
        :meth:`pyramid.config.Configurator.add_view`
        method's ``renderer`` argument for information about how a
        configurator relates to a renderer).

        The ``wrapper`` argument should be the name of another view
        which will wrap this view when rendered (see the ``add_view``
        method's ``wrapper`` argument for a description)."""
        if isinstance(renderer, basestring):
            renderer = RendererHelper(name=renderer, package=self.package,
                                      registry = self.registry)
        view = self._derive_view(view, attr=attr, renderer=renderer)
        def bwcompat_view(context, request):
            context = getattr(request, 'context', None)
            return view(context, request)
        return self.add_view(bwcompat_view, context=HTTPForbidden,
                             wrapper=wrapper, renderer=renderer)

    @action_method
    def set_notfound_view(self, view=None, attr=None, renderer=None,
                          wrapper=None):
        """ Add a default not found view to the current configuration
        state.

        .. warning:: This method has been deprecated in
           :app:`Pyramid` 1.0.  *Do not use it for new development;
           it should only be used to support older code bases which
           depend upon it.* See :ref:`changing_the_notfound_view` to
           see how a not found view should be registered in new
           projects.

        The ``view`` argument should be a :term:`view callable` or a
        :term:`dotted Python name` which refers to a view callable.

        The ``attr`` argument should be the attribute of the view
        callable used to retrieve the response (see the ``add_view``
        method's ``attr`` argument for a description).

        The ``renderer`` argument should be the name of (or path to) a
        :term:`renderer` used to generate a response for this view
        (see the
        :meth:`pyramid.config.Configurator.add_view`
        method's ``renderer`` argument for information about how a
        configurator relates to a renderer).

        The ``wrapper`` argument should be the name of another view
        which will wrap this view when rendered (see the ``add_view``
        method's ``wrapper`` argument for a description).
        """
        if isinstance(renderer, basestring):
            renderer = RendererHelper(name=renderer, package=self.package,
                                      registry=self.registry)
        view = self._derive_view(view, attr=attr, renderer=renderer)
        def bwcompat_view(context, request):
            context = getattr(request, 'context', None)
            return view(context, request)
        return self.add_view(bwcompat_view, context=HTTPNotFound,
                             wrapper=wrapper, renderer=renderer)

    @action_method
    def set_request_factory(self, factory):
        """ The object passed as ``factory`` should be an object (or a
        :term:`dotted Python name` which refers to an object) which
        will be used by the :app:`Pyramid` router to create all
        request objects.  This factory object must have the same
        methods and attributes as the
        :class:`pyramid.request.Request` class (particularly
        ``__call__``, and ``blank``).

        .. note:: Using the ``request_factory`` argument to the
           :class:`pyramid.config.Configurator` constructor
           can be used to achieve the same purpose.
        """
        factory = self.maybe_dotted(factory)
        def register():
            self.registry.registerUtility(factory, IRequestFactory)
        self.action(IRequestFactory, register)

    @action_method
    def set_renderer_globals_factory(self, factory, warn=True):
        """ The object passed as ``factory`` should be an callable (or
        a :term:`dotted Python name` which refers to an callable) that
        will be used by the :app:`Pyramid` rendering machinery as a
        renderers global factory (see :ref:`adding_renderer_globals`).

        The ``factory`` callable must accept a single argument named
        ``system`` (which will be a dictionary) and it must return a
        dictionary.  When an application uses a renderer, the
        factory's return dictionary will be merged into the ``system``
        dictionary, and therefore will be made available to the code
        which uses the renderer.

        .. warning:: This method is deprecated as of Pyramid 1.1.

        .. note:: Using the ``renderer_globals_factory`` argument
           to the :class:`pyramid.config.Configurator` constructor
           can be used to achieve the same purpose.
        """
        if warn:
            warnings.warn(
                'Calling the ``set_renderer_globals`` method of a Configurator '
                'is deprecated as of Pyramid 1.1. Use a BeforeRender event '
                'subscriber as documented in the "Hooks" chapter of the '
                'Pyramid narrative documentation instead',
                DeprecationWarning,
                3)

        factory = self.maybe_dotted(factory)
        def register():
            self.registry.registerUtility(factory, IRendererGlobalsFactory)
        self.action(IRendererGlobalsFactory, register)

    @action_method
    def set_locale_negotiator(self, negotiator):
        """
        Set the :term:`locale negotiator` for this application.  The
        :term:`locale negotiator` is a callable which accepts a
        :term:`request` object and which returns a :term:`locale
        name`.  The ``negotiator`` argument should be the locale
        negotiator implementation or a :term:`dotted Python name`
        which refers to such an implementation.

        Later calls to this method override earlier calls; there can
        be only one locale negotiator active at a time within an
        application.  See :ref:`activating_translation` for more
        information.

        .. note:: Using the ``locale_negotiator`` argument to the
           :class:`pyramid.config.Configurator` constructor
           can be used to achieve the same purpose.
        """
        negotiator = self.maybe_dotted(negotiator)
        def register():
            self.registry.registerUtility(negotiator, ILocaleNegotiator)
        self.action(ILocaleNegotiator, register)

    @action_method
    def set_default_permission(self, permission):
        """
        Set the default permission to be used by all subsequent
        :term:`view configuration` registrations.  ``permission``
        should be a :term:`permission` string to be used as the
        default permission.  An example of a permission
        string:``'view'``.  Adding a default permission makes it
        unnecessary to protect each view configuration with an
        explicit permission, unless your application policy requires
        some exception for a particular view.

        If a default permission is *not* set, views represented by
        view configuration registrations which do not explicitly
        declare a permission will be executable by entirely anonymous
        users (any authorization policy is ignored).

        Later calls to this method override will conflict with earlier calls;
        there can be only one default permission active at a time within an
        application.

        .. warning::

          If a default permission is in effect, view configurations meant to
          create a truly anonymously accessible view (even :term:`exception
          view` views) *must* use the explicit permission string
          :data:`pyramid.security.NO_PERMISSION_REQUIRED` as the permission.
          When this string is used as the ``permission`` for a view
          configuration, the default permission is ignored, and the view is
          registered, making it available to all callers regardless of their
          credentials.

        See also :ref:`setting_a_default_permission`.

        .. note:: Using the ``default_permission`` argument to the
           :class:`pyramid.config.Configurator` constructor
           can be used to achieve the same purpose.
        """
        # default permission used during view registration
        self.registry.registerUtility(permission, IDefaultPermission)
        self.action(IDefaultPermission, None)

    @action_method
    def set_view_mapper(self, mapper):
        """
        Setting a :term:`view mapper` makes it possible to make use of
        :term:`view callable` objects which implement different call
        signatures than the ones supported by :app:`Pyramid` as described in
        its narrative documentation.

        The ``mapper`` should argument be an object implementing
        :class:`pyramid.interfaces.IViewMapperFactory` or a :term:`dotted
        Python name` to such an object.

        The provided ``mapper`` will become the default view mapper to be
        used by all subsequent :term:`view configuration` registrations, as
        if you had passed a ``default_view_mapper`` argument to the
        :class:`pyramid.config.Configurator` constructor.
        
        See also :ref:`using_a_view_mapper`.
        """
        mapper = self.maybe_dotted(mapper)
        self.registry.registerUtility(mapper, IViewMapperFactory)
        self.action(IViewMapperFactory, None)

    @action_method
    def set_session_factory(self, session_factory):
        """
        Configure the application with a :term:`session factory`.  If
        this method is called, the ``session_factory`` argument must
        be a session factory callable.

        .. note:: Using the ``session_factory`` argument to the
           :class:`pyramid.config.Configurator` constructor
           can be used to achieve the same purpose.
        """
        def register():
            self.registry.registerUtility(session_factory, ISessionFactory)
        self.action(ISessionFactory, register)

    def add_translation_dirs(self, *specs):
        """ Add one or more :term:`translation directory` paths to the
        current configuration state.  The ``specs`` argument is a
        sequence that may contain absolute directory paths
        (e.g. ``/usr/share/locale``) or :term:`asset specification`
        names naming a directory path (e.g. ``some.package:locale``)
        or a combination of the two.

        Example:

        .. code-block:: python

           config.add_translation_dirs('/usr/share/locale',
                                       'some.package:locale')

        Later calls to ``add_translation_dir`` insert directories into the
        beginning of the list of translation directories created by earlier
        calls.  This means that the same translation found in a directory
        added later in the configuration process will be found before one
        added earlier in the configuration process.  However, if multiple
        specs are provided in a single call to ``add_translation_dirs``, the
        directories will be inserted into the beginning of the directory list
        in the order they're provided in the ``*specs`` list argument (items
        earlier in the list trump ones later in the list).
        """
        for spec in specs[::-1]: # reversed

            package_name, filename = self._split_spec(spec)
            if package_name is None: # absolute filename
                directory = filename
            else:
                __import__(package_name)
                package = sys.modules[package_name]
                directory = os.path.join(package_path(package), filename)

            if not os.path.isdir(os.path.realpath(directory)):
                raise ConfigurationError('"%s" is not a directory' % directory)

            tdirs = self.registry.queryUtility(ITranslationDirectories)
            if tdirs is None:
                tdirs = []
                self.registry.registerUtility(tdirs, ITranslationDirectories)

            tdirs.insert(0, directory)
            # XXX no action?

        if specs:

            # We actually only need an IChameleonTranslate function
            # utility to be registered zero or one times.  We register the
            # same function once for each added translation directory,
            # which does too much work, but has the same effect.

            ctranslate = ChameleonTranslate(translator)
            self.registry.registerUtility(ctranslate, IChameleonTranslate)

    @action_method
    def add_static_view(self, name, path, **kw):
        """ Add a view used to render static assets such as images
        and CSS files.

        The ``name`` argument is a string representing an
        application-relative local URL prefix.  It may alternately be a full
        URL.

        The ``path`` argument is the path on disk where the static files
        reside.  This can be an absolute path, a package-relative path, or a
        :term:`asset specification`.

        The ``cache_max_age`` keyword argument is input to set the
        ``Expires`` and ``Cache-Control`` headers for static assets served.
        Note that this argument has no effect when the ``name`` is a *url
        prefix*.  By default, this argument is ``None``, meaning that no
        particular Expires or Cache-Control headers are set in the response.

        The ``permission`` keyword argument is used to specify the
        :term:`permission` required by a user to execute the static view.  By
        default, it is the string
        :data:`pyramid.security.NO_PERMISSION_REQUIRED`, a special sentinel
        which indicates that, even if a :term:`default permission` exists for
        the current application, the static view should be renderered to
        completely anonymous users.  This default value is permissive
        because, in most web apps, static assets seldom need protection from
        viewing.  If ``permission`` is specified, the security checking will
        be performed against the default root factory ACL.

        Any other keyword arguments sent to ``add_static_view`` are passed on
        to :meth:`pyramid.config.Configuration.add_route` (e.g. ``factory``,
        perhaps to define a custom factory with a custom ACL for this static
        view).

        *Usage*

        The ``add_static_view`` function is typically used in conjunction
        with the :func:`pyramid.url.static_url` function.
        ``add_static_view`` adds a view which renders a static asset when
        some URL is visited; :func:`pyramid.url.static_url` generates a URL
        to that asset.

        The ``name`` argument to ``add_static_view`` is usually a :term:`view
        name`.  When this is the case, the :func:`pyramid.url.static_url` API
        will generate a URL which points to a Pyramid view, which will serve
        up a set of assets that live in the package itself. For example:

        .. code-block:: python

           add_static_view('images', 'mypackage:images/')

        Code that registers such a view can generate URLs to the view via
        :func:`pyramid.url.static_url`:

        .. code-block:: python

           static_url('mypackage:images/logo.png', request)

        When ``add_static_view`` is called with a ``name`` argument that
        represents a URL prefix, as it is above, subsequent calls to
        :func:`pyramid.url.static_url` with paths that start with the
        ``path`` argument passed to ``add_static_view`` will generate a URL
        something like ``http://<Pyramid app URL>/images/logo.png``, which
        will cause the ``logo.png`` file in the ``images`` subdirectory of
        the ``mypackage`` package to be served.

        ``add_static_view`` can alternately be used with a ``name`` argument
        which is a *URL*, causing static assets to be served from an external
        webserver.  This happens when the ``name`` argument is a fully
        qualified URL (e.g. starts with ``http://`` or similar).  In this
        mode, the ``name`` is used as the prefix of the full URL when
        generating a URL using :func:`pyramid.url.static_url`.  For example,
        if ``add_static_view`` is called like so:

        .. code-block:: python

           add_static_view('http://example.com/images', 'mypackage:images/')

        Subsequently, the URLs generated by :func:`pyramid.url.static_url`
        for that static view will be prefixed with
        ``http://example.com/images``:

        .. code-block:: python

           static_url('mypackage:images/logo.png', request)

        When ``add_static_view`` is called with a ``name`` argument that is
        the URL ``http://example.com/images``, subsequent calls to
        :func:`pyramid.url.static_url` with paths that start with the
        ``path`` argument passed to ``add_static_view`` will generate a URL
        something like ``http://example.com/logo.png``.  The external
        webserver listening on ``example.com`` must be itself configured to
        respond properly to such a request.

        See :ref:`static_assets_section` for more information.
        """
        spec = self._make_spec(path)
        info = self.registry.queryUtility(IStaticURLInfo)
        if info is None:
            info = StaticURLInfo(self)
            self.registry.registerUtility(info, IStaticURLInfo)

        info.add(name, spec, **kw)

    # testing API
    def testing_securitypolicy(self, userid=None, groupids=(),
                               permissive=True):
        """Unit/integration testing helper: Registers a pair of faux
        :app:`Pyramid` security policies: a :term:`authentication
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
        :func:`pyramid.security.authenticated_userid` or
        :func:`pyramid.security.effective_principals` APIs are
        used.

        This function is most useful when testing code that uses
        the APIs named :func:`pyramid.security.has_permission`,
        :func:`pyramid.security.authenticated_userid`,
        :func:`pyramid.security.effective_principals`, and
        :func:`pyramid.security.principals_allowed_by_permission`.
        """
        from pyramid.testing import DummySecurityPolicy
        policy = DummySecurityPolicy(userid, groupids, permissive)
        self.registry.registerUtility(policy, IAuthorizationPolicy)
        self.registry.registerUtility(policy, IAuthenticationPolicy)

    def testing_resources(self, resources):
        """Unit/integration testing helper: registers a dictionary of
        :term:`resource` objects that can be resolved via the
        :func:`pyramid.traversal.find_resource` API.

        The :func:`pyramid.traversal.find_resource` API is called with
        a path as one of its arguments.  If the dictionary you
        register when calling this method contains that path as a
        string key (e.g. ``/foo/bar`` or ``foo/bar``), the
        corresponding value will be returned to ``find_resource`` (and
        thus to your code) when
        :func:`pyramid.traversal.find_resource` is called with an
        equivalent path string or tuple.
        """
        class DummyTraverserFactory:
            def __init__(self, context):
                self.context = context

            def __call__(self, request):
                path = request.environ['PATH_INFO']
                ob = resources[path]
                traversed = traversal_path(path)
                return {'context':ob, 'view_name':'','subpath':(),
                        'traversed':traversed, 'virtual_root':ob,
                        'virtual_root_path':(), 'root':ob}
        self.registry.registerAdapter(DummyTraverserFactory, (Interface,),
                                      ITraverser)
        return resources

    testing_models = testing_resources # b/w compat

    @action_method
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
        :meth:`pyramid.registry.Registry.notify`,
        or :func:`zope.component.event.dispatch`.

        The default value of ``event_iface`` (``None``) implies a
        subscriber registered for *any* kind of event.
        """
        event_iface = self.maybe_dotted(event_iface)
        L = []
        def subscriber(*event):
            L.extend(event)
        self.add_subscriber(subscriber, event_iface)
        return L

    def testing_add_renderer(self, path, renderer=None):
        """Unit/integration testing helper: register a renderer at
        ``path`` (usually a relative filename ala ``templates/foo.pt``
        or an asset specification) and return the renderer object.
        If the ``renderer`` argument is None, a 'dummy' renderer will
        be used.  This function is useful when testing code that calls
        the :func:`pyramid.renderers.render` function or
        :func:`pyramid.renderers.render_to_response` function or
        any other ``render_*`` or ``get_*`` API of the
        :mod:`pyramid.renderers` module.

        Note that calling this method for with a ``path`` argument
        representing a renderer factory type (e.g. for ``foo.pt``
        usually implies the ``chameleon_zpt`` renderer factory)
        clobbers any existing renderer factory registered for that
        type.

        .. note:: This method is also available under the alias
           ``testing_add_template`` (an older name for it).

        """
        from pyramid.testing import DummyRendererFactory
        helper = RendererHelper(name=path, registry=self.registry)
        factory = self.registry.queryUtility(IRendererFactory, name=helper.type)
        if not isinstance(factory, DummyRendererFactory):
            factory = DummyRendererFactory(helper.type, factory)
            self.registry.registerUtility(factory, IRendererFactory,
                                          name=helper.type)

        from pyramid.testing import DummyTemplateRenderer
        if renderer is None:
            renderer = DummyTemplateRenderer()
        factory.add(path, renderer)
        return renderer

    testing_add_template = testing_add_renderer

def _make_predicates(xhr=None, request_method=None, path_info=None,
                     request_param=None, header=None, accept=None,
                     containment=None, request_type=None,
                     traverse=None, custom=()):

    # PREDICATES
    # ----------
    #
    # Given an argument list, a predicate list is computed.
    # Predicates are added to a predicate list in (presumed)
    # computation expense order.  All predicates associated with a
    # view or route must evaluate true for the view or route to
    # "match" during a request.  Elsewhere in the code, we evaluate
    # predicates using a generator expression.  The fastest predicate
    # should be evaluated first, then the next fastest, and so on, as
    # if one returns false, the remainder of the predicates won't need
    # to be evaluated.
    #
    # While we compute predicates, we also compute a predicate hash
    # (aka phash) that can be used by a caller to identify identical
    # predicate lists.
    #
    # ORDERING
    # --------
    #
    # A "order" is computed for the predicate list.  An order is
    # a scoring.
    #
    # Each predicate is associated with a weight value, which is a
    # multiple of 2.  The weight of a predicate symbolizes the
    # relative potential "importance" of the predicate to all other
    # predicates.  A larger weight indicates greater importance.
    #
    # All weights for a given predicate list are bitwise ORed together
    # to create a "score"; this score is then subtracted from
    # MAX_ORDER and divided by an integer representing the number of
    # predicates+1 to determine the order.
    #
    # The order represents the ordering in which a "multiview" ( a
    # collection of views that share the same context/request/name
    # triad but differ in other ways via predicates) will attempt to
    # call its set of views.  Views with lower orders will be tried
    # first.  The intent is to a) ensure that views with more
    # predicates are always evaluated before views with fewer
    # predicates and b) to ensure a stable call ordering of views that
    # share the same number of predicates.  Views which do not have
    # any predicates get an order of MAX_ORDER, meaning that they will
    # be tried very last.

    predicates = []
    weights = []
    h = md5()

    if xhr:
        def xhr_predicate(context, request):
            return request.is_xhr
        xhr_predicate.__text__ = "xhr = True"
        weights.append(1 << 1)
        predicates.append(xhr_predicate)
        h.update('xhr:%r' % bool(xhr))

    if request_method is not None:
        def request_method_predicate(context, request):
            return request.method == request_method
        text = "request method = %s"
        request_method_predicate.__text__ = text % request_method
        weights.append(1 << 2)
        predicates.append(request_method_predicate)
        h.update('request_method:%r' % request_method)

    if path_info is not None:
        try:
            path_info_val = re.compile(path_info)
        except re.error, why:
            raise ConfigurationError(why[0])
        def path_info_predicate(context, request):
            return path_info_val.match(request.path_info) is not None
        text = "path_info = %s"
        path_info_predicate.__text__ = text % path_info
        weights.append(1 << 3)
        predicates.append(path_info_predicate)
        h.update('path_info:%r' % path_info)

    if request_param is not None:
        request_param_val = None
        if '=' in request_param:
            request_param, request_param_val = request_param.split('=', 1)
        if request_param_val is None:
            text = "request_param %s" % request_param
        else:
            text = "request_param %s = %s" % (request_param, request_param_val)
        def request_param_predicate(context, request):
            if request_param_val is None:
                return request_param in request.params
            return request.params.get(request_param) == request_param_val
        request_param_predicate.__text__ = text
        weights.append(1 << 4)
        predicates.append(request_param_predicate)
        h.update('request_param:%r=%r' % (request_param, request_param_val))

    if header is not None:
        header_name = header
        header_val = None
        if ':' in header:
            header_name, header_val = header.split(':', 1)
            try:
                header_val = re.compile(header_val)
            except re.error, why:
                raise ConfigurationError(why[0])
        if header_val is None:
            text = "header %s" % header_name
        else:
            text = "header %s = %s" % (header_name, header_val)
        def header_predicate(context, request):
            if header_val is None:
                return header_name in request.headers
            val = request.headers.get(header_name)
            if val is None:
                return False
            return header_val.match(val) is not None
        header_predicate.__text__ = text
        weights.append(1 << 5)
        predicates.append(header_predicate)
        h.update('header:%r=%r' % (header_name, header_val))

    if accept is not None:
        def accept_predicate(context, request):
            return accept in request.accept
        accept_predicate.__text__ = "accept = %s" % accept
        weights.append(1 << 6)
        predicates.append(accept_predicate)
        h.update('accept:%r' % accept)

    if containment is not None:
        def containment_predicate(context, request):
            return find_interface(context, containment) is not None
        containment_predicate.__text__ = "containment = %s" % containment
        weights.append(1 << 7)
        predicates.append(containment_predicate)
        h.update('containment:%r' % hash(containment))

    if request_type is not None:
        def request_type_predicate(context, request):
            return request_type.providedBy(request)
        text = "request_type = %s"
        request_type_predicate.__text__ = text % request_type
        weights.append(1 << 8)
        predicates.append(request_type_predicate)
        h.update('request_type:%r' % hash(request_type))

    if traverse is not None:
        # ``traverse`` can only be used as a *route* "predicate"; it
        # adds 'traverse' to the matchdict if it's specified in the
        # routing args.  This causes the ResourceTreeTraverser to use
        # the resolved traverse pattern as the traversal path.
        from pyramid.urldispatch import _compile_route
        _, tgenerate = _compile_route(traverse)
        def traverse_predicate(context, request):
            if 'traverse' in context:
                return True
            m = context['match']
            tvalue = tgenerate(m)
            m['traverse'] = traversal_path(tvalue)
            return True
        # This isn't actually a predicate, it's just a infodict
        # modifier that injects ``traverse`` into the matchdict.  As a
        # result, the ``traverse_predicate`` function above always
        # returns True, and we don't need to update the hash or attach
        # a weight to it
        predicates.append(traverse_predicate)

    if custom:
        for num, predicate in enumerate(custom):
            if getattr(predicate, '__text__', None) is None:
                text = '<unknown custom predicate>'
                try:
                    predicate.__text__ = text
                except AttributeError:
                    # if this happens the predicate is probably a classmethod
                    if hasattr(predicate, '__func__'):
                        predicate.__func__.__text__ = text
                    else: # # pragma: no cover ; 2.5 doesn't have __func__ 
                        predicate.im_func.__text__ = text
            predicates.append(predicate)
            # using hash() here rather than id() is intentional: we
            # want to allow custom predicates that are part of
            # frameworks to be able to define custom __hash__
            # functions for custom predicates, so that the hash output
            # of predicate instances which are "logically the same"
            # may compare equal.
            h.update('custom%s:%r' % (num, hash(predicate)))
        weights.append(1 << 10)

    score = 0
    for bit in weights:
        score = score | bit
    order = (MAX_ORDER - score) / (len(predicates) + 1)
    phash = h.hexdigest()
    return order, predicates, phash

class MultiView(object):
    implements(IMultiView)

    def __init__(self, name):
        self.name = name
        self.media_views = {}
        self.views = []
        self.accepts = []

    def add(self, view, order, accept=None, phash=None):
        if phash is not None:
            for i, (s, v, h) in enumerate(list(self.views)):
                if phash == h:
                    self.views[i] = (order, view, phash)
                    return

        if accept is None or '*' in accept:
            self.views.append((order, view, phash))
            self.views.sort()
        else:
            subset = self.media_views.setdefault(accept, [])
            subset.append((order, view, phash))
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
        for order, view, phash in self.get_views(request):
            if not hasattr(view, '__predicated__'):
                return view
            if view.__predicated__(context, request):
                return view
        raise PredicateMismatch(self.name)

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
        for order, view, phash in self.get_views(request):
            try:
                return view(context, request)
            except PredicateMismatch:
                continue
        raise PredicateMismatch(self.name)

def wraps_view(wrapper):
    def inner(self, view):
        wrapper_view = wrapper(self, view)
        return preserve_view_attrs(view, wrapper_view)
    return inner

def preserve_view_attrs(view, wrapper):
    if wrapper is view:
        return view

    original_view = getattr(view, '__original_view__', None)

    if original_view is None:
        original_view = view

    wrapper.__wraps__ = view
    wrapper.__original_view__ = original_view
    wrapper.__module__ = view.__module__
    wrapper.__doc__ = view.__doc__

    try:
        wrapper.__name__ = view.__name__
    except AttributeError:
        wrapper.__name__ = repr(view)

    # attrs that may not exist on "view", but, if so, must be attached to
    # "wrapped view"
    for attr in ('__permitted__', '__call_permissive__', '__permission__',
                 '__predicated__', '__predicates__', '__accept__',
                 '__order__'):
        try:
            setattr(wrapper, attr, getattr(view, attr))
        except AttributeError:
            pass

    return wrapper

class ViewDeriver(object):
    def __init__(self, **kw):
        self.kw = kw
        self.registry = kw['registry']
        self.authn_policy = self.registry.queryUtility(IAuthenticationPolicy)
        self.authz_policy = self.registry.queryUtility(IAuthorizationPolicy)
        self.logger = self.registry.queryUtility(IDebugLogger)

    def __call__(self, view):
        return self.attr_wrapped_view(
            self.predicated_view(
                self.authdebug_view(
                    self.secured_view(
                        self.owrapped_view(
                            self.http_cached_view(
                                self.decorated_view(
                                    self.rendered_view(
                                        self.mapped_view(view)))))))))

    @wraps_view
    def mapped_view(self, view):
        mapper = self.kw.get('mapper')
        if mapper is None:
            mapper = getattr(view, '__view_mapper__', None)
            if mapper is None:
                mapper = self.registry.queryUtility(IViewMapperFactory)
                if mapper is None:
                    mapper = DefaultViewMapper

        mapped_view = mapper(**self.kw)(view)
        return mapped_view

    @wraps_view
    def owrapped_view(self, view):
        wrapper_viewname = self.kw.get('wrapper_viewname')
        viewname = self.kw.get('viewname')
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
        return _owrapped_view

    @wraps_view
    def http_cached_view(self, view):
        if self.registry.settings.get('prevent_http_cache', False):
            return view
        
        seconds = self.kw.get('http_cache')

        if seconds is None:
            return view

        options = {}

        if isinstance(seconds, (tuple, list)):
            try:
                seconds, options = seconds
            except ValueError:
                raise ConfigurationError(
                    'If http_cache parameter is a tuple or list, it must be '
                    'in the form (seconds, options); not %s' % (seconds,))

        def wrapper(context, request):
            response = view(context, request)
            prevent_caching = getattr(response.cache_control, 'prevent_auto',
                                      False)
            if not prevent_caching:
                response.cache_expires(seconds, **options)
            return response

        return wrapper

    @wraps_view
    def secured_view(self, view):
        permission = self.kw.get('permission')
        if permission == NO_PERMISSION_REQUIRED:
            # allow views registered within configurations that have a
            # default permission to explicitly override the default
            # permission, replacing it with no permission at all
            permission = None

        wrapped_view = view
        if self.authn_policy and self.authz_policy and (permission is not None):
            def _permitted(context, request):
                principals = self.authn_policy.effective_principals(request)
                return self.authz_policy.permits(context, principals,
                                                 permission)
            def _secured_view(context, request):
                result = _permitted(context, request)
                if result:
                    return view(context, request)
                msg = getattr(request, 'authdebug_message',
                              'Unauthorized: %s failed permission check' % view)
                raise HTTPForbidden(msg, result=result)
            _secured_view.__call_permissive__ = view
            _secured_view.__permitted__ = _permitted
            _secured_view.__permission__ = permission
            wrapped_view = _secured_view

        return wrapped_view

    @wraps_view
    def authdebug_view(self, view):
        wrapped_view = view
        settings = self.registry.settings
        permission = self.kw.get('permission')
        if settings and settings.get('debug_authorization', False):
            def _authdebug_view(context, request):
                view_name = getattr(request, 'view_name', None)

                if self.authn_policy and self.authz_policy:
                    if permission is None:
                        msg = 'Allowed (no permission registered)'
                    else:
                        principals = self.authn_policy.effective_principals(
                            request)
                        msg = str(self.authz_policy.permits(context, principals,
                                                            permission))
                else:
                    msg = 'Allowed (no authorization policy in use)'

                view_name = getattr(request, 'view_name', None)
                url = getattr(request, 'url', None)
                msg = ('debug_authorization of url %s (view name %r against '
                       'context %r): %s' % (url, view_name, context, msg))
                self.logger and self.logger.debug(msg)
                if request is not None:
                    request.authdebug_message = msg
                return view(context, request)

            wrapped_view = _authdebug_view

        return wrapped_view

    @wraps_view
    def predicated_view(self, view):
        predicates = self.kw.get('predicates', ())
        if not predicates:
            return view
        def predicate_wrapper(context, request):
            if all((predicate(context, request) for predicate in predicates)):
                return view(context, request)
            raise PredicateMismatch(
                'predicate mismatch for view %s' % view)
        def checker(context, request):
            return all((predicate(context, request) for predicate in
                        predicates))
        predicate_wrapper.__predicated__ = checker
        predicate_wrapper.__predicates__ = predicates
        return predicate_wrapper

    @wraps_view
    def attr_wrapped_view(self, view):
        kw = self.kw
        accept, order, phash = (kw.get('accept', None),
                                kw.get('order', MAX_ORDER),
                                kw.get('phash', DEFAULT_PHASH))
        # this is a little silly but we don't want to decorate the original
        # function with attributes that indicate accept, order, and phash,
        # so we use a wrapper
        if (
            (accept is None) and
            (order == MAX_ORDER) and
            (phash == DEFAULT_PHASH)
            ):
            return view # defaults
        def attr_view(context, request):
            return view(context, request)
        attr_view.__accept__ = accept
        attr_view.__order__ = order
        attr_view.__phash__ = phash
        attr_view.__view_attr__ = self.kw.get('attr')
        attr_view.__permission__ = self.kw.get('permission')
        return attr_view

    @wraps_view
    def rendered_view(self, view):
        # one way or another this wrapper must produce a Response (unless
        # the renderer is a NullRendererHelper)
        renderer = self.kw.get('renderer')
        if renderer is None:
            # register a default renderer if you want super-dynamic
            # rendering.  registering a default renderer will also allow
            # override_renderer to work if a renderer is left unspecified for
            # a view registration.
            return self._response_resolved_view(view)
        if renderer is renderers.null_renderer:
            return view
        return self._rendered_view(view, renderer)

    def _rendered_view(self, view, view_renderer):
        def rendered_view(context, request):
            renderer = view_renderer
            result = view(context, request)
            registry = self.registry
            # this must adapt, it can't do a simple interface check
            # (avoid trying to render webob responses)
            response = registry.queryAdapterOrSelf(result, IResponse)
            if response is None:
                attrs = getattr(request, '__dict__', {})
                if 'override_renderer' in attrs:
                    # renderer overridden by newrequest event or other
                    renderer_name = attrs.pop('override_renderer')
                    renderer = RendererHelper(name=renderer_name,
                                              package=self.kw.get('package'),
                                              registry = registry)
                if '__view__' in attrs:
                    view_inst = attrs.pop('__view__')
                else:
                    view_inst = getattr(view, '__original_view__', view)
                response = renderer.render_view(request, result, view_inst,
                                                context)
            return response

        return rendered_view

    def _response_resolved_view(self, view):
        registry = self.registry
        def viewresult_to_response(context, request):
            result = view(context, request)
            response = registry.queryAdapterOrSelf(result, IResponse)
            if response is None:
                raise ValueError(
                    'Could not convert view return value "%s" into a '
                    'response object' % (result,))
            return response

        return viewresult_to_response

    @wraps_view
    def decorated_view(self, view):
        decorator = self.kw.get('decorator')
        if decorator is None:
            return view
        return decorator(view)

class DefaultViewMapper(object):
    classProvides(IViewMapperFactory)
    implements(IViewMapper)
    def __init__(self, **kw):
        self.attr = kw.get('attr')

    def __call__(self, view):
        if inspect.isclass(view):
            view = self.map_class(view)
        else:
            view = self.map_nonclass(view)
        return view

    def map_class(self, view):
        ronly = requestonly(view, self.attr)
        if ronly:
            mapped_view = self.map_class_requestonly(view)
        else:
            mapped_view = self.map_class_native(view)
        return mapped_view

    def map_nonclass(self, view):
        # We do more work here than appears necessary to avoid wrapping the
        # view unless it actually requires wrapping (to avoid function call
        # overhead).
        mapped_view = view
        ronly = requestonly(view, self.attr)
        if ronly:
            mapped_view = self.map_nonclass_requestonly(view)
        elif self.attr:
            mapped_view = self.map_nonclass_attr(view)
        return mapped_view
        
    def map_class_requestonly(self, view):
        # its a class that has an __init__ which only accepts request
        attr = self.attr
        def _class_requestonly_view(context, request):
            inst = view(request)
            request.__view__ = inst
            if attr is None:
                response = inst()
            else:
                response = getattr(inst, attr)()
            return response
        return _class_requestonly_view

    def map_class_native(self, view):
        # its a class that has an __init__ which accepts both context and
        # request
        attr = self.attr
        def _class_view(context, request):
            inst = view(context, request)
            request.__view__ = inst
            if attr is None:
                response = inst()
            else:
                response = getattr(inst, attr)()
            return response
        return _class_view

    def map_nonclass_requestonly(self, view):
        # its a function that has a __call__ which accepts only a single
        # request argument
        attr = self.attr
        def _requestonly_view(context, request):
            if attr is None:
                response = view(request)
            else:
                response = getattr(view, attr)(request)
            return response
        return _requestonly_view

    def map_nonclass_attr(self, view):
        # its a function that has a __call__ which accepts both context and
        # request, but still has an attr
        def _attr_view(context, request):
            response = getattr(view, self.attr)(context, request)
            return response
        return _attr_view

def requestonly(view, attr=None):
    if attr is None:
        attr = '__call__'
    if inspect.isfunction(view):
        fn = view
    elif inspect.isclass(view):
        try:
            fn = view.__init__
        except AttributeError:
            return False
    else:
        try:
            fn = getattr(view, attr)
        except AttributeError:
            return False

    try:
        argspec = inspect.getargspec(fn)
    except TypeError:
        return False

    args = argspec[0]

    if hasattr(fn, 'im_func'):
        # it's an instance method
        if not args:
            return False
        args = args[1:]
    if not args:
        return False

    if len(args) == 1:
        return True

    defaults = argspec[3]
    if defaults is None:
        defaults = ()

    if args[0] == 'request':
        if len(args) - len(defaults) == 1:
            return True

    return False

class PyramidConfigurationMachine(ConfigurationMachine):
    autocommit = False

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

def translator(msg):
    request = get_current_request()
    localizer = get_localizer(request)
    return localizer.translate(msg)

def isexception(o):
    if IInterface.providedBy(o):
        if IException.isEqualOrExtendedBy(o):
            return True
    return (
        isinstance(o, Exception) or
        (inspect.isclass(o) and (issubclass(o, Exception)))
        )

global_registries = WeakOrderedSet()

