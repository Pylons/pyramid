from pyramid.view import notfound_view_config, view_config, UseSubrequest
from pyramid.response import Response

@notfound_view_config(route_name='foo', append_slash=True)
def foo_notfound(request): # pragma: no cover
    return Response('foo_notfound')

@notfound_view_config(route_name='baz')
def baz_notfound(request):
    return Response('baz_notfound')

@notfound_view_config(append_slash=True)
def notfound(request):
    return Response('generic_notfound')

@view_config(route_name='bar')
def bar(request):
    return Response('OK bar')

@view_config(route_name='foo2')
def foo2(request):
    return Response('OK foo2')

@notfound_view_config(route_name='wiz', append_slash=UseSubrequest)
def wiz_notfound(request): # pragma: no cover
    return Response('wiz_notfound')

@view_config(route_name='wiz2')
def wiz2(request):
    return Response('OK wiz2')

def includeme(config):
    config.add_route('foo', '/foo')
    config.add_route('foo2', '/foo/')
    config.add_route('bar', '/bar/')
    config.add_route('baz', '/baz')
    config.add_route('wiz', '/wiz')
    config.add_route('wiz2', '/wiz/')
    config.scan('pyramid.tests.pkgs.notfoundview')
    
