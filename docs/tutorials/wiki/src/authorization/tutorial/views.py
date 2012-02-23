from docutils.core import publish_parts
import re

from pyramid.httpexceptions import HTTPFound

from pyramid.view import (
    view_config,
    forbidden_view_config,
    )

from pyramid.security import (
    authenticated_userid,
    remember,
    forget,
    )

from .security import USERS
from .models import Page

# regular expression used to find WikiWords
wikiwords = re.compile(r"\b([A-Z]\w+[A-Z]+\w+)")

@view_config(context='.models.Wiki', permission='view')
def view_wiki(context, request):
    return HTTPFound(location=request.resource_url(context, 'FrontPage'))

@view_config(context='.models.Page',
             renderer='templates/view.pt', permission='view')
def view_page(context, request):
    wiki = context.__parent__

    def check(match):
        word = match.group(1)
        if word in wiki:
            page = wiki[word]
            view_url = request.resource_url(page)
            return '<a href="%s">%s</a>' % (view_url, word)
        else:
            add_url = request.application_url + '/add_page/' + word 
            return '<a href="%s">%s</a>' % (add_url, word)

    content = publish_parts(context.data, writer_name='html')['html_body']
    content = wikiwords.sub(check, content)
    edit_url = request.resource_url(context, 'edit_page')

    logged_in = authenticated_userid(request)

    return dict(page = context, content = content, edit_url = edit_url,
                logged_in = logged_in)

@view_config(name='add_page', context='.models.Wiki',
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
        return HTTPFound(location = request.resource_url(page))
    save_url = request.resource_url(context, 'add_page', name)
    page = Page('')
    page.__name__ = name
    page.__parent__ = context

    logged_in = authenticated_userid(request)

    return dict(page = page, save_url = save_url, logged_in = logged_in)

@view_config(name='edit_page', context='.models.Page',
             renderer='templates/edit.pt',
             permission='edit')
def edit_page(context, request):
    if 'form.submitted' in request.params:
        context.data = request.params['body']
        return HTTPFound(location = request.resource_url(context))

    logged_in = authenticated_userid(request)

    return dict(page = context,
                save_url = request.resource_url(context, 'edit_page'),
                logged_in = logged_in)

@view_config(context='.models.Wiki', name='login',
             renderer='templates/login.pt')
@forbidden_view_config(renderer='templates/login.pt')
def login(request):
    login_url = request.resource_url(request.context, 'login')
    referrer = request.url
    if referrer == login_url:
        referrer = '/' # never use the login form itself as came_from
    came_from = request.params.get('came_from', referrer)
    message = ''
    login = ''
    password = ''
    if 'form.submitted' in request.params:
        login = request.params['login']
        password = request.params['password']
        if USERS.get(login) == password:
            headers = remember(request, login)
            return HTTPFound(location = came_from,
                             headers = headers)
        message = 'Failed login'

    return dict(
        message = message,
        url = request.application_url + '/login',
        came_from = came_from,
        login = login,
        password = password,
        )

@view_config(context='.models.Wiki', name='logout')
def logout(request):
    headers = forget(request)
    return HTTPFound(location = request.resource_url(request.context),
                     headers = headers)
