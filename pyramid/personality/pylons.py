from pyramid.threadlocal import get_current_request
from pyramid.url import route_url

def renderer_globals_factory_config(helpers):
    """ Return a Pylons renderer globals factory using ``helpers`` as
    a helpers key."""
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

