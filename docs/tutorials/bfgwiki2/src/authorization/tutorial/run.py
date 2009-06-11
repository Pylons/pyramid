from repoze.bfg.router import make_app
from repoze.bfg.authentication import AuthTktAuthenticationPolicy

import tutorial
from tutorial.models import DBSession
from tutorial.models import initialize_sql
from tutorial.models import RootFactory

class Cleanup:
    def __init__(self, cleaner):
        self.cleaner = cleaner
    def __del__(self):
        self.cleaner()

def handle_teardown(event):
    environ = event.request.environ
    environ['tutorial.sasession'] = Cleanup(DBSession.remove)

def app(global_config, **kw):
    """ This function returns a repoze.bfg.router.Router object.
    
    It is usually called by the PasteDeploy framework during ``paster serve``.
    """
    db_string = kw.get('db_string')
    if db_string is None:
        raise ValueError("No 'db_string' value in application configuration.")
    initialize_sql(db_string)

    authpolicy = AuthTktAuthenticationPolicy('seekr!t', callback=groupfinder)

    return make_app(RootFactory, tutorial,  authentication_policy=authpolicy,
                    options=kw)

USERS = {'editor':'editor',
          'viewer':'viewer'}
GROUPS = {'editor':['group.editors']}

def groupfinder(userid):
    if userid in USERS:
        return GROUPS.get(userid, [])

