from pyramid.config import Configurator
from pyramid_zodbconn import get_connection
from .models import appmaker


def root_factory(request):
    conn = get_connection(request)
    return appmaker(conn.root())


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    settings['tm.manager_hook'] = 'pyramid_tm.explicit_manager'
    with Configurator(settings=settings) as config:
        config.include('pyramid_chameleon')
        config.include('pyramid_tm')
        config.include('pyramid_retry')
        config.include('pyramid_zodbconn')
        config.set_root_factory(root_factory)
        config.add_static_view('static', 'static', cache_max_age=3600)
        config.scan()
        return config.make_wsgi_app()
