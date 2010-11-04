from pyramid.configuration import Configurator
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy

from paste.deploy.converters import asbool

from tutorial.models import initialize_sql
from tutorial.security import groupfinder

def app(global_config, **settings):
    """ This function returns a WSGI application.
    
    It is usually called by the PasteDeploy framework during 
    ``paster serve``.
    """
    db_string = settings.get('db_string')
    if db_string is None:
        raise ValueError("No 'db_string' value in application configuration.")
    db_echo = settings.get('db_echo', 'false')
    initialize_sql(db_string, asbool(db_echo))
    authn_policy = AuthTktAuthenticationPolicy(
        'sosecret', callback=groupfinder)
    authz_policy = ACLAuthorizationPolicy()
    config = Configurator(settings=settings,
                          root_factory='tutorial.models.RootFactory',
                          authentication_policy=authn_policy,
                          authorization_policy=authz_policy)
    config.begin()
    config.add_static_view('static', 'templates/static')
    config.add_route('view_wiki', '/', view='tutorial.views.view_wiki')
    config.add_route('login', '/login',
                     view='tutorial.login.login',
                     view_renderer='tutorial:templates/login.pt')
    config.add_route('logout', '/logout',
                     view='tutorial.login.logout')
    config.add_route('view_page', '/:pagename',
                     view='tutorial.views.view_page',
                     view_renderer='tutorial:templates/view.pt')
    config.add_route('add_page', '/add_page/:pagename',
                     view='tutorial.views.add_page',
                     view_renderer='tutorial:templates/view.pt',
                     view_permission='edit')
    config.add_route('edit_page', '/:pagename/edit_page',
                     view='tutorial.views.edit_page',
                     view_renderer='tutorial:templates/edit.pt',
                     view_permission='edit')
    config.add_view('tutorial.login.login',
                    renderer='tutorial:templates/login.pt',
                    context='pyramid.exceptions.Forbidden')
    config.end()
    return config.make_wsgi_app()

