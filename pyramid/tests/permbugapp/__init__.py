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

def includeme(config):
     from pyramid.authentication import AuthTktAuthenticationPolicy
     from pyramid.authorization import ACLAuthorizationPolicy
     authn_policy = AuthTktAuthenticationPolicy('seekt1t')
     authz_policy = ACLAuthorizationPolicy()
     config._set_authentication_policy(authn_policy)
     config._set_authorization_policy(authz_policy)
     config.add_view(test, name='test')
     config.add_view(x_view, name='x', permission='private')
