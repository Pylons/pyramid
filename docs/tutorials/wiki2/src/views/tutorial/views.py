import re

from docutils.core import publish_parts

from pyramid.httpexceptions import HTTPFound, HTTPNotFound

from tutorial.models import DBSession
from tutorial.models import Page

# regular expression used to find WikiWords
wikiwords = re.compile(r"\b([A-Z]\w+[A-Z]+\w+)")

def view_wiki(request):
    return HTTPFound(location = request.route_url('view_page',
                                                  pagename='FrontPage'))

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
    return dict(page=page, content=content, edit_url=edit_url)

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
    return dict(page=page, save_url=save_url)

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
        )
