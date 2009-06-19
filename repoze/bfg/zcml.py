import inspect
import types

from zope.configuration import xmlconfig

from zope.component import getSiteManager
from zope.component import queryUtility

import zope.configuration.config

from zope.configuration.exceptions import ConfigurationError
from zope.configuration.fields import GlobalObject
from zope.configuration.fields import Tokens

from zope.interface import Interface
from zope.interface import implements

from zope.schema import Bool
from zope.schema import TextLine

from repoze.bfg.interfaces import IRoutesMapper
from repoze.bfg.interfaces import IViewPermission
from repoze.bfg.interfaces import INotFoundView
from repoze.bfg.interfaces import IForbiddenView
from repoze.bfg.interfaces import IView

from repoze.bfg.request import DEFAULT_REQUEST_FACTORIES
from repoze.bfg.request import named_request_factories

from repoze.bfg.security import ViewPermissionFactory

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
        try:
            request_factories = _context.request_factories[route_name]
        except KeyError:
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

class IRouteDirective(Interface):
    """ The interface for the ``route`` ZCML directive
    """
    name = TextLine(title=u'name', required=True)
    path = TextLine(title=u'path', required=True)
    view = GlobalObject(title=u'view', required=False)
    permission = TextLine(title=u'permission', required=False)
    factory = GlobalObject(title=u'context factory', required=False)
    minimize = Bool(title=u'minimize', required=False)
    encoding = TextLine(title=u'encoding', required=False)
    static = Bool(title=u'static', required=False)
    filter = GlobalObject(title=u'filter', required=False)
    absolute = Bool(title=u'absolute', required=False)
    member_name = TextLine(title=u'member_name', required=False)
    collection_name = TextLine(title=u'collection_name', required=False)
    request_type = TextLine(title=u'request_type', required=False)
    condition_method = TextLine(title=u'condition_method', required=False)
    condition_subdomain = TextLine(title=u'condition_subdomain', required=False)
    condition_function = GlobalObject(title=u'condition_function',
                                      required=False)
    parent_member_name = TextLine(title=u'parent member_name', required=False)
    parent_collection_name = TextLine(title=u'parent collection_name',
                                      required=False)
    explicit = Bool(title=u'explicit', required=False)
    subdomains = Tokens(title=u'subdomains', required=False,
                        value_type=TextLine())

class Route(zope.configuration.config.GroupingContextDecorator):
    """ Handle ``route`` ZCML directives
    """
    view = None
    permission = None
    factory = None
    minimize = True
    encoding = None
    static = False
    filter = None
    absolute = False
    member_name = None
    collection_name = None
    condition_method = None
    request_type = None
    condition_subdomain = None
    condition_function = None
    parent_member_name = None
    parent_collection_name = None
    subdomains = None
    explicit = False

    implements(zope.configuration.config.IConfigurationContext,
               IRouteDirective)

    def __init__(self, context, path, name, **kw):
        self.validate(**kw)
        self.requirements = {} # mutated by subdirectives
        self.context = context
        self.path = path
        self.name = name
        self.__dict__.update(**kw)

    def validate(self, **kw):
        parent_member_name = kw.get('parent_member_name')
        parent_collection_name = kw.get('parent_collection_name')
        if parent_member_name or parent_collection_name:
            if not (parent_member_name and parent_collection_name):
                raise ConfigurationError(
                    'parent_member_name and parent_collection_name must be '
                    'specified together')

    def after(self):
        context = self.context
        name = self.name
        if not hasattr(context, 'request_factories'):
            context.request_factories = {}
        context.request_factories[name] = named_request_factories(name)

        if self.view:
            view(context, self.permission, None, self.view, '',
                 self.request_type, name)

        method = self.condition_method or self.request_type

        self.context.action(
            discriminator = ('route', self.name, repr(self.requirements),
                             method, self.condition_subdomain,
                             self.condition_function, self.subdomains),
            callable = connect_route,
            args = (self,),
            )

def route_requirement(context, attr, expr):
    route = context.context
    if attr in route.requirements:
        raise ValueError('Duplicate requirement', attr)
    route.requirements[attr] = expr

def connect_route(directive):
    mapper = queryUtility(IRoutesMapper)
    if mapper is None:
        return
    args = [directive.name, directive.path]
    kw = dict(requirements=directive.requirements)
    if directive.minimize:
        kw['_minimize'] = True
    if directive.explicit:
        kw['_explicit'] = True
    if directive.encoding:
        kw['_encoding'] = directive.encoding
    if directive.static:
        kw['_static'] = True
    if directive.filter:
        kw['_filter'] = directive.filter
    if directive.absolute:
        kw['_absolute'] = True
    if directive.member_name:
        kw['_member_name'] = directive.member_name
    if directive.collection_name:
        kw['_collection_name'] = directive.collection_name
    if directive.parent_member_name and directive.parent_collection_name:
            kw['_parent_resource'] = {
                'member_name':directive.parent_member_name,
                'collection_name':directive.parent_collection_name,
                }
    conditions = {}

    # request_type and condition_method are aliases; condition_method
    # "wins"
    if directive.request_type:
        conditions['method'] = directive.request_type
    if directive.condition_method:
        conditions['method'] = directive.condition_method
    if directive.condition_subdomain:
        conditions['sub_domain'] = directive.condition_subdomain
    if directive.condition_function:
        conditions['function'] = directive.condition_function
    if directive.subdomains:
        conditions['sub_domain'] = directive.subdomains
    if conditions:
        kw['conditions'] = conditions

    result = mapper.connect(*args, **kw)
    route = mapper.matchlist[-1]
    route._factory = directive.factory
    context = directive.context
    route.request_factories = context.request_factories[directive.name]
    return result

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

