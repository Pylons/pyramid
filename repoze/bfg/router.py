from zope.component import getAdapter
from zope.component.event import dispatch
from zope.interface import directlyProvides

from webob import Request
from webob.exc import HTTPNotFound
from webob.exc import HTTPUnauthorized

from repoze.bfg.events import NewRequest
from repoze.bfg.events import NewResponse
from repoze.bfg.events import WSGIApplicationCreatedEvent

from repoze.bfg.interfaces import ITraverserFactory
from repoze.bfg.interfaces import IRequest

from repoze.bfg.registry import registry_manager
from repoze.bfg.registry import makeRegistry

from repoze.bfg.security import Unauthorized

from repoze.bfg.view import is_response
from repoze.bfg.view import render_view_to_response

_marker = ()

class Router:
    """ WSGI application which routes requests to 'view' code based on
    a view registry"""
    def __init__(self, root_policy, registry):
        self.root_policy = root_policy
        self.registry = registry

    def __call__(self, environ, start_response):
        registry_manager.set(self.registry)
        request = Request(environ)
        directlyProvides(request, IRequest)
        dispatch(NewRequest(request))
        root = self.root_policy(environ)
        traverser = getAdapter(root, ITraverserFactory)
        context, name, subpath = traverser(environ)

        request.context = context
        request.view_name = name
        request.subpath = subpath

        try:
            response = render_view_to_response(context, request, name,
                                               secure=True)
        except Unauthorized, why:
            app = HTTPUnauthorized()
            app.explanation = str(why)
            return app(environ, start_response)

        if response is None:
            app = HTTPNotFound(request.url)
            return app(environ, start_response)

        if not is_response(response):
            raise ValueError('response did not implement IResponse: %r'
                             % response)

        dispatch(NewResponse(response))

        start_response(response.status, response.headerlist)
        return response.app_iter

def make_app(root_policy, package=None, filename='configure.zcml',
             options=None):
    """ Create a view registry based on the application's ZCML.  and
    return a Router object, representing a ``repoze.bfg`` WSGI
    application.  ``root_policy`` must be a callable that accepts a
    WSGI environment and returns a graph root object.  ``package`` is
    a Python module representing the application's package,
    ``filename`` is the filesystem path to a ZCML file (optionally
    relative to the package path) that should be parsed to create the
    view registry.  ``options``, if used, should be a dictionary
    containing bfg-specific runtime options, with each key
    representing the option and the key's value representing the
    specific option value, e.g. ``{'reload_templates':True}``"""
    registry = makeRegistry(filename, package, options)
    app = Router(root_policy, registry)

    try:
        registry_manager.set(registry)
        dispatch(WSGIApplicationCreatedEvent(app))
    finally:
        registry_manager.clear()

    return app

    
