from repoze.bfg.router import make_app

def app(global_config, **kw):
    """ This function returns a repoze.bfg.router.Router object.  It
    is usually called by the PasteDeploy framework during ``paster
    serve``"""
    from myproject.models import get_root
    import myproject
    return make_app(get_root, myproject, options=kw)
