from webob import Response
from pyramid.view import view_config

@view_config(name='x')
def x_view(request): # pragma: no cover
     return Response('this is private!')

@view_config(name='y', permission='private2')
def y_view(request): # pragma: no cover
     return Response('this is private too!')
     
@view_config(name='z', permission='__no_permission_required__')
def z_view(request):
     return Response('this is public')
