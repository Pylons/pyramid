from cgi import escape
import sys
from webob import Response

from zope.interface import providedBy
from zope.component.event import dispatch
from zope.component import queryUtility

from zope.interface import implements

from repoze.bfg.authorization import ACLAuthorizationPolicy

from repoze.bfg.events import NewRequest
from repoze.bfg.events import NewResponse
from repoze.bfg.events import WSGIApplicationCreatedEvent

from repoze.bfg.interfaces import ILogger
from repoze.bfg.interfaces import IResponseFactory
from repoze.bfg.interfaces import IRootFactory
from repoze.bfg.interfaces import IRouter
from repoze.bfg.interfaces import IRoutesMapper
from repoze.bfg.interfaces import ISettings
from repoze.bfg.interfaces import IForbiddenView
from repoze.bfg.interfaces import INotFoundView
from repoze.bfg.interfaces import IView
from repoze.bfg.interfaces import IViewPermission
from repoze.bfg.interfaces import IAuthorizationPolicy
from repoze.bfg.interfaces import IAuthenticationPolicy
from repoze.bfg.interfaces import IDefaultRootFactory

from repoze.bfg.log import make_stream_logger

from repoze.bfg.registry import Registry
from repoze.bfg.registry import populateRegistry

from repoze.bfg.request import request_factory

from repoze.bfg.security import Allowed

from repoze.bfg.settings import Settings
from repoze.bfg.settings import get_options

from repoze.bfg.threadlocal import manager

from repoze.bfg.traversal import _traverse

from repoze.bfg.urldispatch import RoutesRootFactory

_marker = object()

class Router(object):
    """ The main repoze.bfg WSGI application. """
    implements(IRouter)

    debug_authorization = False
    debug_notfound = False
    threadlocal_manager = manager

    def __init__(self, registry):
        self.registry = registry
        self.logger = registry.queryUtility(ILogger, 'repoze.bfg.debug')
        self.forbidden_view = registry.queryUtility(
            IForbiddenView, default=default_forbidden_view)
        self.notfound_view = registry.queryUtility(
            INotFoundView, default=default_notfound_view)
        settings = registry.queryUtility(ISettings)
        if settings is not None:
            self.debug_authorization = settings.debug_authorization
            self.debug_notfound = settings.debug_notfound
        self.secured = not not registry.queryUtility(IAuthenticationPolicy)
        self.root_factory = registry.queryUtility(IRootFactory,
                                                  default=DefaultRootFactory)
        self.root_policy = self.root_factory # b/w compat
        self.traverser_warned = {}

    def __call__(self, environ, start_response):
        """
        Accept ``environ`` and ``start_response``; route requests to
        ``repoze.bfg`` views based on registrations within the
        application registry; call ``start_response`` and return an
        iterable.
        """
        registry = self.registry
        logger = self.logger

        threadlocals = {'registry':registry, 'request':None}
        self.threadlocal_manager.push(threadlocals)
 
        try:
            root = self.root_factory(environ)
            request = request_factory(environ)
            threadlocals['request'] = request
            registry.has_listeners and registry.notify(NewRequest(request))

            tdict = _traverse(root, environ, registry)
            if '_deprecation_warning' in tdict:
                warning = tdict.pop('_deprecation_warning')
                if not warning in self.traverser_warned:
                    self.logger and self.logger.warn(warning)
            context, view_name, subpath, traversed, vroot, vroot_path = (
                tdict['context'], tdict['view_name'], tdict['subpath'],
                tdict['traversed'], tdict['virtual_root'],
                tdict['virtual_root_path'])

            # webob.Request's __setattr__ (as of 0.9.5 and lower) is a
            # bottleneck; since we're sure we're using a
            # webob.Request, we can go around its back and set stuff
            # into the environ directly
            attrs = environ.setdefault('webob.adhoc_attrs', {})
            attrs.update(tdict)

            def respond(response, view_name):
                registry.has_listeners and registry.notify(
                    NewResponse(response))
                try:
                    start_response(response.status, response.headerlist)
                    return response.app_iter
                except AttributeError:
                    raise ValueError(
                        'Non-response object returned from view %s: %r' %
                        (view_name, response))

            if self.secured:
                permitted = registry.queryMultiAdapter((context, request),
                                                       IViewPermission,
                                                       name=view_name)
                if permitted is None:
                    if self.debug_authorization:
                        permitted =  Allowed(
                            'Allowed: view name %r against context %r (no '
                            'permission registered).' % (view_name, context))
                    else:
                        permitted = True
                
            else:
                if self.debug_authorization:
                    permitted =  Allowed(
                        'Allowed: view name %r against context %r (no '
                        'authentication policy in use).' % (view_name, context))
                else:
                    permitted = True

            if self.debug_authorization:
                logger and logger.debug(
                    'debug_authorization of url %s (view name %r against '
                    'context %r): %s' % (request.url, view_name, context,
                                         permitted))

            if not permitted:
                if self.debug_authorization:
                    msg = str(permitted)
                else:
                    msg = 'Unauthorized: failed security policy check'
                environ['repoze.bfg.message'] = msg
                return respond(self.forbidden_view(context, request),
                               '<IForbiddenView>')

            view_callable = registry.adapters.lookup(
                map(providedBy, (context, request)), IView, name=view_name,
                default=None)

            if view_callable is None:
                if self.debug_notfound:
                    msg = (
                        'debug_notfound of url %s; path_info: %r, context: %r, '
                        'view_name: %r, subpath: %r, traversed: %r, '
                        'root: %r, vroot: %r,  vroot_path: %r' % (
                        request.url, request.path_info, context, view_name,
                        subpath, traversed, root, vroot, vroot_path)
                        )
                    logger and logger.debug(msg)
                else:
                    msg = request.path_info
                environ['repoze.bfg.message'] = msg
                return respond(self.notfound_view(context, request),
                               '<INotFoundView>')

            response = view_callable(context, request)
            return respond(response, view_name)

        finally:
            self.threadlocal_manager.pop()

def default_view(context, request, status):
    try:
        msg = escape(request.environ['repoze.bfg.message'])
    except KeyError:
        msg = ''
    html = """
    <html>
    <title>%s</title>
    <body>
    <h1>%s</h1>
    <code>%s</code>
    </body>
    </html>
    """ % (status, status, msg)
    headers = [('Content-Length', str(len(html))),
               ('Content-Type', 'text/html')]
    response_factory = queryUtility(IResponseFactory, default=Response)
    return response_factory(status = status,
                            headerlist = headers,
                            app_iter = [html])

def default_forbidden_view(context, request):
    return default_view(context, request, '401 Unauthorized')

def default_notfound_view(context, request):
    return default_view(context, request, '404 Not Found')

def make_app(root_factory, package=None, filename='configure.zcml',
             authentication_policy=None, authorization_policy=None,
             options=None, registry=None, debug_logger=None):
    # registry and debug_logger *only* for unittests
    """ Return a Router object, representing a fully configured
    ``repoze.bfg`` WSGI application.

    ``root_factory`` must be a callable that accepts a WSGI
    environment and returns a traversal root object.  The traversal
    root returned by the root factory is the *default* traversal root;
    it can be overridden on a per-view basis.  ``root_factory`` may be
    ``None``, in which case a 'default default' traversal root is
    used.

    ``package`` is a Python module representing the application's
    package.  It is optional, defaulting to ``None``.  If ``package``
    is ``None``, the ``filename`` passed must be an absolute pathname
    to a ZCML file that represents the application's configuration.

    ``filename`` is the filesystem path to a ZCML file (optionally
    relative to the package path) that should be parsed to create the
    application registry.  It defaults to ``configure.zcml``.

    ``authentication_policy`` should be an object that implements the
    ``repoze.bfg.interfaces.IAuthenticationPolicy`` interface (e.g.
    it might be an instance of
    ``repoze.bfg.authentication.RemoteUserAuthenticationPolicy``) or
    ``None``.  If ``authentication_policy`` is ``None``, no
    authentication or authorization will be performed.  Instead, BFG
    will ignore any view permission assertions in your application and
    imperative security checks performed by your application will
    always return ``True``.

    ``authorization_policy`` is an object that implements the
    ``repoze.bfg.interfaces.IAuthorizationPoicy`` interface
    (notionally) or ``None``.  If the ``authentication_policy``
    argument is ``None``, this argument is ignored entirely because
    being able to authorize access to a user depends on being able to
    authenticate that user.  If the ``authentication_policy`` argument
    is *not* ``None``, and the ``authorization_policy`` argument *is*
    ``None``, the authorization policy defaults to an authorization
    implementation that uses ACLs.

    ``options``, if used, should be a dictionary containing runtime
    options (e.g. the key/value pairs in an app section of a
    PasteDeploy file), with each key representing the option and the
    key's value representing the specific option value,
    e.g. ``{'reload_templates':True}``"""
    if options is None:
        options = {}

    if registry is None:
        regname = filename
        if package:
            regname = package.__name__
        registry = Registry(regname)

    if debug_logger is None:
        debug_logger = make_stream_logger('repoze.bfg.debug', sys.stderr)
    registry.registerUtility(debug_logger, ILogger, 'repoze.bfg.debug')

    settings = Settings(get_options(options))
    registry.registerUtility(settings, ISettings)

    if authentication_policy:
        registry.registerUtility(authentication_policy, IAuthenticationPolicy)
        if authorization_policy is None:
            authorization_policy = ACLAuthorizationPolicy()
        registry.registerUtility(authorization_policy, IAuthorizationPolicy)

    if root_factory is None:
        root_factory = DefaultRootFactory

    # register the *default* root factory so apps can find it later
    registry.registerUtility(root_factory, IDefaultRootFactory)

    mapper = RoutesRootFactory(root_factory)
    registry.registerUtility(mapper, IRoutesMapper)

    populateRegistry(registry, filename, package)

    if mapper.has_routes():
        # if the user had any <route/> statements in his configuration,
        # use the RoutesRootFactory as the IRootFactory; otherwise use the
        # default root factory (optimization; we don't want to go through
        # the Routes logic if we know there are no routes to match)
        root_factory = mapper

    registry.registerUtility(root_factory, IRootFactory)

    app = Router(registry)

    # We push the registry on to the stack here in case any ZCA API is
    # used in listeners subscribed to the WSGIApplicationCreatedEvent
    # we send.
    manager.push({'registry':registry, 'request':None})
    try:
        # use dispatch here instead of registry.notify to make unit
        # tests possible
        dispatch(WSGIApplicationCreatedEvent(app))
    finally:
        manager.pop()

    return app

class DefaultRootFactory:
    __parent__ = None
    __name__ = None
    def __init__(self, environ):
        if 'bfg.routes.matchdict' in environ:
            # provide backwards compatibility for applications which
            # used routes (at least apps without any custom "context
            # factory") in BFG 0.9.X and before
            self.__dict__.update(environ['bfg.routes.matchdict'])

