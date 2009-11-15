import re
import sys

from zope.component import getSiteManager
from zope.component import getUtility
from zope.component import queryUtility

from zope.configuration.exceptions import ConfigurationError
from zope.configuration.fields import GlobalObject

from zope.interface import Interface
from zope.interface import implementedBy
from zope.interface.interfaces import IInterface

from zope.schema import Bool
from zope.schema import Int
from zope.schema import TextLine
from zope.schema import ASCIILine

import martian

from repoze.bfg.interfaces import IAuthenticationPolicy
from repoze.bfg.interfaces import IAuthorizationPolicy
from repoze.bfg.interfaces import IForbiddenView
from repoze.bfg.interfaces import IMultiView
from repoze.bfg.interfaces import INotFoundView
from repoze.bfg.interfaces import IPackageOverrides
from repoze.bfg.interfaces import IRendererFactory
from repoze.bfg.interfaces import IRequest
from repoze.bfg.interfaces import IRouteRequest
from repoze.bfg.interfaces import IRoutesMapper
from repoze.bfg.interfaces import ISecuredView
from repoze.bfg.interfaces import IView
from repoze.bfg.interfaces import IViewPermission

from repoze.bfg.authentication import RepozeWho1AuthenticationPolicy
from repoze.bfg.authentication import RemoteUserAuthenticationPolicy
from repoze.bfg.authentication import AuthTktAuthenticationPolicy
from repoze.bfg.authorization import ACLAuthorizationPolicy
from repoze.bfg.configuration import zcml_configure
from repoze.bfg.path import package_name
from repoze.bfg.request import route_request_iface
from repoze.bfg.resource import PackageOverrides
from repoze.bfg.resource import resource_spec
from repoze.bfg.static import StaticRootFactory
from repoze.bfg.traversal import find_interface
from repoze.bfg.view import MultiView
from repoze.bfg.view import derive_view
from repoze.bfg.view import static as static_view

###################### directives ##########################

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
        The name shows up in URLs/paths. For example 'foo' or 'foo.html'.""",
        required=False,
        )

    attr = TextLine(
        title=u'The callable attribute of the view object(default is __call__)',
        description=u'',
        required=False)

    renderer = TextLine(
        title=u'The renderer asssociated with the view',
        description=u'',
        required=False)

    wrapper = TextLine(
        title = u'The *name* of the view that acts as a wrapper for this view.',
        description = u'',
        required=False)

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

    containment = GlobalObject(
        title = u'Dotted name of a containment class or interface',
        required=False)

    request_method = TextLine(
        title = u'Request method name that must be matched (e.g. GET/POST)',
        description = (u'The view will be called if and only if the request '
                       'method (``request.method``) matches this string. This'
                       'functionality replaces the older ``request_type`` '
                       'functionality.'),
        required=False)

    request_param = TextLine(
        title = (u'Request parameter name that must exist in '
                 '``request.params`` for this view to match'),
        description = (u'The view will be called if and only if the request '
                       'parameter exists which matches this string.'),
        required=False)

    xhr = Bool(
        title = (u'True if request has an X-Requested-With header with the '
                 'value "XMLHttpRequest"'),
        description=(u'Useful for detecting AJAX requests issued from '
                     'jQuery, Protoype and other JavaScript libraries'),
        required=False)

    accept = TextLine(
        title = (u'Mimetype(s) that must be present in "Accept" HTTP header '
                 'for the view to match a request'),
        description=(u'Accepts a mimetype match token in the form '
                     '"text/plain", a wildcard mimetype match token in the '
                     'form "text/*" or a match-all wildcard mimetype match '
                     'token in the form "*/*".'),
        required = False)

    header = TextLine(
        title=u'Header name/value pair in the form "name=<regex>"',
        description=u'Regular expression matching for header values',
        required = False)

    path_info = TextLine(
        title = (u'Regular expression which must match the ``PATH_INFO`` '
                 'header for the view to match a request'),
        description=(u'Accepts a regular expression.'),
        required = False)

def _make_predicates(xhr=None, request_method=None, path_info=None,
                     request_param=None, header=None, accept=None,
                     containment=None):
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
    # sys.maxint, meaning that they will be tried very last.

    predicates = []
    weight = sys.maxint

    if xhr:
        def xhr_predicate(context, request):
            return request.is_xhr
        weight = weight - 10
        predicates.append(xhr_predicate)

    if request_method is not None:
        def request_method_predicate(context, request):
            return request.method == request_method
        weight = weight - 20
        predicates.append(request_method_predicate)

    if path_info is not None:
        try:
            path_info_val = re.compile(path_info)
        except re.error, why:
            raise ConfigurationError(why[0])
        def path_info_predicate(context, request):
            return path_info_val.match(request.path_info) is not None
        weight = weight - 30
        predicates.append(path_info_predicate)

    if request_param is not None:
        request_param_val = None
        if '=' in request_param:
            request_param, request_param_val = request_param.split('=', 1)
        def request_param_predicate(context, request):
            if request_param_val is None:
                return request_param in request.params
            return request.params.get(request_param) == request_param_val
        weight = weight - 40
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
        weight = weight - 50
        predicates.append(header_predicate)

    if accept is not None:
        def accept_predicate(context, request):
            return accept in request.accept
        weight = weight - 60
        predicates.append(accept_predicate)

    if containment is not None:
        def containment_predicate(context, request):
            return find_interface(context, containment) is not None
        weight = weight - 70
        predicates.append(containment_predicate)

    # this will be == sys.maxint if no predicates
    score = weight / (len(predicates) + 1)
    return score, predicates

def view(
    _context,
    permission=None,
    for_=None,
    view=None,
    name="",
    request_type=None,
    route_name=None,
    request_method=None,
    request_param=None,
    containment=None,
    attr=None,
    renderer=None,
    wrapper=None,
    xhr=False,
    accept=None,
    header=None,
    path_info=None,
    cacheable=True, # not used, here for b/w compat < 0.8
    ):

    if not view:
        if renderer:
            def view(context, request):
                return {}
        else:
            raise ConfigurationError('"view" attribute was not specified and '
                                     'no renderer specified')

    sm = getSiteManager()

    if request_type in ('GET', 'HEAD', 'PUT', 'POST', 'DELETE'):
        # b/w compat for 1.0
        request_method = request_type
        request_type = None

    if request_type is None:
        if route_name is None:
            request_type = IRequest
        else:
            request_type = queryUtility(IRouteRequest, name=route_name)
            if request_type is None:
                request_type = route_request_iface(route_name)
                sm.registerUtility(request_type, IRouteRequest, name=route_name)

    if isinstance(request_type, basestring):
        request_type = _context.resolve(request_type)

    if renderer and '.' in renderer:
        renderer = resource_spec(renderer, package_name(_context.resolve('.')))

    score, predicates = _make_predicates(
        xhr=xhr, request_method=request_method, path_info=path_info,
        request_param=request_param, header=header, accept=accept,
        containment=containment)

    def register():
        derived_view = derive_view(view, permission, predicates, attr, renderer,
                                   wrapper, name)
        r_for_ = for_
        r_request_type = request_type
        if r_for_ is None:
            r_for_ = Interface
        if not IInterface.providedBy(r_for_):
            r_for_ = implementedBy(r_for_)
        if not IInterface.providedBy(r_request_type):
            r_request_type = implementedBy(r_request_type)
        old_view = sm.adapters.lookup((r_for_, r_request_type), IView,name=name)
        if old_view is None:
            if hasattr(derived_view, '__call_permissive__'):
                sm.registerAdapter(derived_view, (for_, request_type),
                                   ISecuredView, name, _context.info)
                if hasattr(derived_view, '__permitted__'):
                    # bw compat
                    sm.registerAdapter(derived_view.__permitted__,
                                       (for_, request_type), IViewPermission,
                                       name, _context.info)
            else:
                sm.registerAdapter(derived_view, (for_, request_type),
                                   IView, name, _context.info)
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
                multiview.add(old_view, sys.maxint)
            multiview.add(derived_view, score)
            for i in (IView, ISecuredView):
                # unregister any existing views
                sm.adapters.unregister((r_for_, r_request_type), i, name=name)
            sm.registerAdapter(multiview, (for_, request_type), IMultiView,
                               name, _context.info)
            # b/w compat
            sm.registerAdapter(multiview.__permitted__,
                               (for_, request_type), IViewPermission,
                               name, _context.info)
    _context.action(
        discriminator = ('view', for_, name, request_type, IView, containment,
                         request_param, request_method, route_name, attr,
                         xhr, accept, header, path_info),
        callable = register,
        args = (),
        )

_view = view # for directives that take a view arg

class ISystemViewDirective(Interface):
    view = GlobalObject(
        title=u"",
        description=u"The view function",
        required=False,
        )

    attr = TextLine(
        title=u'The callable attribute of the view object(default is __call__)',
        description=u'',
        required=False)

    renderer = TextLine(
        title=u'The renderer asssociated with the view',
        description=u'',
        required=False)

    wrapper = TextLine(
        title = u'The *name* of the view that acts as a wrapper for this view.',
        description = u'',
        required=False)

def notfound(_context, view=None, attr=None, renderer=None, wrapper=None):
    view_utility(_context, view, attr, renderer, wrapper, INotFoundView)

def forbidden(_context, view=None, attr=None, renderer=None, wrapper=None):
    view_utility(_context, view, attr, renderer, wrapper, IForbiddenView)

def view_utility(_context, view, attr, renderer, wrapper, iface):
    if not view:
        if renderer:
            def view(context, request):
                return {}
        else:
            raise ConfigurationError('"view" attribute was not specified and '
                                     'no renderer specified')

    if renderer and '.' in renderer:
        renderer = resource_spec(renderer, package_name(_context.resolve('.')))

    def register():
        derived_view = derive_view(view, attr=attr, renderer_name=renderer,
                                   wrapper_viewname=wrapper)
        sm = getSiteManager()
        sm.registerUtility(derived_view, iface, '', _context.info)

    _context.action(
        discriminator = iface,
        callable = register,
        )

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
              PackageOverrides=PackageOverrides):
    # PackageOverrides kw arg for tests
    sm = getSiteManager()
    pkg_name = package.__name__
    override_pkg_name = override_package.__name__
    override = queryUtility(IPackageOverrides, name=pkg_name)
    if override is None:
        override = PackageOverrides(package)
        sm.registerUtility(override, IPackageOverrides, name=pkg_name)
    override.insert(path, override_pkg_name, override_prefix)

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

    package = context.resolve(package)
    override_package = context.resolve(override_package)

    context.action(
        discriminator = None,
        callable = _override,
        args = (package, path, override_package, override_prefix),
        )

class IRepozeWho1AuthenticationPolicyDirective(Interface):
    identifier_name = TextLine(title=u'identitfier_name', required=False,
                               default=u'auth_tkt')
    callback = GlobalObject(title=u'callback', required=False)

def repozewho1authenticationpolicy(_context, identifier_name='auth_tkt',
                                   callback=None):
    policy = RepozeWho1AuthenticationPolicy(identifier_name=identifier_name,
                                            callback=callback)
    # authentication policies must be registered eagerly so they can
    # be found by the view registration machinery
    sm = getSiteManager()
    sm.registerUtility(policy, IAuthenticationPolicy)
    _context.action(discriminator=IAuthenticationPolicy)

class IRemoteUserAuthenticationPolicyDirective(Interface):
    environ_key = TextLine(title=u'environ_key', required=False,
                           default=u'REMOTE_USER')
    callback = GlobalObject(title=u'callback', required=False)

def remoteuserauthenticationpolicy(_context, environ_key='REMOTE_USER',
                                   callback=None):
    policy = RemoteUserAuthenticationPolicy(environ_key=environ_key,
                                            callback=callback)
    # authentication policies must be registered eagerly so they can
    # be found by the view registration machinery
    sm = getSiteManager()
    sm.registerUtility(policy, IAuthenticationPolicy)
    _context.action(discriminator=IAuthenticationPolicy)

class IAuthTktAuthenticationPolicyDirective(Interface):
    secret = TextLine(title=u'secret', required=True)
    callback = GlobalObject(title=u'callback', required=False)
    cookie_name = ASCIILine(title=u'cookie_name', required=False,
                            default='repoze.bfg.auth_tkt')
    secure = Bool(title=u"secure", required=False, default=False)
    include_ip = Bool(title=u"include_ip", required=False, default=False)
    timeout = Int(title=u"timeout", required=False, default=None)
    reissue_time = Int(title=u"reissue_time", required=False, default=None)
    max_age = Int(title=u"max_age", required=False, default=None)

def authtktauthenticationpolicy(_context,
                                secret,
                                callback=None,
                                cookie_name='repoze.bfg.auth_tkt',
                                secure=False,
                                include_ip=False,
                                timeout=None,
                                reissue_time=None,
                                max_age=None):
    try:
        policy = AuthTktAuthenticationPolicy(secret,
                                             callback=callback,
                                             cookie_name=cookie_name,
                                             secure=secure,
                                             include_ip = include_ip,
                                             timeout = timeout,
                                             reissue_time = reissue_time,
                                             max_age=max_age)
    except ValueError, why:
        raise ConfigurationError(str(why))
    # authentication policies must be registered eagerly so they can
    # be found by the view registration machinery
    sm = getSiteManager()
    sm.registerUtility(policy, IAuthenticationPolicy)
    _context.action(discriminator=IAuthenticationPolicy)

class IACLAuthorizationPolicyDirective(Interface):
    pass

def aclauthorizationpolicy(_context):
    policy = ACLAuthorizationPolicy()
    # authorization policies must be registered eagerly so they can be
    # found by the view registration machinery
    sm = getSiteManager()
    sm.registerUtility(policy, IAuthorizationPolicy)
    _context.action(discriminator=IAuthorizationPolicy)

class IRouteDirective(Interface):
    """ The interface for the ``route`` ZCML directive
    """
    name = TextLine(title=u'name', required=True)
    path = TextLine(title=u'path', required=True)
    factory = GlobalObject(title=u'context factory', required=False)
    view = GlobalObject(title=u'view', required=False)

    view_for = GlobalObject(title=u'view_for', required=False)
    # alias for view_for
    for_ = GlobalObject(title=u'for', required=False)

    view_permission = TextLine(title=u'view_permission', required=False)
    # alias for view_permission
    permission = TextLine(title=u'permission', required=False)

    view_request_type = TextLine(title=u'view_request_type', required=False)
    # alias for view_request_type
    request_type = TextLine(title=u'request_type', required=False)

    view_renderer = TextLine(title=u'view_renderer', required=False)
    # alias for view_renderer
    renderer = TextLine(title=u'renderer', required=False)

    view_request_method = TextLine(title=u'view_request_method', required=False)
    view_containment = GlobalObject(
        title = u'Dotted name of a containment class or interface',
        required=False)
    view_attr = TextLine(title=u'view_attr', required=False)
    view_header = TextLine(title=u'view_header', required=False)
    view_accept = TextLine(title=u'view_accept', required=False)
    view_xhr = Bool(title=u'view_xhr', required=False)
    view_path_info = TextLine(title=u'view_path_info', required=False)

    request_method = TextLine(title=u'request_method', required=False)
    request_param = TextLine(title=u'request_param', required=False)
    header = TextLine(title=u'header', required=False)
    accept = TextLine(title=u'accept', required=False)
    xhr = Bool(title=u'xhr', required=False)
    path_info = TextLine(title=u'path_info', required=False)

def route(_context, name, path, view=None, view_for=None,
          permission=None, factory=None, request_type=None, for_=None,
          header=None, xhr=False, accept=None, path_info=None,
          request_method=None, request_param=None, 
          view_permission=None, view_request_type=None, 
          view_request_method=None, view_request_param=None,
          view_containment=None, view_attr=None,
          renderer=None, view_renderer=None, view_header=None, 
          view_accept=None, view_xhr=False,
          view_path_info=None):
    """ Handle ``route`` ZCML directives
    """
    # the strange ordering of the request kw args above is for b/w
    # compatibility purposes.
    # these are route predicates; if they do not match, the next route
    # in the routelist will be tried
    _, predicates = _make_predicates(xhr=xhr,
                                     request_method=request_method,
                                     path_info=path_info,
                                     request_param=request_param,
                                     header=header,
                                     accept=accept)

    sm = getSiteManager()

    if request_type in ('GET', 'HEAD', 'PUT', 'POST', 'DELETE'):
        # b/w compat for 1.0
        view_request_method = request_type
        request_type = None

    request_iface = queryUtility(IRouteRequest, name=name)
    if request_iface is None:
        request_iface = route_request_iface(name)
        sm.registerUtility(request_iface, IRouteRequest, name=name)

    if view:
        view_for = view_for or for_
        view_request_type = view_request_type or request_type
        view_permission = view_permission or permission
        view_renderer = view_renderer or renderer
        _view(
            _context,
            permission=view_permission,
            for_=view_for,
            view=view,
            name='',
            request_type=view_request_type,
            route_name=name, 
            request_method=view_request_method,
            request_param=view_request_param,
            containment=view_containment,
            attr=view_attr,
            renderer=view_renderer,
            header=view_header,
            accept=view_accept,
            xhr=view_xhr,
            path_info=view_path_info,
            )

    _context.action(
        discriminator = ('route', name, xhr, request_method, path_info,
                         request_param, header, accept),
        callable = connect_route,
        args = (path, name, factory, predicates),
        )

def connect_route(path, name, factory, predicates):
    mapper = getUtility(IRoutesMapper)
    mapper.connect(path, name, factory, predicates=predicates)

class IRendererDirective(Interface):
    factory = GlobalObject(
        title=u'IRendererFactory implementation',
        required=True)

    name = TextLine(
        title=u'Token (e.g. ``json``) or filename extension (e.g. ".pt")',
        required=False)

def renderer(_context, factory, name=''):
    # renderer factories must be registered eagerly so they can be
    # found by the view machinery
    sm = getSiteManager()
    sm.registerUtility(factory, IRendererFactory, name=name)
    _context.action(discriminator=(IRendererFactory, name))

class IStaticDirective(Interface):
    name = TextLine(
        title=u"The URL prefix of the static view",
        description=u"""
        The directory will be served up for the route that starts with
        this prefix.""",
        required=True)

    path = TextLine(
        title=u'Path to the directory which contains resources',
        description=u'May be package-relative by using a colon to '
        'seperate package name and path relative to the package directory.',
        required=True)

    cache_max_age = Int(
        title=u"Cache maximum age in seconds",
        required=False,
        default=None)

def static(_context, name, path, cache_max_age=3600):
    """ Handle ``static`` ZCML directives
    """
    path = resource_spec(path, package_name(_context.resolve('.')))
    view = static_view(path, cache_max_age=cache_max_age)
    route(_context, name, "%s*subpath" % name, view=view,
          view_for=StaticRootFactory, factory=StaticRootFactory(path))

class IScanDirective(Interface):
    package = GlobalObject(
        title=u"The package we'd like to scan.",
        required=True,
        )

def scan(_context, package, martian=martian):
    # martian overrideable only for unit tests
    multi_grokker = BFGMultiGrokker()
    multi_grokker.register(BFGViewGrokker())
    module_grokker = martian.ModuleGrokker(grokker=multi_grokker)
    martian.grok_dotted_name(package.__name__, grokker=module_grokker,
                             context=_context, exclude_filter=exclude)

################# utility stuff ####################

class BFGViewMarker(object):
    pass

class BFGMultiGrokker(martian.core.MultiInstanceOrClassGrokkerBase):
    def get_bases(self, obj):
        if hasattr(obj, '__bfg_view_settings__'):
            return [BFGViewMarker]
        return []

class BFGViewGrokker(martian.InstanceGrokker):
    martian.component(BFGViewMarker)
    def grok(self, name, obj, **kw):
        config = getattr(obj, '__bfg_view_settings__', [])
        for settings in config:
            view(kw['context'], view=obj, **settings)
        return bool(config)

def exclude(name):
    if name.startswith('.'):
        return True
    return False

class Uncacheable(object):
    """ Include in discriminators of actions which are not cacheable;
    this class only exists for backwards compatibility (<0.8.1)"""

file_configure = zcml_configure # backwards compat (>0.8.1)

