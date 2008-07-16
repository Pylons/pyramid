from zope.component import getMultiAdapter
from zope.component import queryMultiAdapter
from zope.component import queryUtility
from zope.interface import directlyProvides

from webob import Request
from webob.exc import HTTPNotFound
from webob.exc import HTTPUnauthorized

from repoze.bfg.interfaces import IPublishTraverserFactory
from repoze.bfg.interfaces import IViewFactory
from repoze.bfg.interfaces import IViewPermission
from repoze.bfg.interfaces import ISecurityPolicy
from repoze.bfg.interfaces import IWSGIApplicationFactory
from repoze.bfg.interfaces import IRequest

from repoze.bfg.registry import registry_manager

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
        root = self.root_policy(environ)
        path = environ.get('PATH_INFO', '/')
        traverser = getMultiAdapter((root, request), IPublishTraverserFactory)
        context, name, subpath = traverser(path)
        request.subpath = subpath
        request.view_name = name

        security_policy = queryUtility(ISecurityPolicy)
        if security_policy:
            permission = queryMultiAdapter((context, request), IViewPermission,
                                           name=name)
            if permission is not None:
                if not permission(security_policy):
                    app = HTTPUnauthorized()
                    app.explanation = repr(permission)
                    return app(environ, start_response)

        app = queryMultiAdapter((context, request), IViewFactory, name=name)
        if app is None:
            app = HTTPNotFound(request.url)
        else:
            app = getMultiAdapter((context, request, app),
                                  IWSGIApplicationFactory)
        return app(environ, start_response)

def make_app(root_policy, package=None, filename='configure.zcml'):
    """ Create a view registry based on the application's ZCML.  and
    return a Router object, representing a ``repoze.bfg`` WSGI
    application.  'root_policy' must be a callable that accepts a WSGI
    environment and returns a graph root object.  'package' is the
    dotted-Python-path packagename of the application, 'filename' is
    the filesystem path to a ZCML file (optionally relative to the
    package path) that should be parsed to create the view registry."""
    from repoze.bfg.registry import makeRegistry
    registry = makeRegistry(filename, package)
    return Router(root_policy, registry)

    
