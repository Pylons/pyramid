from zope.configuration.exceptions import ConfigurationError
from zope.configuration.fields import GlobalObject
from zope.configuration.config import ConfigurationMachine
from zope.configuration import xmlconfig

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
from repoze.bfg.interfaces import IView
from repoze.bfg.interfaces import IRouteRequest

from repoze.bfg.authentication import RepozeWho1AuthenticationPolicy
from repoze.bfg.authentication import RemoteUserAuthenticationPolicy
from repoze.bfg.authentication import AuthTktAuthenticationPolicy
from repoze.bfg.authorization import ACLAuthorizationPolicy
from repoze.bfg.request import route_request_iface
from repoze.bfg.threadlocal import get_current_registry
from repoze.bfg.static import StaticRootFactory

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

    reg = get_current_registry()

    if request_type in ('GET', 'HEAD', 'PUT', 'POST', 'DELETE'):
        # b/w compat for 1.0
        request_method = request_type
        request_type = None

    if request_type is not None:
        request_type = _context.resolve(request_type)

    if renderer and '.' in renderer:
        renderer = _context.path(renderer)

    def register():
        config = get_configurator(reg)
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
          permission=None, factory=None, for_=None,
          header=None, xhr=False, accept=None, path_info=None,
          request_method=None, request_param=None, 
          view_permission=None, view_request_method=None,
          view_request_param=None, view_containment=None, view_attr=None,
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

    view_for = view_for or for_
    view_permission = view_permission or permission
    view_renderer = view_renderer or renderer
    if view_renderer and '.' in view_renderer:
        view_renderer = _context.path(view_renderer)

    def register():
        config = get_configurator(reg)
        config.route(
            name,
            path,
            factory=factory,
            header=header,
            xhr=xhr,
            accept=accept,
            path_info=path_info,
            request_method=request_method,
            request_param=request_param,
            view=view,
            view_for=view_for,
            view_permission=view_permission,
            view_request_method=view_request_method,
            view_request_param=view_request_param,
            view_containment=view_containment,
            view_attr=view_attr,
            view_renderer=view_renderer,
            view_header=view_header,
            view_accept=view_accept,
            view_xhr=view_xhr,
            view_path_info=view_path_info,
            _info=_context.info
            )
        
    _context.action(
        discriminator = ('route', name, xhr, request_method, path_info,
                         request_param, header, accept),
        callable = register,
        )

    if view:
        request_iface = reg.queryUtility(IRouteRequest, name=name)
        if request_iface is None:
            request_iface = route_request_iface(name)
            reg.registerUtility(request_iface, IRouteRequest, name=name)
        _context.action(
            discriminator = (
                'view', view_for, '', request_iface, IView,
                view_containment, view_request_param, view_request_method,
                name, view_attr, view_xhr, view_accept, view_header,
                view_path_info),
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

class SystemViewHandler(object):
    def __init__(self, iface):
        self.iface = iface

    def __call__(self, _context, view=None, attr=None, renderer=None,
                 wrapper=None):
        if renderer and '.' in renderer:
            renderer = _context.path(renderer)

        def register(iface=self.iface):
            reg = get_current_registry()
            config = get_configurator(reg)
            config.system_view(iface, view=view, attr=attr, renderer=renderer,
                               wrapper=wrapper, _info=_context.info)

        _context.action(
            discriminator = self.iface,
            callable = register,
            )
        
notfound = SystemViewHandler(INotFoundView)
forbidden = SystemViewHandler(IForbiddenView)

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
    reg = get_current_registry()
    config = get_configurator(reg)

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
    config = get_configurator(reg)
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
    config = get_configurator(reg)
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
    config = get_configurator(reg)
    config.authentication_policy(policy, _info=_context.info)
    _context.action(discriminator=IAuthenticationPolicy)

class IACLAuthorizationPolicyDirective(Interface):
    pass

def aclauthorizationpolicy(_context):
    policy = ACLAuthorizationPolicy()
    # authorization policies must be registered eagerly so they can be
    # found by the view registration machinery
    reg = get_current_registry()
    config = get_configurator(reg)
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
    config = get_configurator(reg)
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
    abspath = _context.path(path)
    reg = get_current_registry()
    config = get_configurator(reg)

    _context.action(
        discriminator = ('route', name, False, None, None, None, None, None),
        callable=config.static,
        args = (name, abspath, cache_max_age, _context.info),
        )

    _context.action(
        discriminator = (
            'view', StaticRootFactory, '', None, IView, None,  None, None,
            name, None, None, None, None, None,
            )
        )

class IScanDirective(Interface):
    package = GlobalObject(
        title=u"The package we'd like to scan.",
        required=True,
        )

def scan(_context, package, martian=martian):
    # martian overrideable only for unit tests
    def register():
        reg = get_current_registry()
        config = get_configurator(reg)
        config.scan(package, _info=_context.info, martian=martian)
    _context.action(discriminator=None, callable=register)

def zcml_configure(name, package):
    """ Given a ZCML filename as ``name`` and a Python package as
    ``package`` which the filename should be relative to, load the
    ZCML into the current ZCML registry.

    .. note:: This feature is new as of :mod:`repoze.bfg` 1.1.
    """
    context = ConfigurationMachine()
    xmlconfig.registerCommonDirectives(context)
    context.package = package
    xmlconfig.include(context, name, package)
    context.execute_actions(clear=False) # the raison d'etre
    return context.actions

file_configure = zcml_configure # backwards compat (>0.8.1)

def get_configurator(reg):
    # dont create a new configurator instance unless necessary, as
    # frames will point to each configurator instance via closures
    # when some configuration methods (such as config.view) are
    # called.
    from repoze.bfg.configuration import Configurator
    try:
        config = reg.get('bfg_configurator')
    except:
        config = None
    if config is None:
        config = Configurator(reg)
    return config
