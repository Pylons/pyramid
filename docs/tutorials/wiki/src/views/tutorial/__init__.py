from pyramid.config import Configurator
from repoze.zodbconn.finder import PersistentApplicationFinder
from tutorial.models import appmaker

def main(global_config, **settings):
    """ This function returns a WSGI application.
    """
    zodb_uri = settings.get('zodb_uri', False)
    if zodb_uri is False:
        raise ValueError("No 'zodb_uri' in application configuration.")

    finder = PersistentApplicationFinder(zodb_uri, appmaker)
    def get_root(request):
        return finder(request.environ)
    config = Configurator(root_factory=get_root, settings=settings)
    config.add_static_view('static', 'tutorial:static')
    config.scan('tutorial')
    return config.make_wsgi_app()
