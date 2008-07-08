from webob import Response

from repoze.bfg.template import TemplateView

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

