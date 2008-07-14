import formencode
import time

from webob.exc import HTTPFound

from repoze.bfg.template import render_template
from repoze.bfg.sampleapp.models import BlogEntry

def datestring(dt):
    return dt.strftime('%Y-%m-%d %H:%M:%S')

def blog_default_view(context, request):
    entrydata = []
    for name, entry in self.context.items():
        entrydata.append(
            {
            'name':name,
            'title':entry.title,
            'author':entry.author,
            'created':datestring(entry.created),
            'message':self.request.params.get('message'),
            }
            )

    info = {'name':self.context.__name__, entries:entrydata}
    return render_template('templates/blog.pt', info)

def blog_entry_default_view(context, request):
    info = {
        'name':self.context.__name__,
        'title':self.context.title,
        'body':self.context.body,
        'author':self.context.author,
        'created':datestring(self.context.created),
        }
    return render_template('templates/blog_entry.pt', **info)

class BlogAddSchema(formencode.Schema):
    allow_extra_fields = True
    author = formencode.validators.NotEmpty()
    body = formencode.validators.NotEmpty()
    title = formencode.validators.NotEmpty()

def blog_entry_add_view(context, request):
    params = self.request.params

    message = None

    author = params.get('author', '')
    body = params.get('body', '')
    title = params.get('title', '')
    info = dict(request=self.request,
                author=author, body=body, title=title, message=None)

    if params.has_key('form.submitted'):
        schema = BlogAddSchema()
        try:
            form = schema.to_python(params)
        except formencode.validators.Invalid, why:
            message = str(why)
            info['message'] = message
        else:
            author = form['author']
            body = form['body']
            title = form['title']
            name = str(time.time())
            new_entry = BlogEntry(name, title, body, author)
            self.context[name] = new_entry
            return HTTPFound(location='/')
    else:
        return render_template('templates/blog_entry_add.pt', **info)
                      
def contents_view(context, request):
    return render_template('templates/contents.pt', context=context)
