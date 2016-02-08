import cgi
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
    )

from ..models import Page
from ..security.default import USERS

# regular expression used to find WikiWords
wikiwords = re.compile(r"\b([A-Z]\w+[A-Z]+\w+)")

@view_config(route_name='view_wiki', permission='view')
def view_wiki(request):
    next_url = request.route_url('view_page', pagename='FrontPage')
    return HTTPFound(location=next_url)

@view_config(route_name='view_page', renderer='../templates/view.jinja2',
             permission='view')
def view_page(request):
    pagename = request.matchdict['pagename']
    page = request.dbsession.query(Page).filter_by(name=pagename).first()
    if page is None:
        return HTTPNotFound('No such page')

    def check(match):
        word = match.group(1)
        exists = request.dbsession.query(Page).filter_by(name=word).all()
        if exists:
            view_url = request.route_url('view_page', pagename=word)
            return '<a href="%s">%s</a>' % (view_url, cgi.escape(word))
        else:
            add_url = request.route_url('add_page', pagename=word)
            return '<a href="%s">%s</a>' % (add_url, cgi.escape(word))

    content = publish_parts(page.data, writer_name='html')['html_body']
    content = wikiwords.sub(check, content)
    edit_url = request.route_url('edit_page', pagename=pagename)
    return dict(page=page, content=content, edit_url=edit_url)

@view_config(route_name='add_page', renderer='../templates/edit.jinja2',
             permission='edit')
def add_page(request):
    pagename = request.matchdict['pagename']
    if 'form.submitted' in request.params:
        body = request.params['body']
        page = Page(name=pagename, data=body)
        request.dbsession.add(page)
        next_url = request.route_url('view_page', pagename=pagename)
        return HTTPFound(location=next_url)
    save_url = request.route_url('add_page', pagename=pagename)
    page = Page(name='', data='')
    return dict(page=page, save_url=save_url)

@view_config(route_name='edit_page', renderer='../templates/edit.jinja2',
             permission='edit')
def edit_page(request):
    pagename = request.matchdict['pagename']
    page = request.dbsession.query(Page).filter_by(name=pagename).one()
    if 'form.submitted' in request.params:
        page.data = request.params['body']
        next_url = request.route_url('view_page', pagename=pagename)
        return HTTPFound(location=next_url)
    return dict(
        page=page,
        save_url=request.route_url('edit_page', pagename=pagename),
        )


@view_config(route_name='login', renderer='templates/login.jinja2')
@forbidden_view_config(renderer='templates/login.jinja2')
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
            return HTTPFound(location=came_from, headers=headers)
        message = 'Failed login'

    return dict(
        message=message,
        url=request.route_url('login'),
        came_from=came_from,
        login=login,
        password=password,
        )

@view_config(route_name='logout')
def logout(request):
    headers = forget(request)
    next_url = request.route_url('view_wiki')
    return HTTPFound(location=next_url, headers=headers)
