import re
from docutils.core import publish_parts

from pyramid.httpexceptions import (
    HTTPFound,
    HTTPNotFound,
    )

from pyramid.view import (
    view_config,
    forbidden_view_config,
    )

from pyramid.security import (
    remember,
    forget,
    authenticated_userid,
    )

from .models import (
    DBSession,
    Page,
    )

from .security import USERS

# regular expression used to find WikiWords
wikiwords = re.compile(r"\b([A-Z]\w+[A-Z]+\w+)")

@view_config(route_name='view_wiki')
def view_wiki(request):
    return HTTPFound(location = request.route_url('view_page',
                                                  pagename='FrontPage'))

@view_config(route_name='view_page', renderer='templates/view.pt')
def view_page(request):
    pagename = request.matchdict['pagename']
    session = DBSession()
    page = session.query(Page).filter_by(name=pagename).first()
    if page is None:
        return HTTPNotFound('No such page')

    def check(match):
        word = match.group(1)
        exists = session.query(Page).filter_by(name=word).all()
        if exists:
            view_url = request.route_url('view_page', pagename=word)
            return '<a href="%s">%s</a>' % (view_url, word)
        else:
            add_url = request.route_url('add_page', pagename=word)
            return '<a href="%s">%s</a>' % (add_url, word)

    content = publish_parts(page.data, writer_name='html')['html_body']
    content = wikiwords.sub(check, content)
    edit_url = request.route_url('edit_page', pagename=pagename)
    return dict(page=page, content=content, edit_url=edit_url,
                logged_in=authenticated_userid(request))

@view_config(route_name='add_page', renderer='templates/edit.pt',
             permission='edit')
def add_page(request):
    name = request.matchdict['pagename']
    if 'form.submitted' in request.params:
        session = DBSession()
        body = request.params['body']
        page = Page(name, body)
        session.add(page)
        return HTTPFound(location = request.route_url('view_page',
                                                      pagename=name))
    save_url = request.route_url('add_page', pagename=name)
    page = Page('', '')
    return dict(page=page, save_url=save_url,
                logged_in=authenticated_userid(request))

@view_config(route_name='edit_page', renderer='templates/edit.pt',
             permission='edit')
def edit_page(request):
    name = request.matchdict['pagename']
    session = DBSession()
    page = session.query(Page).filter_by(name=name).one()
    if 'form.submitted' in request.params:
        page.data = request.params['body']
        session.add(page)
        return HTTPFound(location = request.route_url('view_page',
                                                      pagename=name))
    return dict(
        page=page,
        save_url = request.route_url('edit_page', pagename=name),
        logged_in=authenticated_userid(request),
        )

@view_config(route_name='login', renderer='templates/login.pt')
@forbidden_view_config(renderer='templates/login.pt')
def login(request):
    login_url = request.route_url('login')
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

@view_config(route_name='logout')
def logout(request):
    headers = forget(request)
    return HTTPFound(location = request.route_url('view_wiki'),
                     headers = headers)
    
