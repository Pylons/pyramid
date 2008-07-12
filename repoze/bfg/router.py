from zope.component import getMultiAdapter
from zope.component import queryMultiAdapter
from zope.interface import directlyProvides

from webob import Request
from webob.exc import HTTPNotFound

from repoze.bfg.interfaces import IPublishTraverserFactory
from repoze.bfg.interfaces import IViewFactory
from repoze.bfg.interfaces import IWSGIApplicationFactory
from repoze.bfg.interfaces import IRequest

_marker = ()

class Router:
    def __init__(self, root_policy, app_context):
        self.root_policy = root_policy
        self.app_context = app_context

    def __call__(self, environ, start_response):
        request = Request(environ)
        directlyProvides(request, IRequest)
        root = self.root_policy(environ)
        path = environ.get('PATH_INFO', '/')
        traverser = getMultiAdapter((root, request), IPublishTraverserFactory)
        context, name, subpath = traverser(path)
        request.subpath = subpath
        request.view_name = name
        app = queryMultiAdapter((context, request), IViewFactory, name=name,
                                default=_marker)
        if app is _marker:
            app = HTTPNotFound(request.url)
        else:
            app = getMultiAdapter((context, request, app),
                                  IWSGIApplicationFactory)
        return app(environ, start_response)

# enable the below when we figure out app-local registries

## def app_component_registry(app_context):
##     registry = getattr(app_context, 'registry', None)
##     if registry is None:
##         from zope.component.registry import Components
##         app_context.registry = Components()
##     return app_context.registry

def make_app(root_policy, package=None, filename='configure.zcml'):
    import zope.configuration.xmlconfig
    context = zope.configuration.xmlconfig.file(filename, package=package)
    return Router(root_policy, context)

    
