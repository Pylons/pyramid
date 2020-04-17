class RootFactory:
    __acl__ = [('Allow', 'fred', 'view')]

    def __init__(self, request):
        pass


class LocalRootFactory:
    __acl__ = [('Allow', 'bob', 'view')]

    def __init__(self, request):
        pass


def includeme(config):
    from pyramid.authentication import RemoteUserAuthenticationPolicy
    from pyramid.authorization import ACLAuthorizationPolicy

    authn_policy = RemoteUserAuthenticationPolicy()
    authz_policy = ACLAuthorizationPolicy()
    config.set_authentication_policy(authn_policy)
    config.set_authorization_policy(authz_policy)
    config.add_static_view('allowed', 'tests:fixtures/static/')
    config.add_static_view(
        'protected', 'tests:fixtures/static/', permission='view'
    )
    config.add_static_view(
        'factory_protected',
        'tests:fixtures/static/',
        permission='view',
        factory=LocalRootFactory,
    )
