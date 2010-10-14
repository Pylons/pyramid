from repoze.bfg.configuration import Configurator
from paste.deploy.converters import asbool

from tutorial.models import initialize_sql
from tutorial.models import RootFactory

def app(global_config, **settings):
    """ This function returns a WSGI application.
    
    It is usually called by the PasteDeploy framework during 
    ``paster serve``.
    """
    zcml_file = settings.get('configure_zcml', 'configure.zcml')
    db_string = settings.get('db_string')
    if db_string is None:
        raise ValueError(
            "No 'db_string' value in application configuration.")
    db_echo = settings.get('db_echo', 'false')
    initialize_sql(db_string, asbool(db_echo))
    config = Configurator(settings=settings, root_factory=RootFactory)
    config.begin()
    config.load_zcml(zcml_file)
    config.end()
    return config.make_wsgi_app()

