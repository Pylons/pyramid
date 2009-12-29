import re

from docutils.core import publish_parts

from webob.exc import HTTPFound

from repoze.bfg.url import route_url

from tutorial.models import DBSession
from tutorial.models import Page

# regular expression used to find WikiWords
wikiwords = re.compile(r"\b([A-Z]\w+[A-Z]+\w+)")

def view_wiki(request):
    return HTTPFound(location = route_url('view_page', request,
                                          pagename='FrontPage'))

def view_page(request):
    matchdict = request.matchdict
    session = DBSession()
    page = session.query(Page).filter_by(name=matchdict['pagename']).one()

    def check(match):
        word = match.group(1)
        exists = session.query(Page).filter_by(name=word).all()
        if exists:
            view_url = route_url('view_page', request, pagename=word)
            return '<a href="%s">%s</a>' % (view_url, word)
        else:
            add_url = route_url('add_page', request, pagename=word)
            return '<a href="%s">%s</a>' % (add_url, word)

    content = publish_parts(page.data, writer_name='html')['html_body']
    content = wikiwords.sub(check, content)
    edit_url = route_url('edit_page', request,
                         pagename=matchdict['pagename'])
    return dict(page=page, content=content, edit_url=edit_url)

def add_page(request):
    name = request.matchdict['pagename']
    if 'form.submitted' in request.params:
        session = DBSession()
        body = request.params['body']
        page = Page(name, body)
        session.add(page)
        return HTTPFound(location = route_url('view_page', request,
                                              pagename=name))
    save_url = route_url('add_page', request, pagename=name)
    page = Page('', '')
    return dict(page=page, save_url=save_url)
    
def edit_page(request):
    name = request.matchdict['pagename']
    session = DBSession()
    page = session.query(Page).filter_by(name=name).one()
    if 'form.submitted' in request.params:
        page.data = request.params['body']
        session.add(page)
        return HTTPFound(location = route_url('view_page', request,
                                              pagename=name))
    return dict(
        page=page,
        save_url = route_url('edit_page', request, pagename=name),
        )
