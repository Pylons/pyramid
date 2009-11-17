from zope.component import getSiteManager
from zope.component import queryUtility

from zope.configuration.exceptions import ConfigurationError
from zope.configuration.fields import GlobalObject

from zope.interface import Interface

from zope.schema import Bool
from zope.schema import Int
from zope.schema import TextLine
from zope.schema import ASCIILine

import martian

from repoze.bfg.interfaces import IAuthenticationPolicy
from repoze.bfg.interfaces import IAuthorizationPolicy
from repoze.bfg.interfaces import IForbiddenView
from repoze.bfg.interfaces import INotFoundView
from repoze.bfg.interfaces import IRendererFactory
from repoze.bfg.interfaces import IRequest
from repoze.bfg.interfaces import IRouteRequest
from repoze.bfg.interfaces import IView

from repoze.bfg.authentication import RepozeWho1AuthenticationPolicy
from repoze.bfg.authentication import RemoteUserAuthenticationPolicy
from repoze.bfg.authentication import AuthTktAuthenticationPolicy
from repoze.bfg.authorization import ACLAuthorizationPolicy
from repoze.bfg.configuration import zcml_configure
from repoze.bfg.configuration import Configurator
from repoze.bfg.path import package_name
from repoze.bfg.request import route_request_iface
from repoze.bfg.resource import resource_spec
from repoze.bfg.static import StaticRootFactory
from repoze.bfg.threadlocal import get_current_registry
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

    reg = get_current_registry()

    if request_type in ('GET', 'HEAD', 'PUT', 'POST', 'DELETE'):
        # b/w compat for 1.0
        request_method = request_type
        request_type = None

    if request_type is None:
        if route_name is None:
            request_type = IRequest
        else:
            request_type = reg.queryUtility(IRouteRequest, name=route_name)
            if request_type is None:
                request_type = route_request_iface(route_name)
                reg.registerUtility(request_type, IRouteRequest,
                                    name=route_name)

    if isinstance(request_type, basestring):
        request_type = _context.resolve(request_type)

    if renderer and '.' in renderer:
        renderer = resource_spec(renderer, package_name(_context.resolve('.')))

    def register():
        config = Configurator(reg)
        config.view(
            permission=permission, for_=for_, view=view, name=name,
            request_type=request_type, route_name=route_name,
            request_method=request_method, request_param=request_param,
            containment=containment, attr=attr, renderer=renderer,
            wrapper=wrapper, xhr=xhr, accept=accept, header=header,
            path_info=path_info, _info=_context.info)

    _context.action(
        discriminator = ('view', for_, name, request_type, IView, containment,
                         request_param, request_method, route_name, attr,
                         xhr, accept, header, path_info),
        callable = register,
        )

_view = view # for directives that take a view arg

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
    reg = get_current_registry()

    if request_type in ('GET', 'HEAD', 'PUT', 'POST', 'DELETE'):
        # b/w compat for 1.0
        view_request_method = request_type
        request_type = None

    request_iface = queryUtility(IRouteRequest, name=name)
    if request_iface is None:
        request_iface = route_request_iface(name)
        reg.registerUtility(request_iface, IRouteRequest, name=name)

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

    def register():
        config = Configurator(reg)
        config.route(
            name, path, factory=factory, header=header,
            xhr=xhr, accept=accept, path_info=path_info,
            request_method=request_method, request_param=request_param,
            _info=_context.info)
        
    _context.action(
        discriminator = ('route', name, xhr, request_method, path_info,
                         request_param, header, accept),
        callable = register,
        )

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
        reg = get_current_registry()
        config = Configurator(reg)
        config.view_utility(view, attr, renderer, wrapper, iface, _context.info)

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

def resource(_context, to_override, override_with):
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

    reg = get_current_registry()
    config = Configurator(reg)

    _context.action(
        discriminator = None,
        callable = config.resource,
        args = (to_override, override_with, _context.info),
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
    reg = get_current_registry()
    config = Configurator(reg)
    config.authentication_policy(policy, _info=_context.info)
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
    reg = get_current_registry()
    config = Configurator(reg)
    config.authentication_policy(policy, _info=_context.info)
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
    reg = get_current_registry()
    config = Configurator(reg)
    config.authentication_policy(policy, _info=_context.info)
    _context.action(discriminator=IAuthenticationPolicy)

class IACLAuthorizationPolicyDirective(Interface):
    pass

def aclauthorizationpolicy(_context):
    policy = ACLAuthorizationPolicy()
    # authorization policies must be registered eagerly so they can be
    # found by the view registration machinery
    reg = get_current_registry()
    config = Configurator(reg)
    config.authorization_policy(policy, _info=_context.info)
    _context.action(discriminator=IAuthorizationPolicy)

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
    reg = get_current_registry()
    config = Configurator(reg)
    config.renderer(factory, name, _info=_context.info)
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
    def register():
        reg = get_current_registry()
        config = Configurator(reg)
        config.scan(package, _info=_context.info, martian=martian)
    _context.action(discriminator=None, callable=register)

class Uncacheable(object):
    """ Include in discriminators of actions which are not cacheable;
    this class only exists for backwards compatibility (<0.8.1)"""

file_configure = zcml_configure # backwards compat (>0.8.1)

