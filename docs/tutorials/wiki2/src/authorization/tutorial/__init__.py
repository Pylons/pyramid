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
    config.add_static_view('static', 'tutorial:static')
    config.add_route('view_wiki', '/', view='tutorial.views.view_wiki')
    config.add_route('login', '/login',
                     view='tutorial.login.login',
                     view_renderer='tutorial:templates/login.pt')
    config.add_route('logout', '/logout',
                     view='tutorial.login.logout')
    config.add_route('view_page', '/{pagename}',
                     view='tutorial.views.view_page',
                     view_renderer='tutorial:templates/view.pt')
    config.add_route('add_page', '/add_page/{pagename}',
                     view='tutorial.views.add_page',
                     view_renderer='tutorial:templates/edit.pt',
                     view_permission='edit')
    config.add_route('edit_page', '/{pagename}/edit_page',
                     view='tutorial.views.edit_page',
                     view_renderer='tutorial:templates/edit.pt',
                     view_permission='edit')
    config.add_view('tutorial.login.login',
                    renderer='tutorial:templates/login.pt',
                    context='pyramid.exceptions.Forbidden')
    return config.make_wsgi_app()

