from cgi import escape
from pyramid.security import view_execution_permitted
from webob import Response

def x_view(request): # pragma: no cover
     return Response('this is private!')

def test(context, request):
    # should return false
     msg = 'Allow ./x? %s' % repr(view_execution_permitted(
         context, request, 'x'))
     return Response(escape(msg))
