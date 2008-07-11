from zope.component import getMultiAdapter
from zope.component import queryMultiAdapter
from zope.interface import directlyProvides

from webob import Request
from webob.exc import HTTPNotFound
from webob.exc import HTTPFound

from repoze.bfg.interfaces import IPublishTraverserFactory
from repoze.bfg.interfaces import IViewFactory
from repoze.bfg.interfaces import IWSGIApplicationFactory

from repoze.bfg.interfaces import IRequest

_marker = ()

class Router:
    def __init__(self, root_policy, default_redirects=True):
        self.root_policy = root_policy
        self.default_redirects = default_redirects

    def __call__(self, environ, start_response):
        request = Request(environ)
        directlyProvides(request, IRequest)
        root = self.root_policy(environ)
        path = environ.get('PATH_INFO', '/')
        traverser = getMultiAdapter((root, request), IPublishTraverserFactory)
        context, name, subpath = traverser(path)
        if self.default_redirects and (not name) and (not path.endswith('/')):
            # if this is the default view of the context, and the URL
            # doesn't end in a slash, redirect to the url + '/' (so we
            # don't have to play base tag games)
            app = HTTPFound(add_slash=True)
        else:
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

def make_app(root_policy, package=None, default_redirects=True,
             filename='configure.zcml'):
    import zope.configuration.xmlconfig
    zope.configuration.xmlconfig.file(filename, package=package)
    return Router(root_policy, default_redirects)

    
