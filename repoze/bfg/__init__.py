try:
    from repoze.bfg.router import make_app # for import elsewhere
    from repoze.bfg.registry import get_options # for import elsewhere
except ImportError:
    # don't try so hard that we cause setup.py test to fail when the
    # right modules aren't installed.
    pass
