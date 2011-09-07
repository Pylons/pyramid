from pyramid.config import Configurator
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy

from sqlalchemy import engine_from_config

from tutorial.models import initialize_sql
from tutorial.security import groupfinder

def main(global_config, **settings):
    """ This function returns a WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    initialize_sql(engine)
    authn_policy = AuthTktAuthenticationPolicy(
        'sosecret', callback=groupfinder)
    authz_policy = ACLAuthorizationPolicy()
    config = Configurator(settings=settings,
                          root_factory='tutorial.models.RootFactory',
                          authentication_policy=authn_policy,
                          authorization_policy=authz_policy)
    config.add_static_view('static', 'tutorial:static', cache_max_age=3600)

    config.add_route('view_wiki', '/')
    config.add_route('login', '/login')
    config.add_route('logout', '/logout')
    config.add_route('view_page', '/{pagename}')
    config.add_route('add_page', '/add_page/{pagename}')
    config.add_route('edit_page', '/{pagename}/edit_page')

    config.add_view('tutorial.views.view_wiki', route_name='view_wiki')
    config.add_view('tutorial.login.login', route_name='login', 
                    renderer='tutorial:templates/login.pt')
    config.add_view('tutorial.login.logout', route_name='logout')
    config.add_view('tutorial.views.view_page', route_name='view_page',
                    renderer='tutorial:templates/view.pt')
    config.add_view('tutorial.views.add_page', route_name='add_page',
                    renderer='tutorial:templates/edit.pt', permission='edit')
    config.add_view('tutorial.views.edit_page', route_name='edit_page',
                    renderer='tutorial:templates/edit.pt', permission='edit')
    config.add_view('tutorial.login.login',
                    context='pyramid.httpexceptions.HTTPForbidden',
                    renderer='tutorial:templates/login.pt')
    return config.make_wsgi_app()

