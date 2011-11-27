from pyramid.config import Configurator
from sqlalchemy import engine_from_config

from .models import DBSession

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    config = Configurator(settings=settings)
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('view_wiki', '/')
    config.add_route('view_page', '/{pagename}')
    config.add_route('add_page', '/add_page/{pagename}')
    config.add_route('edit_page', '/{pagename}/edit_page')
    config.scan()
    return config.make_wsgi_app()
