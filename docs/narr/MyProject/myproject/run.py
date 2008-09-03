from repoze.bfg.router import make_app
from repoze.bfg.registry import get_options

def app(global_config, **kw):
    """ This function returns a repoze.bfg.router.Router object.  It
    is usually called by the PasteDeploy framework during ``paster
    serve``"""
    from myproject.models import get_root
    import myproject
    options = get_options(kw)
    return make_app(get_root, myproject, options=options)
