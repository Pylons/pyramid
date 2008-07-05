from zope.component import getAdapter
from repoze.bfg.interfaces import IWSGIApplication

class Router:
    def __init__(self, app, root_policy, traversal_policy):
        self.app = app
        self.root_policy = root_policy
        self.traversal_policy = traversal_policy

    def __call__(self, environ, start_response):
        root = self.root_policy(environ)
        context, name, subpath = self.traversal_policy(root, environ)
        app = getAdapter(context, IWSGIApplication, name)
        environ['repoze.bfg.context'] = context
        environ['repoze.bfg.subpath'] = subpath
        return app(environ, start_response)
