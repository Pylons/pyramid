from pyramid.threadlocal import get_current_request
from pyramid.url import route_url

def renderer_globals_factory_config(helpers):
    """ Return a :term:`renderer globals` factory useful in applications that
    behave like :term:`Pylons` using the ``helpers`` argument passed as a the
    ``helpers`` key (should be a Python module)."""
    def renderer_globals_factory(system):
        req = system['request']
        if req is None:
            req = get_current_request()
        renderer_globals = {
            'url': route_url,
            'h': helpers,
            'request':req,
            }
        if req is not None:
            tmpl_context = req.tmpl_context
            renderer_globals['c'] = tmpl_context
            renderer_globals['tmpl_context'] = tmpl_context
            if 'session' in req.__dict__:
                renderer_globals['session'] = req.session
        return renderer_globals
    return renderer_globals_factory

