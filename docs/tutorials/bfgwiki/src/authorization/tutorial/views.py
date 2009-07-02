from docutils.core import publish_parts
import re

from webob.exc import HTTPFound
from repoze.bfg.url import model_url
from repoze.bfg.chameleon_zpt import render_template_to_response

from repoze.bfg.security import authenticated_userid

from repoze.bfg.view import static
from repoze.bfg.view import bfg_view

from tutorial.models import Page
from tutorial.models import Wiki

# regular expression used to find WikiWords
wikiwords = re.compile(r"\b([A-Z]\w+[A-Z]+\w+)")

static_app = static('templates/static')

@bfg_view(for_=Wiki, name='static', permission='view')
def static_view(context, request):
    return static_app(context, request)

@bfg_view(for_=Wiki, permission='view')
def view_wiki(context, request):
    return HTTPFound(location = model_url(context, request, 'FrontPage'))

@bfg_view(for_=Page, permission='view')
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

    logged_in = authenticated_userid(request)

    return render_template_to_response('templates/view.pt',
                                       request = request,
                                       page = context,
                                       content = content,
                                       logged_in = logged_in,
                                       edit_url = edit_url)

@bfg_view(for_=Wiki, name='add_page', permission='edit')
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

    logged_in = authenticated_userid(request)

    return render_template_to_response('templates/edit.pt',
                                       request = request,
                                       page = page,
                                       logged_in = logged_in,
                                       save_url = save_url)

@bfg_view(for_=Page, name='edit_page', permission='edit')
def edit_page(context, request):
    if 'form.submitted' in request.params:
        context.data = request.params['body']
        return HTTPFound(location = model_url(context, request))

    logged_in = authenticated_userid(request)

    return render_template_to_response('templates/edit.pt',
                                       request = request,
                                       page = context,
                                       logged_in = logged_in,
                                       save_url = model_url(context, request,
                                                            'edit_page')
                                       )

