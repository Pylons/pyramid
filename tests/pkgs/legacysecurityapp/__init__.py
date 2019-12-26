from pyramid.authentication import RemoteUserAuthenticationPolicy
from pyramid.response import Response
from pyramid.security import Allowed, Denied


class AuthorizationPolicy:
    def permits(self, context, principals, permission):
        if 'bob' in principals and permission == 'foo':
            return Allowed('')
        else:
            return Denied('')

    def principals_allowed_by_permission(self, context, permission):
        raise NotImplementedError()  # pragma: no cover


def public(context, request):
    return Response('Hello')


def private(context, request):
    return Response('Secret')


def inaccessible(context, request):
    raise AssertionError()  # pragma: no cover


def includeme(config):
    config.set_authentication_policy(RemoteUserAuthenticationPolicy())
    config.set_authorization_policy(AuthorizationPolicy())
    config.add_route('public', '/public')
    config.add_view(public, route_name='public')
    config.add_route('private', '/private')
    config.add_view(private, route_name='private', permission='foo')
    config.add_route('inaccessible', '/inaccessible')
    config.add_view(inaccessible, route_name='inaccessible', permission='bar')
