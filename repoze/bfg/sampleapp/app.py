from zope.interface import classProvides
from zope.interface import implements
from zope.interface import Interface
from zope.interface import Attribute

from repoze.bfg.interfaces import IViewFactory
from repoze.bfg.interfaces import IView

from webob import Response

class IBlogModel(Interface):
    id = Attribute('id')

class BlogModel:
    implements(IBlogModel)
    def __init__(self, id):
        self.id = id

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
    from repoze.bfg.interfaces import IViewFactory
    from repoze.bfg.interfaces import IRequest
    from zope.component import getGlobalSiteManager
    gsm = getGlobalSiteManager()
    gsm.registerAdapter(BlogDefaultView, (IBlogModel, IRequest), IViewFactory)
    gsm.registerAdapter(BlogWooHooView, (IBlogModel, IRequest), IViewFactory,
                        name='woohoo.html')
    gsm.registerAdapter(DefaultView, (None, IRequest), IViewFactory, '')
    from repoze.bfg.router import make_app
    def get_root(environ):
        return {'blog':BlogModel('myblog')}
    app = make_app(get_root)
    from paste import httpserver
    httpserver.serve(app, host='0.0.0.0', port='5432')
    
