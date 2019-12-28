from docutils.core import publish_parts
import re

from pyramid.httpexceptions import HTTPFound
from pyramid.security import (
    forget,
    remember,
)
from pyramid.view import (
    forbidden_view_config,
    view_config,
    )

from ..models import Page
from ..security import check_password, USERS

# regular expression used to find WikiWords
wikiwords = re.compile(r"\b([A-Z]\w+[A-Z]+\w+)")


@view_config(context='..models.Wiki',
             permission='view')
def view_wiki(context, request):
    return HTTPFound(location=request.resource_url(context, 'FrontPage'))


@view_config(context='..models.Page', renderer='tutorial:templates/view.pt',
             permission='view')
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

    page_text = publish_parts(context.data, writer_name='html')['html_body']
    page_text = wikiwords.sub(check, page_text)
    edit_url = request.resource_url(context, 'edit_page')
    return dict(page=context, page_text=page_text, edit_url=edit_url,
                logged_in=request.authenticated_userid)


@view_config(name='add_page', context='..models.Wiki',
             renderer='tutorial:templates/edit.pt',
             permission='edit')
def add_page(context, request):
    pagename = request.subpath[0]
    if 'form.submitted' in request.params:
        body = request.params['body']
        page = Page(body)
        page.__name__ = pagename
        page.__parent__ = context
        context[pagename] = page
        return HTTPFound(location=request.resource_url(page))
    save_url = request.resource_url(context, 'add_page', pagename)
    page = Page('')
    page.__name__ = pagename
    page.__parent__ = context
    return dict(page=page, save_url=save_url,
                logged_in=request.authenticated_userid)


@view_config(name='edit_page', context='..models.Page',
             renderer='tutorial:templates/edit.pt',
             permission='edit')
def edit_page(context, request):
    if 'form.submitted' in request.params:
        context.data = request.params['body']
        return HTTPFound(location=request.resource_url(context))

    return dict(page=context,
                save_url=request.resource_url(context, 'edit_page'),
                logged_in=request.authenticated_userid)


@view_config(context='..models.Wiki', name='login',
             renderer='tutorial:templates/login.pt')
@forbidden_view_config(renderer='tutorial:templates/login.pt')
def login(request):
    login_url = request.resource_url(request.context, 'login')
    referrer = request.url
    if referrer == login_url:
        referrer = '/'  # never use the login form itself as came_from
    came_from = request.params.get('came_from', referrer)
    message = ''
    login = ''
    password = ''
    if 'form.submitted' in request.params:
        login = request.params['login']
        password = request.params['password']
        if check_password(USERS.get(login), password):
            headers = remember(request, login)
            return HTTPFound(location=came_from,
                             headers=headers)
        message = 'Failed login'

    return dict(
        message=message,
        url=request.application_url + '/login',
        came_from=came_from,
        login=login,
        password=password,
        title='Login',
    )


@view_config(context='..models.Wiki', name='logout')
def logout(request):
    headers = forget(request)
    return HTTPFound(location=request.resource_url(request.context),
                     headers=headers)
