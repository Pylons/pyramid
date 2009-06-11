from zope.interface import implements
from webob import Request as WebobRequest

from zope.interface.interface import InterfaceClass

from repoze.bfg.interfaces import IRequest
from repoze.bfg.interfaces import IGETRequest
from repoze.bfg.interfaces import IPOSTRequest
from repoze.bfg.interfaces import IPUTRequest
from repoze.bfg.interfaces import IDELETERequest
from repoze.bfg.interfaces import IHEADRequest

from repoze.bfg.threadlocal import manager

def current_request():
    """Return the currently active request or ``None`` if no request
    is currently active.  This is *not* an official API, but it's
    going to live here 'forever' and so can be relied on to exist.

    **This function should be used extremely sparingly** (read: almost
    never), because its usage makes it possible to write code that can
    be neither easily tested nor scripted.  The author of this
    function reserves the right to point and laugh at code which uses
    it inappropriately.  Inappropriate usage is defined as follows:

    - This function should never be called within :term:`view` code.
      View code already has access to the request (it's passed in).

    - This function should never be called in :term:`model` code.
      Model code should never require any access to the request; if
      your model code requires access to a request object, you've
      almost certainly factored something wrong, and you should change
      your code rather than using this function.

    - This function should never be called within application-specific
      forks of third-party library code.  The library you've forked
      almost certainly has nothing to do with repoze.bfg, and making
      it dependent on repoze.bfg (rather than making your repoze.bfg
      application depend upon it) means you're forming a dependency in
      the wrong direction.

    - This function should never be called because it's 'easier' or
      'more elegant' to think about calling it than to pass a request
      through a series of function calls when creating some API
      design.  Your application should instead almost certainly pass
      data derived from the request around rather than relying on
      being able to call this function to obtain the request in places
      that actually have no business knowing about it.  Parameters are
      meant to be passed around as function arguments, not obtained
      from some pseudo-global.  Don't try to 'save typing' or create
      'nicer APIs' by using this function in the place where a request
      is required; this will only lead to sadness later.

    However, this function *is* still useful in very limited
    circumstances.  As a rule of thumb, usage of ``current_request``
    is useful **within code which is meant to eventually be removed**.
    For instance, you may find yourself wanting to deprecate some API
    that expects to be passed a request object in favor of one that
    does not expect to be passed a request object.  But you need to
    keep implementations of the old API working for some period of
    time while you deprecate the older API.  So you write a 'facade'
    implementation of the new API which calls into the code which
    implements the older API.  Since the new API does not require the
    request, your facade implementation doesn't have local access to
    the request when it needs to pass it into the older API
    implementaton.  After some period of time, the older
    implementation code is disused and the hack that uses
    ``current_request`` is removed.  This would be an appropriate
    place to use the ``current_request`` function.

    ``current_request`` retrieves a request object from a thread-local
    stack that is managed by a :term:`Router` object.  Therefore the
    very definition of 'current request' is defined entirely by the
    behavior of a repoze.bfg Router.  Scripts which use
    :mod:`repoze.bfg` machinery but never actually start a WSGI server
    or receive requests via HTTP (such as scripts which use the
    :mod:`repoze.bfg.scripting`` API) will never cause any Router code
    to be executed.  Such scripts should expect this function to
    always return ``None``.
    """
    return manager.get()['request']

def request_factory(environ):
    try:
        method = environ['REQUEST_METHOD']
    except KeyError:
        method = None

    if 'bfg.routes.route' in environ:
        route = environ['bfg.routes.route']
        request_factories = route.request_factories
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
        default_iface = InterfaceClass('%s_IRequest' % name)
        get_iface = InterfaceClass('%s_IGETRequest' % name, (default_iface,))
        post_iface = InterfaceClass('%s_IPOSTRequest' % name, (default_iface,))
        put_iface = InterfaceClass('%s_IPUTRequest' % name, (default_iface,))
        delete_iface = InterfaceClass('%s_IDELETERequest' % name,
                                      (default_iface,))
        head_iface = InterfaceClass('%s_IHEADRequest' % name, (default_iface))
        
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

