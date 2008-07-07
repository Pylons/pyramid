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
    def __init__(self, root_policy):
        self.root_policy = root_policy

    def __call__(self, environ, start_response):
        request = Request(environ)
        directlyProvides(request, IRequest)
        root = self.root_policy(environ)
        path = environ.get('PATH_INFO', '/')
        traverser = getMultiAdapter((root, request), IPublishTraverserFactory)
        context, name, subpath = traverser(path)
        request.subpath = subpath
        app = queryMultiAdapter((context, request), IViewFactory, name=name,
                                default=_marker)
        if app is _marker:
            app = HTTPNotFound(request.url)
        else:
            app = getMultiAdapter((app, request), IWSGIApplicationFactory)
        return app(environ, start_response)

def make_app(root_policy, package=None, filename='configure.zcml'):
    import zope.configuration.xmlconfig
    zope.configuration.xmlconfig.file(filename, package=package)
    return Router(root_policy)

    
