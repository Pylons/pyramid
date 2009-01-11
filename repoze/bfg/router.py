import sys
from cgi import escape

from zope.component import getAdapter
from zope.component import getUtility
from zope.component import queryUtility
from zope.component.event import dispatch

from zope.interface import directlyProvides
from zope.interface import implements

from webob import Request
from webob.exc import HTTPNotFound
from webob.exc import HTTPUnauthorized

from repoze.bfg.events import NewRequest
from repoze.bfg.events import NewResponse
from repoze.bfg.events import WSGIApplicationCreatedEvent

from repoze.bfg.interfaces import ILogger
from repoze.bfg.interfaces import ITraverserFactory
from repoze.bfg.interfaces import IRequest
from repoze.bfg.interfaces import IRouter
from repoze.bfg.interfaces import IRootFactory
from repoze.bfg.interfaces import ISettings

from repoze.bfg.log import make_stream_logger

from repoze.bfg.registry import registry_manager
from repoze.bfg.registry import makeRegistry
from repoze.bfg.settings import Settings

from repoze.bfg.view import render_view_to_response
from repoze.bfg.view import view_execution_permitted

_marker = ()

class Router(object):
    """ WSGI application which routes requests to 'view' code based on
    a view registry"""

    implements(IRouter)
    
    def __init__(self, registry):
        self.registry = registry

    def __call__(self, environ, start_response):
        registry_manager.set(self.registry)
        request = Request(environ)
        directlyProvides(request, IRequest)
        dispatch(NewRequest(request))

        root_factory = getUtility(IRootFactory)
        root = root_factory(environ)
        traverser = getAdapter(root, ITraverserFactory)
        context, view_name, subpath = traverser(environ)

        request.root = root
        request.context = context
        request.view_name = view_name
        request.subpath = subpath

        permitted = view_execution_permitted(context, request, view_name)

        settings = queryUtility(ISettings)
        debug_authorization = settings and settings.debug_authorization

        if debug_authorization:
            logger = queryUtility(ILogger, 'repoze.bfg.debug')
            logger and logger.debug(
                'debug_authorization of url %s (view name %r against context '
                '%r): %s' % (request.url, view_name, context, permitted.msg)
                )
        if not permitted:
            if debug_authorization:
                msg = permitted.msg
            else:
                msg = 'Unauthorized: failed security policy check'
            app = HTTPUnauthorized(escape(msg))
            return app(environ, start_response)
            
        response = render_view_to_response(context, request, view_name,
                                           secure=False)

        if response is None:
            debug_notfound = settings and settings.debug_notfound
            if debug_notfound:
                logger = queryUtility(ILogger, 'repoze.bfg.debug')
                msg = (
                    'debug_notfound of url %s; path_info: %r, context: %r, '
                    'view_name: %r, subpath: %r' % (
                    request.url, request.path_info, context, view_name, subpath)
                    )
                logger and logger.debug(msg)
            else:
                msg = request.url
            app = HTTPNotFound(escape(msg))
            return app(environ, start_response)

        dispatch(NewResponse(response))

        start_response(response.status, response.headerlist)
        return response.app_iter

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

    registry = makeRegistry(filename, package)
    settings = Settings(options)
    registry.registerUtility(settings, ISettings)
    debug_logger = make_stream_logger('repoze.bfg.debug', sys.stderr)
    registry.registerUtility(debug_logger, ILogger, 'repoze.bfg.debug')
    registry.registerUtility(root_factory, IRootFactory)
    app = Router(registry)

    try:
        registry_manager.set(registry)
        dispatch(WSGIApplicationCreatedEvent(app))
    finally:
        registry_manager.clear()

    return app

