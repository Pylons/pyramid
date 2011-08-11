try:
    import json
except ImportError: # pragma: no cover
    try:
        import simplejson as json
    except NotImplementedError:
        from django.utils import simplejson as json # GAE

