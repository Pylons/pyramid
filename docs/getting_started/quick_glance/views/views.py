from pyramid.response import Response
from pyramid.view import view_config


@view_config(route_name='hello')
def hello_world(request):
    return Response('<h1>Hello %(name)s!</h1>' % request.matchdict)
