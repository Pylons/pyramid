from zope.component import getAdapter
from repoze.bfg.interfaces import IWSGIApplication

class Router:
    def __init__(self, app, root_finder, policy):
        self.app = app
        self.root_finder = root_finder
        self.policy = policy

    def __call__(self, environ, start_response):
        root = self.root_finder(environ)
        context, name, subpath = self.policy(root, environ)
        app = getAdapter(context, IWSGIApplication, name)
        environ['repoze.bfg.context'] = context
        environ['repoze.bfg.subpath'] = subpath
        return app(environ, start_response)
