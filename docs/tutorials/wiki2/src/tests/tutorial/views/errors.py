from pyramid.httpexceptions import HTTPFound
from pyramid.view import (
    forbidden_view_config,
    notfound_view_config,
)

@notfound_view_config(renderer='../templates/404.jinja2')
def notfound_view(request):
    return {}

@forbidden_view_config()
def forbidden_view(request):
    next_url = request.route_url('login', _query={'came_from': request.url})
    return HTTPFound(location=next_url)
