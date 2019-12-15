from pyramid.response import Response
from pyramid.security import Allowed, Denied


class SecurityPolicy:
    def identify(self, request):
        raise NotImplementedError()  # pragma: no cover

    def authenticated_userid(self, request):
        return request.environ.get('REMOTE_USER')

    def permits(self, request, context, permission):
        userid = self.authenticated_userid(request)
        if userid and permission == 'foo':
            return Allowed('')
        else:
            return Denied('')

    def remember(self, request, userid, **kw):
        raise NotImplementedError()  # pragma: no cover

    def forget(self, request, **kw):
        raise NotImplementedError()  # pragma: no cover


def public(context, request):
    return Response('Hello')


def private(context, request):
    return Response('Secret')


def inaccessible(context, request):
    raise AssertionError()  # pragma: no cover


def includeme(config):
    config.set_security_policy(SecurityPolicy())
    config.add_route('public', '/public')
    config.add_view(public, route_name='public')
    config.add_route('private', '/private')
    config.add_view(private, route_name='private', permission='foo')
    config.add_route('inaccessible', '/inaccessible')
    config.add_view(inaccessible, route_name='inaccessible', permission='bar')
