from pyramid.configuration import Configurator
from pyramid.settings import asbool

from tutorial.models import initialize_sql

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    db_string = settings.get('db_string')
    if db_string is None:
        raise ValueError("No 'db_string' value in application configuration.")
    db_echo = settings.get('db_echo', 'false')
    initialize_sql(db_string, asbool(db_echo))
    config = Configurator(settings=settings)
    config.begin()
    config.add_static_view('static', 'tutorial:static')
    config.add_route('home', '/', view='tutorial.views.my_view',
                     view_renderer='templates/mytemplate.pt')
    config.end()
    return config.make_wsgi_app()


