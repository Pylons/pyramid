from zope.interface import classProvides
from zope.interface import implements

from repoze.bfg.interfaces import IViewFactory
from repoze.bfg.interfaces import IView

from webob import Response

class View(object):
    classProvides(IViewFactory)
    implements(IView)

    def __init__(self, context, request):
        self.context = context
        self.request = request

class BlogDefaultView(View):
    def __call__(self):
        return Response('Hello world from the blog %s!' % self.context.id)

class BlogWooHooView(View):
    def __call__(self):
        return Response('Woo hoo from the blog named %s!' % self.context.id)

class DefaultView(View):
    def __call__(self):
        return Response('Default page, context is %s' % self.context)


if __name__ == '__main__':
    from repoze.bfg import sampleapp
    from repoze.bfg.sampleapp.models import BlogModel
    from repoze.bfg.router import make_app
    blog = BlogModel('myblog')
    root = {'blog':blog}
    def get_root(environ):
        return root
    app = make_app(get_root, sampleapp)
    from paste import httpserver
    httpserver.serve(app, host='0.0.0.0', port='5432')
    
