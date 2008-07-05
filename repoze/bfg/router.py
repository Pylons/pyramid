from zope.component import getAdapter
from repoze.bfg.interfaces import IWSGIApplicationFactory

class Router:
    def __init__(self, root_policy, traversal_policy):
        self.root_policy = root_policy
        self.traversal_policy = traversal_policy

    def __call__(self, environ, start_response):
        root = self.root_policy(environ)
        context, name, subpath = self.traversal_policy(root, environ)
        environ['repoze.bfg.subpath'] = subpath
        app = getAdapter(context, IWSGIApplicationFactory, name=name)
        return app(environ, start_response)
