from zope.component import getMultiAdapter
from zope.component import queryMultiAdapter
from zope.component import queryUtility
from zope.component.event import dispatch
from zope.interface import directlyProvides

from webob import Request
from webob.exc import HTTPNotFound
from webob.exc import HTTPUnauthorized

from repoze.bfg.events import NewRequest
from repoze.bfg.events import NewResponse
from repoze.bfg.interfaces import ITraverserFactory
from repoze.bfg.interfaces import IView
from repoze.bfg.interfaces import IViewPermission
from repoze.bfg.interfaces import ISecurityPolicy
from repoze.bfg.interfaces import IRequest

from repoze.bfg.registry import registry_manager

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
        traverser = getMultiAdapter((root, request), ITraverserFactory)
        context, name, subpath = traverser(environ)

        request.context = context
        request.view_name = name
        request.subpath = subpath

        security_policy = queryUtility(ISecurityPolicy)
        if security_policy:
            permission = queryMultiAdapter((context, request), IViewPermission,
                                           name=name)
            if permission is not None:
                if not permission(security_policy):
                    app = HTTPUnauthorized()
                    app.explanation = repr(permission)
                    return app(environ, start_response)

        response = queryMultiAdapter((context, request), IView, name=name,
                                     default=_marker)
        if response is _marker:
            app = HTTPNotFound(request.url)
            return app(environ, start_response)

        if not isResponse(response):
            raise ValueError('response was not IResponse: %s' % response)

        dispatch(NewResponse(response))

        start_response(response.status, response.headerlist)
        return response.app_iter

def isResponse(ob):
    # response objects aren't obligated to implement a Zope interface,
    # so we do it the hard way
    if ( hasattr(ob, 'app_iter') and hasattr(ob, 'headerlist') and
         hasattr(ob, 'status') ):
        if ( hasattr(ob.app_iter, '__iter__') and
             hasattr(ob.headerlist, '__iter__') and
             isinstance(ob.status, basestring) ) :
            return True

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

    
