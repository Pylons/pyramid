from zope.interface import classProvides
from zope.interface import implements
from zope.interface import Interface

from repoze.bfg.interfaces import IViewFactory
from repoze.bfg.interfaces import IView

from webob import Response

class IBlogModel(Interface):
    pass

class BlogModel:
    implements(IBlogModel)

class BlogDefaultView(object):
    classProvides(IViewFactory)
    implements(IView)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        return Response('Hello world!')

class BlogWooHooView(object):
    classProvides(IViewFactory)
    implements(IView)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        return Response('Woo hoo!')
    
if __name__ == '__main__':
    from repoze.bfg.interfaces import IViewFactory
    from repoze.bfg.interfaces import IRequest
    from zope.component import getGlobalSiteManager
    gsm = getGlobalSiteManager()
    gsm.registerAdapter(BlogDefaultView, (IBlogModel, IRequest), IViewFactory)
    gsm.registerAdapter(BlogWooHooView, (IBlogModel, IRequest), IViewFactory,
                        name='woohoo.html')
    from repoze.bfg.router import make_app
    def get_root(environ):
        return {'blog':BlogModel()}
    app = make_app(get_root)
    from paste import httpserver
    httpserver.serve(app, host='0.0.0.0', port='5432')
    
