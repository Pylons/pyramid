from docutils.core import publish_parts
from pyramid.httpexceptions import HTTPSeeOther
from pyramid.view import view_config
import re

from ..models import Page


# regular expression used to find WikiWords
wikiwords = re.compile(r"\b([A-Z]\w+[A-Z]+\w+)")

@view_config(context='..models.Wiki')
def view_wiki(context, request):
    return HTTPSeeOther(location=request.resource_url(context, 'FrontPage'))


@view_config(context='..models.Page', renderer='tutorial:templates/view.pt')
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
    return dict(page=context, page_text=page_text, edit_url=edit_url)


@view_config(name='add_page', context='..models.Wiki',
             renderer='tutorial:templates/edit.pt')
def add_page(context, request):
    pagename = request.subpath[0]
    if 'form.submitted' in request.params:
        body = request.params['body']
        page = Page(body)
        page.__name__ = pagename
        page.__parent__ = context
        context[pagename] = page
        return HTTPSeeOther(location=request.resource_url(page))
    save_url = request.resource_url(context, 'add_page', pagename)
    page = Page('')
    page.__name__ = pagename
    page.__parent__ = context
    return dict(page=page, save_url=save_url)


@view_config(name='edit_page', context='..models.Page',
             renderer='tutorial:templates/edit.pt')
def edit_page(context, request):
    if 'form.submitted' in request.params:
        context.data = request.params['body']
        return HTTPSeeOther(location=request.resource_url(context))

    return dict(page=context,
                save_url=request.resource_url(context, 'edit_page'))
