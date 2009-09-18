from zope.component import queryUtility
from zope.deprecation import deprecated
from zope.interface import implements
from zope.interface.interface import InterfaceClass

from webob import Request as WebobRequest

from repoze.bfg.interfaces import IRequest
from repoze.bfg.interfaces import IRouteRequest

def make_request_ascii(event):
    """ An event handler that causes the request charset to be ASCII;
    used as an INewRequest subscriber so code written before 0.7.0 can
    continue to work without a change"""
    request = event.request
    request.charset = None

class Request(WebobRequest):
    implements(IRequest)
    charset = 'utf-8'

def request_factory(environ):
    if 'bfg.routes.route' in environ:
        route = environ['bfg.routes.route']
        factory = queryUtility(IRouteRequest, name=route.name)
        if factory is not None:
            return factory(environ)
    return Request(environ)

def create_route_request_factory(name):
    iface = InterfaceClass('%s_IRequest' % name, (IRouteRequest,))
        
    class RouteRequest(WebobRequest):
        implements(iface)
        charset = 'utf-8'

    return RouteRequest

from repoze.bfg.threadlocal import get_current_request as get_request # b/c

deprecated('get_request',
           'As of repoze.bfg 1.0, any import of get_request from'
           '``repoze.bfg.request`` is '
           'deprecated.  Use ``from repoze.bfg.threadlocal import '
           'get_current_request instead.')
