from pyramid.response import Response
from pyramid.view import view_config


# Start Route 1
@view_config(route_name='hello')
def hello_world(request):
    body = '<h1>Hi %(first)s %(last)s!</h1>' % request.matchdict
    return Response(body)
    # End Route 1