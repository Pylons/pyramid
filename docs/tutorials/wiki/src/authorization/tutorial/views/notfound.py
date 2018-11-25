from pyramid.view import notfound_view_config

from ..models import Page


@notfound_view_config(renderer='../templates/404.pt')
def notfound_view(request):
    request.response.status = 404
    pagename = request.path
    page = Page(pagename)
    page.__name__ = pagename
    return dict(page=page)
