from zope.component import getUtility
from zope.interface import implements
from webob import Request as WebobRequest

from zope.deprecation import deprecated
from zope.interface.interface import InterfaceClass

from repoze.bfg.interfaces import IRequest
from repoze.bfg.interfaces import IGETRequest
from repoze.bfg.interfaces import IPOSTRequest
from repoze.bfg.interfaces import IPUTRequest
from repoze.bfg.interfaces import IDELETERequest
from repoze.bfg.interfaces import IHEADRequest
from repoze.bfg.interfaces import IRequestFactories

def request_factory(environ):
    try:
        method = environ['REQUEST_METHOD']
    except KeyError:
        method = None

    if 'bfg.routes.route' in environ:
        route = environ['bfg.routes.route']
        request_factories = getUtility(IRequestFactories, name=route.name or '')
    else:
        request_factories = DEFAULT_REQUEST_FACTORIES

    try:
        request_factory = request_factories[method]['factory']
    except KeyError:
        request_factory = request_factories[None]['factory']

    return request_factory(environ)

def make_request_ascii(event):
    """ An event handler that causes the request charset to be ASCII;
    used as an INewRequest subscriber so code written before 0.7.0 can
    continue to work without a change"""
    request = event.request
    request.charset = None

def named_request_factories(name=None):
    # We use 'precooked' Request subclasses that correspond to HTTP
    # request methods when returning a request object from
    # ``request_factory`` rather than using ``alsoProvides`` to attach
    # the proper interface to an unsubclassed webob.Request.  This
    # pattern is purely an optimization (e.g. preventing calls to
    # ``alsoProvides`` means the difference between 590 r/s and 690
    # r/s on a MacBook 2GHz).  This method should be never imported
    # directly by user code; it is *not* an API.
    if name is None:
        default_iface = IRequest
        get_iface = IGETRequest
        post_iface = IPOSTRequest
        put_iface = IPUTRequest
        delete_iface = IDELETERequest
        head_iface = IHEADRequest
    else:
        IC = InterfaceClass
        default_iface = IC('%s_IRequest' % name, (IRequest,))
        get_iface = IC('%s_IGETRequest' % name, (default_iface, IGETRequest))
        post_iface = IC('%s_IPOSTRequest' % name, (default_iface, IPOSTRequest))
        put_iface = IC('%s_IPUTRequest' % name, (default_iface, IPUTRequest))
        delete_iface = IC('%s_IDELETERequest' % name, (default_iface,
                                                       IDELETERequest))
        head_iface = IC('%s_IHEADRequest' % name, (default_iface,
                                                   IHEADRequest,))
        
    class Request(WebobRequest):
        implements(default_iface)
        charset = 'utf-8'

    class GETRequest(WebobRequest):
        implements(get_iface)
        charset = 'utf-8'

    class POSTRequest(WebobRequest):
        implements(post_iface)
        charset = 'utf-8'
    
    class PUTRequest(WebobRequest):
        implements(put_iface)
        charset = 'utf-8'

    class DELETERequest(WebobRequest):
        implements(delete_iface)
        charset = 'utf-8'

    class HEADRequest(WebobRequest):
        implements(head_iface)
        charset = 'utf-8'

    factories = {
        IRequest:{'interface':default_iface, 'factory':Request},
        IGETRequest:{'interface':get_iface, 'factory':GETRequest},
        IPOSTRequest:{'interface':post_iface, 'factory':POSTRequest},
        IPUTRequest:{'interface':put_iface, 'factory':PUTRequest},
        IDELETERequest:{'interface':delete_iface, 'factory':DELETERequest},
        IHEADRequest:{'interface':head_iface, 'factory':HEADRequest},
        None:{'interface':default_iface, 'factory':Request},
        'GET':{'interface':get_iface, 'factory':GETRequest},
        'POST':{'interface':post_iface, 'factory':POSTRequest},
        'PUT':{'interface':put_iface, 'factory':PUTRequest},
        'DELETE':{'interface':delete_iface, 'factory':DELETERequest},
        'HEAD':{'interface':head_iface, 'factory':HEADRequest},
        }

    return factories

DEFAULT_REQUEST_FACTORIES = named_request_factories()

from repoze.bfg.threadlocal import get_current_request as get_request # b/c

deprecated('get_request',
           'As of repoze.bfg 1.0, any import of get_request from'
           '``repoze.bfg.request`` is '
           'deprecated.  Use ``from repoze.bfg.threadlocal import '
           'get_current_request instead.')
