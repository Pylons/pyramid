from repoze.bfg.template import TemplateView

from webob import Response

class BlogDefaultView(TemplateView):
    def getInfo(self):
        return {'greeting':'Hello, I\'m the default view',
                'id':self.context.id}

class BlogWooHooView(TemplateView):
    def getInfo(self):
        return {'greeting':'Woo hoo, I\'m another view' ,
                'id':self.context.id}

class DefaultView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request
        
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
    
