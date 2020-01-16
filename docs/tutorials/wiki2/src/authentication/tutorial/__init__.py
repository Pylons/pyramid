from pyramid.config import Configurator


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    with Configurator(settings=settings) as config:
        config.include('pyramid_jinja2')
        config.include('.security')
        config.include('.routes')
        config.include('.models')
        config.scan()
    return config.make_wsgi_app()
