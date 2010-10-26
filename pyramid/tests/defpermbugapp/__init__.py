from webob import Response
from pyramid.view import bfg_view

@bfg_view(name='x')
def x_view(request):
     return Response('this is private!')

@bfg_view(name='y', permission='private2')
def y_view(request):
     return Response('this is private too!')
     
@bfg_view(name='z', permission='__no_permission_required__')
def z_view(request):
     return Response('this is public')
