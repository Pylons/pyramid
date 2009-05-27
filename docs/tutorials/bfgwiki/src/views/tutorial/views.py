from docutils.core import publish_parts
import re

from webob.exc import HTTPFound
from repoze.bfg.url import model_url
from repoze.bfg.chameleon_zpt import render_template_to_response
from repoze.bfg.view import static

from tutorial.models import Page

# regular expression used to find WikiWords
wikiwords = re.compile(r"\b([A-Z]\w+[A-Z]+\w+)")

static_view = static('templates/static')

def view_wiki(context, request):
    return HTTPFound(location = model_url(context, request, 'FrontPage'))

def view_page(context, request):
    wiki = context.__parent__

    def check(match):
        word = match.group(1)
        if word in wiki:
            page = wiki[word]
            view_url = model_url(page, request)
            return '<a href="%s">%s</a>' % (view_url, word)
        else:
            add_url = request.application_url + '/add_page/' + word 
            return '<a href="%s">%s</a>' % (add_url, word)

    content = publish_parts(context.data, writer_name='html')['html_body']
    content = wikiwords.sub(check, content)
    edit_url = model_url(context, request, 'edit_page')
    return render_template_to_response('templates/view.pt',
                                       request = request,
                                       page = context,
                                       content = content,
                                       edit_url = edit_url)
    
def add_page(context, request):
    name = request.subpath[0]
    if 'form.submitted' in request.params:
        body = request.params['body']
        page = Page(body)
        page.__name__ = name
        page.__parent__ = context
        context[name] = page
        return HTTPFound(location = model_url(page, request))
    save_url = model_url(context, request, 'add_page', name)
    page = Page('')
    page.__name__ = name
    page.__parent__ = context
    return render_template_to_response('templates/edit.pt',
                                       request = request,
                                       page = page,
                                       save_url = save_url)
    
def edit_page(context, request):
    if 'form.submitted' in request.params:
        context.data = request.params['body']
        return HTTPFound(location = model_url(context, request))

    return render_template_to_response('templates/edit.pt',
                                       request = request,
                                       page = context,
                                       save_url = model_url(context, request,
                                                            'edit_page')
                                       )
    
    
