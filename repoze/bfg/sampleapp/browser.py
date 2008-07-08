import time

from webob import Response
from webob.exc import HTTPFound

from repoze.bfg.template import TemplateView
from repoze.bfg.sampleapp.models import BlogEntry

def datestring(dt):
    return dt.strftime('%Y-%m-%dT%H:%M:%S')

class BlogDefaultView(TemplateView):
    def getInfo(self):
        entrydata = []
        for name, entry in self.context.items():
            entrydata.append(
                {
                'name':name,
                'title':entry.title,
                'author':entry.author,
                'created':datestring(entry.created),
                }
                )
        return {'name':self.context.__name__, 'entries':entrydata}

class BlogEntryDefaultView(TemplateView):
    def getInfo(self):
        return {
            'name':self.context.__name__,
            'title':self.context.title,
            'body':self.context.body,
            'author':self.context.author,
            'created':datestring(self.context.created),
            }

class BlogEntryAddView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        author = self.request.params['author']
        body = self.request.params['body']
        title = self.request.params['title']
        name = str(time.time())
        new_entry = BlogEntry(name, title, body, author)
        self.context[name] = new_entry
        return HTTPFound(location='/')
                      
