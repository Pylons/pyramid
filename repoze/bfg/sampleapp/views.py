import formencode
import time

from webob.exc import HTTPFound

from repoze.bfg.template import render_template
from repoze.bfg.sampleapp.models import BlogEntry

def datestring(dt):
    return dt.strftime('%Y-%m-%d %H:%M:%S')

def blog_default_view(context, request):
    entrydata = []
    for name, entry in context.items():
        entrydata.append(
            {
            'name':name,
            'title':entry.title,
            'author':entry.author,
            'created':datestring(entry.created),
            'message':request.params.get('message'),
            }
            )

    return render_template('templates/blog.pt', name=context.__name__,
                           entries=entrydata)

def blog_entry_default_view(context, request):
    info = {
        'name':context.__name__,
        'title':context.title,
        'body':context.body,
        'author':context.author,
        'created':datestring(context.created),
        }
    return render_template('templates/blog_entry.pt', **info)

class BlogAddSchema(formencode.Schema):
    allow_extra_fields = True
    author = formencode.validators.NotEmpty()
    body = formencode.validators.NotEmpty()
    title = formencode.validators.NotEmpty()

def blog_entry_add_view(context, request):
    params = request.params

    message = None

    author = params.get('author', '')
    body = params.get('body', '')
    title = params.get('title', '')
    info = dict(request=request, author=author, body=body, title=title,
                message=None)

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
            context[name] = new_entry
            return HTTPFound(location='/')

    return render_template('templates/blog_entry_add.pt', **info)
                      
def contents_view(context, request):
    return render_template('templates/contents.pt', context=context)
