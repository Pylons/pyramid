import re

from docutils.core import publish_parts

from webob.exc import HTTPFound

from routes import url_for

from repoze.bfg.chameleon_zpt import render_template_to_response
from repoze.bfg.view import static

from tutorial.models import DBSession
from tutorial.models import Page

# regular expression used to find WikiWords
wikiwords = re.compile(r"\b([A-Z]\w+[A-Z]+\w+)")

static_view = static('templates/static')

def view_wiki(context, request):
    return HTTPFound(location = url_for('view_page', page_name='FrontPage'))

def view_page(context, request):
    session = DBSession()
    page = session.query(Page).filter_by(name=context.pagename).one()

    def check(match):
        word = match.group(1)
        exists = session.query(Page).filter_by(name=word).all()
        if exists:
            view_url = url_for('view_page', pagename=word)
            return '<a href="%s">%s</a>' % (view_url, word)
        else:
            add_url = url_for('add_page', pagename=word)
            return '<a href="%s">%s</a>' % (add_url, word)

    content = publish_parts(page.data, writer_name='html')['html_body']
    content = wikiwords.sub(check, content)
    edit_url = url_for('edit_page', pagename=context.pagename)
    return render_template_to_response('templates/view.pt',
                                       request = request,
                                       page = page,
                                       content = content,
                                       edit_url = edit_url)

def add_page(context, request):
    name = context.pagename
    if 'form.submitted' in request.params:
        session = DBSession()
        body = request.params['body']
        page = Page(name, body)
        session.add(page)
        return HTTPFound(location = url_for('view_page', pagename=name))
    save_url = url_for('add_page', pagename=name)
    page = Page('', '')
    return render_template_to_response('templates/edit.pt',
                                       request = request,
                                       page = page,
                                       save_url = save_url)
    
def edit_page(context, request):
    name = context.pagename
    session = DBSession()
    page = session.query(Page).filter_by(name=name).one()
    if 'form.submitted' in request.params:
        page.data = request.params['body']
        session.add(page)
        return HTTPFound(location = url_for('view_page',
                                            pagename=name))

    return render_template_to_response('templates/edit.pt',
                                       request = request,
                                       page = page,
                                       save_url = url_for('edit_page',
                                                          pagename=name),
                                       )
