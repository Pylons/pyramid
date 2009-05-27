from repoze.bfg.router import make_app
from repoze.zodbconn.finder import PersistentApplicationFinder

def app(global_config, **kw):
    """ This function returns a repoze.bfg.router.Router object.
    
    It is usually called by the PasteDeploy framework during ``paster serve``.
    """
    # paster app config callback
    import tutorial
    from tutorial.models import appmaker
    zodb_uri = kw.get('zodb_uri')
    if zodb_uri is None:
        raise ValueError("No 'zodb_uri' in application configuration.")

    get_root = PersistentApplicationFinder(zodb_uri, appmaker)
    return make_app(get_root, tutorial, options=kw)
