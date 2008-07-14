import time

from webob.exc import HTTPFound

from repoze.bfg.view import TemplateView
from repoze.bfg.view import View

from repoze.bfg.sampleapp.models import BlogEntry

def datestring(dt):
    return dt.strftime('%Y-%m-%d %H:%M:%S')

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

class BlogEntryAddView(View):

    def __call__(self):
        author = self.request.params['author']
        body = self.request.params['body']
        title = self.request.params['title']
        name = str(time.time())
        new_entry = BlogEntry(name, title, body, author)
        self.context[name] = new_entry
        return HTTPFound(location='/')
                      
