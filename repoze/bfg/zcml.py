import inspect
import types
import pkg_resources

from zope.configuration import xmlconfig

from zope.component import getSiteManager
from zope.component import getUtility
from zope.component import queryUtility

import zope.configuration.config

from zope.configuration.exceptions import ConfigurationError
from zope.configuration.fields import GlobalObject

from zope.interface import Interface

from zope.schema import TextLine

from repoze.bfg.interfaces import IRoutesMapper
from repoze.bfg.interfaces import IViewPermission
from repoze.bfg.interfaces import INotFoundAppFactory
from repoze.bfg.interfaces import INotFoundView
from repoze.bfg.interfaces import IForbiddenView
from repoze.bfg.interfaces import IAuthenticationPolicy
from repoze.bfg.interfaces import ISecurityPolicy
from repoze.bfg.interfaces import IView
from repoze.bfg.interfaces import IUnauthorizedAppFactory
from repoze.bfg.interfaces import ILogger
from repoze.bfg.interfaces import IRequestFactories
from repoze.bfg.interfaces import IPackageOverrides

from repoze.bfg.resource import OverrideProvider
from repoze.bfg.resource import PackageOverrides

from repoze.bfg.request import DEFAULT_REQUEST_FACTORIES
from repoze.bfg.request import named_request_factories

from repoze.bfg.security import ViewPermissionFactory

from repoze.bfg.secpols import registerBBBAuthn


import martian

def handler(methodName, *args, **kwargs):
    method = getattr(getSiteManager(), methodName)
    method(*args, **kwargs)

def view(
    _context,
    permission=None,
    for_=None,
    view=None,
    name="",
    request_type=None,
    route_name=None,
    cacheable=True, # not used, here for b/w compat < 0.8
    ):

    if not view:
        raise ConfigurationError('"view" attribute was not specified')

    if route_name is None:
        request_factories = DEFAULT_REQUEST_FACTORIES
    else:
        request_factories = queryUtility(IRequestFactories, name=route_name)
        if request_factories is None:
            raise ConfigurationError(
                'Unknown route_name "%s".  <route> definitions must be ordered '
                'before the view definition which mentions the route\'s name '
                'within ZCML (or before the "scan" directive is invoked '
                'within a bfg_view decorator).' % route_name)
        
    if request_type in request_factories:
        request_type = request_factories[request_type]['interface']
    else:
        request_type = _context.resolve(request_type)

    derived_view = derive_view(view)

    if permission:
        pfactory = ViewPermissionFactory(permission)
        _context.action(
            discriminator = ('permission', for_, name, request_type,
                             IViewPermission),
            callable = handler,
            args = ('registerAdapter',
                    pfactory, (for_, request_type), IViewPermission, name,
                    _context.info),
            )

    _context.action(
        discriminator = ('view', for_, name, request_type, IView),
        callable = handler,
        args = ('registerAdapter',
                derived_view, (for_, request_type), IView, name, _context.info),
        )

_view = view # for directives that take a view arg

def view_utility(_context, view, iface):
    derived_view = derive_view(view)
    _context.action(
        discriminator = ('notfound_view',),
        callable = handler,
        args = ('registerUtility', derived_view, iface, '', _context.info),
        )

def notfound(_context, view):
    view_utility(_context, view, INotFoundView)

def forbidden(_context, view):
    view_utility(_context, view, IForbiddenView)

def derive_view(view):
    derived_view = view
    if inspect.isclass(view):
        # If the object we've located is a class, turn it into a
        # function that operates like a Zope view (when it's invoked,
        # construct an instance using 'context' and 'request' as
        # position arguments, then immediately invoke the __call__
        # method of the instance with no arguments; __call__ should
        # return an IResponse).
        if requestonly(view):
            # its __init__ accepts only a single request argument,
            # instead of both context and request
            def _bfg_class_requestonly_view(context, request):
                inst = view(request)
                return inst()
            derived_view = _bfg_class_requestonly_view
        else:
            # its __init__ accepts both context and request
            def _bfg_class_view(context, request):
                inst = view(context, request)
                return inst()
            derived_view = _bfg_class_view

    elif requestonly(view):
        # its __call__ accepts only a single request argument,
        # instead of both context and request
        def _bfg_requestonly_view(context, request):
            return view(request)
        derived_view = _bfg_requestonly_view

    if derived_view is not view:
        derived_view.__module__ = view.__module__
        derived_view.__doc__ = view.__doc__
        try:
            derived_view.__name__ = view.__name__
        except AttributeError:
            derived_view.__name__ = repr(view)

    return derived_view
    
def scan(_context, package, martian=martian):
    # martian overrideable only for unit tests
    module_grokker = martian.ModuleGrokker()
    module_grokker.register(BFGViewFunctionGrokker())
    martian.grok_dotted_name(package.__name__, grokker=module_grokker,
                             context=_context, exclude_filter=exclude)

class IResourceDirective(Interface):
    """
    Directive for specifying that one package may override resources from
    another package.
    """
    to_override = TextLine(
        title=u"Override spec",
        description=u'The spec of the resource to override.',
        required=True)
    override_with = TextLine(
        title=u"With spec",
        description=u"The spec of the resource providing the override.",
        required=True)

def _override(package, path, override_package, override_prefix,
              PackageOverrides=PackageOverrides, pkg_resources=pkg_resources):
    # PackageOverrides and pkg_resources kw args for tests
    sm = getSiteManager()
    override = queryUtility(IPackageOverrides, name=package)
    if override is None:
        override = PackageOverrides(package)
        sm.registerUtility(override, IPackageOverrides, name=package)
        # register_loader_type will be called too many times if there
        # is more than one overridden package; that's OK, as our
        # mutation is idempotent
        pkg_resources.register_loader_type(type(None), OverrideProvider)
    override.insert(path, override_package, override_prefix)

def resource(context, to_override, override_with):
    if to_override == override_with:
        raise ConfigurationError('You cannot override a resource with itself')

    package = to_override
    path = ''
    if ':' in to_override:
        package, path = to_override.split(':', 1)

    override_package = override_with
    override_prefix = ''
    if ':' in override_with:
        override_package, override_prefix = override_with.split(':', 1)

    if path.endswith('/'):
        if not override_prefix.endswith('/'):
            raise ConfigurationError(
                'A directory cannot be overridden with a file (put a slash '
                'at the end of override_with if necessary)')

    if override_prefix.endswith('/'):
        if not path.endswith('/'):
            raise ConfigurationError(
                'A file cannot be overridden with a directory (put a slash '
                'at the end of to_override if necessary)')

    package = context.resolve(package).__name__
    override_package = context.resolve(package).__name__

    context.action(
        discriminator = None,
        callable = _override,
        args = (package, path, override_package, override_prefix),
        )

class IRouteDirective(Interface):
    """ The interface for the ``route`` ZCML directive
    """
    name = TextLine(title=u'name', required=True)
    path = TextLine(title=u'path', required=True)
    view = GlobalObject(title=u'view', required=False)
    view_for = GlobalObject(title=u'view_for', required=False)
    permission = TextLine(title=u'permission', required=False)
    factory = GlobalObject(title=u'context factory', required=False)
    request_type = TextLine(title=u'request_type', required=False)

def route(_context, name, path, view=None, view_for=None, permission=None,
          factory=None, request_type=None):
    """ Handle ``route`` ZCML directives
    """
    sm = getSiteManager()
    request_factories = named_request_factories(name)
    sm.registerUtility(request_factories, IRequestFactories, name=name)

    if view:
        _view(_context, permission, view_for, view, '', request_type, name)

    _context.action(
        discriminator = ('route', name, view_for, request_type),
        callable = connect_route,
        args = (name, path, factory),
        )

def connect_route(name, path, factory):
    mapper = getUtility(IRoutesMapper)
    mapper.connect(name, path, factory)

class IViewDirective(Interface):
    for_ = GlobalObject(
        title=u"The interface or class this view is for.",
        required=False
        )

    permission = TextLine(
        title=u"Permission",
        description=u"The permission needed to use the view.",
        required=False
        )

    view = GlobalObject(
        title=u"",
        description=u"The view function",
        required=False,
        )

    name = TextLine(
        title=u"The name of the view",
        description=u"""
        The name shows up in URLs/paths. For example 'foo' or
        'foo.html'.""",
        required=False,
        )

    request_type = TextLine(
        title=u"The request type string or dotted name interface for the view",
        description=(u"The view will be called if the interface represented by "
                     u"'request_type' is implemented by the request.  The "
                     u"default request type is repoze.bfg.interfaces.IRequest"),
        required=False
        )

    route_name = TextLine(
        title = u'The route that must match for this view to be used',
        required = False)

class INotFoundViewDirective(Interface):
    view = GlobalObject(
        title=u"",
        description=u"The notfound view callable",
        required=True,
        )

class IForbiddenViewDirective(Interface):
    view = GlobalObject(
        title=u"",
        description=u"The forbidden view callable",
        required=True,
        )

class IRouteRequirementDirective(Interface):
    """ The interface for the ``requirement`` route subdirective """
    attr = TextLine(title=u'attr', required=True)
    expr = TextLine(title=u'expression', required=True)

class IScanDirective(Interface):
    package = GlobalObject(
        title=u"The package we'd like to scan.",
        required=True,
        )

def zcml_configure(name, package):
    context = zope.configuration.config.ConfigurationMachine()
    xmlconfig.registerCommonDirectives(context)
    context.package = package
    xmlconfig.include(context, name, package)
    context.execute_actions(clear=False)

    logger = queryUtility(ILogger, name='repoze.bfg.debug')
    registry = getSiteManager()

    # persistence means always having to say you're sorry
    
    authentication_policy = registry.queryUtility(IAuthenticationPolicy)

    if not authentication_policy:
        # deal with bw compat of <= 0.8 security policies (deprecated)
        secpol = registry.queryUtility(ISecurityPolicy)
        if secpol is not None:
            logger and logger.warn(
                'Your application is using a repoze.bfg ``ISecurityPolicy`` '
                '(probably registered via ZCML).  This form of security policy '
                'has been deprecated in BFG 0.9.  See the "Security" chapter '
                'of the repoze.bfg documentation to see how to register a more '
                'up to date set of security policies (an authentication '
                'policy and an authorization policy).  ISecurityPolicy-based '
                'security policies will cease to work in a later BFG '
                'release.')
            registerBBBAuthn(secpol, registry)

    forbidden_view = registry.queryUtility(IForbiddenView)
    unauthorized_app_factory = registry.queryUtility(IUnauthorizedAppFactory)

    if unauthorized_app_factory is not None:
        if forbidden_view is None:
            warning = (
                'Instead of registering a utility against the '
                'repoze.bfg.interfaces.IUnauthorizedAppFactory interface '
                'to return a custom forbidden response, you should now '
                'use the "forbidden" ZCML directive.'
                'The IUnauthorizedAppFactory interface was deprecated in '
                'repoze.bfg 0.9 and will be removed in a subsequent version '
                'of repoze.bfg.  See the "Hooks" chapter of the repoze.bfg '
                'documentation for more information about '
                'the forbidden directive.')
            logger and logger.warn(warning)
            def forbidden(context, request):
                app = unauthorized_app_factory()
                response = request.get_response(app)
                return response
            registry.registerUtility(forbidden, IForbiddenView)

    notfound_view = registry.queryUtility(INotFoundView)
    notfound_app_factory = registry.queryUtility(INotFoundAppFactory)

    if notfound_app_factory is not None:
        if notfound_view is None:
            warning = (
                'Instead of registering a utility against the '
                'repoze.bfg.interfaces.INotFoundAppFactory interface '
                'to return a custom notfound response, you should use the '
                '"notfound" ZCML directive. The '
                'INotFoundAppFactory interface was deprecated in'
                'repoze.bfg 0.9 and will be removed in a subsequent version '
                'of repoze.bfg.  See the "Hooks" chapter of the repoze.bfg '
                'documentation for more information about '
                'the "notfound" directive.')
            logger and logger.warn(warning)
            def notfound(context, request):
                app = notfound_app_factory()
                response = request.get_response(app)
                return response
            registry.registerUtility(notfound, INotFoundView)

    return context.actions

file_configure = zcml_configure # backwards compat (>0.8.1)

class BFGViewFunctionGrokker(martian.InstanceGrokker):
    martian.component(types.FunctionType)

    def grok(self, name, obj, **kw):
        if hasattr(obj, '__is_bfg_view__'):
            permission = obj.__permission__
            for_ = obj.__for__
            name = obj.__view_name__
            request_type = obj.__request_type__
            route_name = obj.__route_name__
            context = kw['context']
            view(context, permission=permission, for_=for_,
                 view=obj, name=name, request_type=request_type,
                 route_name=route_name)
            return True
        return False

def exclude(name):
    if name.startswith('.'):
        return True
    return False

def requestonly(class_or_callable):
    """ Return true of the class or callable accepts only a request argument,
    as opposed to something that accepts context, request """
    if inspect.isfunction(class_or_callable):
        fn = class_or_callable
    elif inspect.isclass(class_or_callable):
        try:
            fn = class_or_callable.__init__
        except AttributeError:
            return False
    else:
        try:
            fn = class_or_callable.__call__
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

class Uncacheable(object):
    """ Include in discriminators of actions which are not cacheable;
    this class only exists for backwards compatibility (<0.8.1)"""

