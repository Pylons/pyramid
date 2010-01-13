import transaction

from repoze.bfg.configuration import Configurator
from repoze.tm import after_end
from repoze.tm import isActive

from tutorial.models import DBSession
from tutorial.models import initialize_sql

def handle_teardown(event):
    environ = event.request.environ
    if isActive(environ):
        t = transaction.get()
        after_end.register(DBSession.remove, t)

def app(global_config, **settings):
    """ This function returns a WSGI application.
    
    It is usually called by the PasteDeploy framework during 
    ``paster serve``.
    """
    db_string = settings.get('db_string')
    if db_string is None:
        raise ValueError("No 'db_string' value in application "
                         "configuration.")
    initialize_sql(db_string)
    config = Configurator(settings=settings)
    config.begin()
    config.load_zcml('configure.zcml')
    config.end()
    return config.make_wsgi_app()
