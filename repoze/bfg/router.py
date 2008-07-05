from zope.component import queryMultiAdapter
from zope.interface import directlyProvides

from webob import Request
from webob.exc import HTTPNotFound

from repoze.bfg.interfaces import IWSGIApplicationFactory
from repoze.bfg.interfaces import IWebObRequest

class Router:
    def __init__(self, root_policy, traversal_policy):
        self.root_policy = root_policy
        self.traversal_policy = traversal_policy

    def __call__(self, environ, start_response):
        root = self.root_policy(environ)
        context, name, subpath = self.traversal_policy(root, environ)
        environ['repoze.bfg.subpath'] = subpath
        request = Request(environ)
        directlyProvides(request, IWebObRequest)
        app = queryMultiAdapter((context, request),
                                IWSGIApplicationFactory, name=name)
        if app is None:
            app = HTTPNotFound(request.url)
        return app(environ, start_response)
