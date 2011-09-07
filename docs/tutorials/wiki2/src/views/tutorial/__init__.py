from pyramid.config import Configurator
from sqlalchemy import engine_from_config

from tutorial.models import initialize_sql

def main(global_config, **settings):
    """ This function returns a WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    initialize_sql(engine)
    config = Configurator(settings=settings)
    config.add_static_view('static', 'tutorial:static', cache_max_age=3600)
    config.add_route('view_wiki', '/')
    config.add_route('view_page', '/{pagename}')
    config.add_route('add_page', '/add_page/{pagename}')
    config.add_route('edit_page', '/{pagename}/edit_page')
    config.add_view('tutorial.views.view_wiki', route_name='view_wiki')
    config.add_view('tutorial.views.view_page', route_name='view_page',
                    renderer='tutorial:templates/view.pt')
    config.add_view('tutorial.views.add_page', route_name='add_page',
                    renderer='tutorial:templates/edit.pt')
    config.add_view('tutorial.views.edit_page', route_name='edit_page',
                    renderer='tutorial:templates/edit.pt')
    return config.make_wsgi_app()

