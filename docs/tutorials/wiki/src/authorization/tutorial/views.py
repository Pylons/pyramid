from docutils.core import publish_parts
import re

from pyramid.httpexceptions import HTTPFound
from pyramid.url import resource_url
from pyramid.view import view_config
from pyramid.security import authenticated_userid

from tutorial.models import Page

# regular expression used to find WikiWords
wikiwords = re.compile(r"\b([A-Z]\w+[A-Z]+\w+)")

@view_config(context='tutorial.models.Wiki', permission='view')
def view_wiki(context, request):
    return HTTPFound(location=resource_url(context, request, 'FrontPage'))

@view_config(context='tutorial.models.Page',
             renderer='templates/view.pt', permission='view')
def view_page(context, request):
    wiki = context.__parent__

    def check(match):
        word = match.group(1)
        if word in wiki:
            page = wiki[word]
            view_url = resource_url(page, request)
            return '<a href="%s">%s</a>' % (view_url, word)
        else:
            add_url = request.application_url + '/add_page/' + word 
            return '<a href="%s">%s</a>' % (add_url, word)

    content = publish_parts(context.data, writer_name='html')['html_body']
    content = wikiwords.sub(check, content)
    edit_url = resource_url(context, request, 'edit_page')

    logged_in = authenticated_userid(request)

    return dict(page = context, content = content, edit_url = edit_url,
                logged_in = logged_in)

@view_config(name='add_page', context='tutorial.models.Wiki',
             renderer='templates/edit.pt',
             permission='edit')
def add_page(context, request):
    name = request.subpath[0]
    if 'form.submitted' in request.params:
        body = request.params['body']
        page = Page(body)
        page.__name__ = name
        page.__parent__ = context
        context[name] = page
        return HTTPFound(location = resource_url(page, request))
    save_url = resource_url(context, request, 'add_page', name)
    page = Page('')
    page.__name__ = name
    page.__parent__ = context

    logged_in = authenticated_userid(request)

    return dict(page = page, save_url = save_url, logged_in = logged_in)

@view_config(name='edit_page', context='tutorial.models.Page',
             renderer='templates/edit.pt',
             permission='edit')
def edit_page(context, request):
    if 'form.submitted' in request.params:
        context.data = request.params['body']
        return HTTPFound(location = resource_url(context, request))

    logged_in = authenticated_userid(request)

    return dict(page = context,
                save_url = resource_url(context, request, 'edit_page'),
                logged_in = logged_in)
    
