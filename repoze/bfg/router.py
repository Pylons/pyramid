from zope.component import getAdapter
from repoze.bfg.interfaces import IWSGIApplication

class Router:
    def __init__(self, app, policy):
        self.app = app
        self.policy = policy

    def __call__(self, environ, start_response):
        context, name, subpath = self.policy(environ)
        app = getAdapter(context, IWSGIApplication, name)
        environ['repoze.bfg.context'] = context
        environ['repoze.bfg.subpath'] = subpath
        return app(environ, start_response)
