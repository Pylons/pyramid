from webob import Response

from pyramid.security import NO_PERMISSION_REQUIRED
from pyramid.view import view_config


@view_config(name='x')
def x_view(request):  # pragma: no cover
    return Response('this is private!')


@view_config(name='y', permission='private2')
def y_view(request):  # pragma: no cover
    return Response('this is private too!')


@view_config(name='z', permission=NO_PERMISSION_REQUIRED)
def z_view(request):
    return Response('this is public')


def includeme(config):
    from pyramid.authentication import AuthTktAuthenticationPolicy
    from pyramid.authorization import ACLAuthorizationPolicy

    authn_policy = AuthTktAuthenticationPolicy('seekt1t', hashalg='sha512')
    authz_policy = ACLAuthorizationPolicy()
    config.scan('tests.pkgs.defpermbugapp')
    config.set_authentication_policy(authn_policy)
    config.set_authorization_policy(authz_policy)
    config.set_default_permission('private')
