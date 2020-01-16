from docutils.core import publish_parts
from html import escape
from pyramid.httpexceptions import (
    HTTPNotFound,
    HTTPSeeOther,
)
from pyramid.view import view_config
import re

from .. import models


# regular expression used to find WikiWords
wikiwords = re.compile(r"\b([A-Z]\w+[A-Z]+\w+)")

@view_config(route_name='view_wiki')
def view_wiki(request):
    next_url = request.route_url('view_page', pagename='FrontPage')
    return HTTPSeeOther(location=next_url)

@view_config(route_name='view_page', renderer='tutorial:templates/view.jinja2')
def view_page(request):
    pagename = request.matchdict['pagename']
    page = request.dbsession.query(models.Page).filter_by(name=pagename).first()
    if page is None:
        raise HTTPNotFound('No such page')

    def add_link(match):
        word = match.group(1)
        exists = request.dbsession.query(models.Page).filter_by(name=word).all()
        if exists:
            view_url = request.route_url('view_page', pagename=word)
            return '<a href="%s">%s</a>' % (view_url, escape(word))
        else:
            add_url = request.route_url('add_page', pagename=word)
            return '<a href="%s">%s</a>' % (add_url, escape(word))

    content = publish_parts(page.data, writer_name='html')['html_body']
    content = wikiwords.sub(add_link, content)
    edit_url = request.route_url('edit_page', pagename=page.name)
    return dict(page=page, content=content, edit_url=edit_url)

@view_config(route_name='edit_page', renderer='tutorial:templates/edit.jinja2')
def edit_page(request):
    pagename = request.matchdict['pagename']
    page = request.dbsession.query(models.Page).filter_by(name=pagename).one()
    if request.method == 'POST':
        page.data = request.params['body']
        next_url = request.route_url('view_page', pagename=page.name)
        return HTTPSeeOther(location=next_url)
    return dict(
        pagename=page.name,
        pagedata=page.data,
        save_url=request.route_url('edit_page', pagename=page.name),
    )

@view_config(route_name='add_page', renderer='tutorial:templates/edit.jinja2')
def add_page(request):
    pagename = request.matchdict['pagename']
    if request.dbsession.query(models.Page).filter_by(name=pagename).count() > 0:
        next_url = request.route_url('edit_page', pagename=pagename)
        return HTTPSeeOther(location=next_url)
    if request.method == 'POST':
        body = request.params['body']
        page = models.Page(name=pagename, data=body)
        page.creator = (
            request.dbsession.query(models.User).filter_by(name='editor').one())
        request.dbsession.add(page)
        next_url = request.route_url('view_page', pagename=pagename)
        return HTTPSeeOther(location=next_url)
    save_url = request.route_url('add_page', pagename=pagename)
    return dict(pagename=pagename, pagedata='', save_url=save_url)
