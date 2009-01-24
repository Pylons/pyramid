import sys
from cgi import escape

from zope.component.event import dispatch

from zope.interface import implements

from webob.exc import HTTPUnauthorized

from repoze.bfg.events import NewRequest
from repoze.bfg.events import NewResponse
from repoze.bfg.events import WSGIApplicationCreatedEvent

from repoze.bfg.interfaces import ILogger
from repoze.bfg.interfaces import IRequestFactory
from repoze.bfg.interfaces import IRootFactory
from repoze.bfg.interfaces import IRouter
from repoze.bfg.interfaces import IRoutesMapper
from repoze.bfg.interfaces import ITraverserFactory
from repoze.bfg.interfaces import ISecurityPolicy
from repoze.bfg.interfaces import ISettings
from repoze.bfg.interfaces import IView
from repoze.bfg.interfaces import IViewPermission

from repoze.bfg.log import make_stream_logger

from repoze.bfg.registry import Registry
from repoze.bfg.registry import registry_manager
from repoze.bfg.registry import populateRegistry

from repoze.bfg.request import HTTP_METHOD_FACTORIES
from repoze.bfg.request import Request

from repoze.bfg.settings import Settings

from repoze.bfg.urldispatch import RoutesRootFactory

from repoze.bfg.view import _view_execution_permitted

_marker = object()

class Router(object):
    """ The main repoze.bfg WSGI application. """
    implements(IRouter)
    
    def __init__(self, registry):
        self.registry = registry
        self.settings = registry.queryUtility(ISettings)
        self.request_factory = registry.queryUtility(IRequestFactory)
        self.security_policy = registry.queryUtility(ISecurityPolicy)
        self.logger = registry.queryUtility(ILogger, 'repoze.bfg.debug')

    @property
    def root_policy(self):
        """  Backwards compatibility alias """
        return self.registry.getUtility(IRootFactory)

    def __call__(self, environ, start_response):
        """
        Accept ``environ`` and ``start_response``; route requests to
        ``repoze.bfg`` views based on registrations within the
        application registry; call ``start_response`` and return an
        iterable.
        """
        registry = self.registry
        registry_manager.push(registry)

        try:
            request_factory = self.request_factory
            if request_factory is None:
                method = environ['REQUEST_METHOD']
                request_factory = HTTP_METHOD_FACTORIES.get(method, Request)

            request = request_factory(environ)
            
            registry.has_listeners and registry.notify(NewRequest(request))
            root_factory = registry.getUtility(IRootFactory)
            root = root_factory(environ)
            traverser = registry.getAdapter(root, ITraverserFactory)
            context, view_name, subpath = traverser(environ)

            # XXX webob.Request's __setattr__ is slow here: investigate.
            request.root = root
            request.context = context
            request.view_name = view_name
            request.subpath = subpath

            settings = self.settings

            debug_authorization = settings and settings.debug_authorization
            security_policy = self.security_policy

            permission = None

            if security_policy is not None:
                permission = registry.queryMultiAdapter((context, request),
                                                        IViewPermission,
                                                        name=view_name)

            permitted = _view_execution_permitted(context, request, view_name,
                                                  security_policy, permission,
                                                  debug_authorization)

            logger = self.logger

            if debug_authorization:
                logger and logger.debug(
                    'debug_authorization of url %s (view name %r against '
                    'context %r): %s' % (
                    request.url, view_name, context, permitted)
                    )
            if not permitted:
                if debug_authorization:
                    msg = str(permitted)
                else:
                    msg = 'Unauthorized: failed security policy check'
                app = HTTPUnauthorized(escape(msg))
                return app(environ, start_response)

            response = registry.queryMultiAdapter(
                (context, request), IView, name=view_name)

            if response is None:
                debug_notfound = settings and settings.debug_notfound
                if debug_notfound:
                    msg = (
                        'debug_notfound of url %s; path_info: %r, context: %r, '
                        'view_name: %r, subpath: %r' % (
                        request.url, request.path_info, context, view_name,
                        subpath)
                        )
                    logger and logger.debug(msg)
                else:
                    msg = request.url
                notfound = NotFound(msg)
                start_response(notfound.status, notfound.headerlist)
                return notfound.app_iter

            registry.has_listeners and registry.notify(NewResponse(response))

            try:
                start_response(response.status, response.headerlist)
                return response.app_iter
            except AttributeError:
                raise ValueError(
                    'Non-response object returned from view: %r' % response)

        finally:
            registry_manager.pop()

class NotFound(object):
    """ Avoid using WebOb's NotFound WSGI response app; it's slow. """
    def __init__(self, msg=''):
        html = """<body>
        <html><title>404 Not Found</title><body><h1>404 Not Found</h1>
        <code>%s</code>
        """ % msg
        self.headerlist = [
            ('Content-Length', len(html) ),
            ('Content-Type', 'text/html')
            ]
        self.app_iter = [html]
        self.status = '404 Not Found'

def make_app(root_factory, package=None, filename='configure.zcml',
             options=None):
    """ Return a Router object, representing a ``repoze.bfg`` WSGI
    application.  ``root_factory`` must be a callable that accepts a
    WSGI environment and returns a root object.  ``package`` is a
    Python module representing the application's package, ``filename``
    is the filesystem path to a ZCML file (optionally relative to the
    package path) that should be parsed to create the application
    registry.  ``options``, if used, should be a dictionary containing
    runtime options (e.g. the key/value pairs in an app section of a
    PasteDeploy file), with each key representing the option and the
    key's value representing the specific option value,
    e.g. ``{'reload_templates':True}``"""
    if options is None:
        options = {}
    regname = filename
    if package:
        regname = package.__name__
    registry = Registry(regname)
    debug_logger = make_stream_logger('repoze.bfg.debug', sys.stderr)
    registry.registerUtility(debug_logger, ILogger, 'repoze.bfg.debug')
    settings = Settings(options)
    registry.registerUtility(settings, ISettings)
    mapper = RoutesRootFactory(root_factory)
    registry.registerUtility(mapper, IRoutesMapper)
    populateRegistry(registry, filename, package)
    if mapper.has_routes():
        # if the user had any <route/> statements in his configuration,
        # use the RoutesRootFactory as the root factory
        root_factory = mapper
    else:
        # otherwise, use only the supplied root_factory (unless it's None)
        if root_factory is None:
            raise ValueError(
                'root_factory (aka get_root) was None and no routes connected')

    registry.registerUtility(root_factory, IRootFactory)
    app = Router(registry)

    # We push the registry on to the stack here in case any ZCA API is
    # used in listeners subscribed to the WSGIApplicationCreatedEvent
    # we send.
    registry_manager.push(registry)
    try:
        # use dispatch here instead of registry.notify to make unit
        # tests possible
        dispatch(WSGIApplicationCreatedEvent(app))
    finally:
        registry_manager.pop()

    return app

