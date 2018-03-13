from pyramid.config import Configurator
from pyramid_zodbconn import get_connection

from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy

from .models import appmaker
from .security import groupfinder

def root_factory(request):
    conn = get_connection(request)
    return appmaker(conn.root())


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    settings['tm.manager_hook'] = 'pyramid_tm.explicit_manager'
    authn_policy = AuthTktAuthenticationPolicy(
        'sosecret', callback=groupfinder, hashalg='sha512')
    authz_policy = ACLAuthorizationPolicy()
    with Configurator(settings=settings) as config:
        config.set_authentication_policy(authn_policy)
        config.set_authorization_policy(authz_policy)
        config.include('pyramid_chameleon')
        config.include('pyramid_tm')
        config.include('pyramid_retry')
        config.include('pyramid_zodbconn')
        config.set_root_factory(root_factory)
        config.add_static_view('static', 'static', cache_max_age=3600)
        config.scan()
        return config.make_wsgi_app()
