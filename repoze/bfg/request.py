from zope.interface import implements
from webob import Request as WebobRequest

import repoze.bfg.interfaces

from repoze.bfg.threadlocal import manager

def current_request():
    """Return the currently active request or ``None`` if no request
    is currently active.

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

def make_request_ascii(event):
    """ An event handler that causes the request charset to be ASCII;
    used as an INewRequest subscriber so code written before 0.7.0 can
    continue to work without a change"""
    request = event.request
    request.charset = None

class Request(WebobRequest):
    implements(repoze.bfg.interfaces.IRequest)
    charset = 'utf-8'

# We use 'precooked' Request subclasses that correspond to HTTP
# request methods within ``router.py`` when constructing a request
# object rather than using ``alsoProvides`` to attach the proper
# interface to an unsubclassed webob.Request.  This pattern is purely
# an optimization (e.g. preventing calls to ``alsoProvides`` means the
# difference between 590 r/s and 690 r/s on a MacBook 2GHz).  These
# classes are *not* APIs.  None of these classes, nor the
# ``HTTP_METHOD_FACTORIES`` or ``HTTP_METHOD_INTERFACES`` lookup dicts
# should be imported directly by user code.

class GETRequest(WebobRequest):
    implements(repoze.bfg.interfaces.IGETRequest)
    charset = 'utf-8'

class POSTRequest(WebobRequest):
    implements(repoze.bfg.interfaces.IPOSTRequest)
    charset = 'utf-8'

class PUTRequest(WebobRequest):
    implements(repoze.bfg.interfaces.IPUTRequest)
    charset = 'utf-8'

class DELETERequest(WebobRequest):
    implements(repoze.bfg.interfaces.IDELETERequest)
    charset = 'utf-8'

class HEADRequest(WebobRequest):
    implements(repoze.bfg.interfaces.IHEADRequest)
    charset = 'utf-8'

HTTP_METHOD_FACTORIES = {
    'GET':GETRequest,
    'POST':POSTRequest,
    'PUT':PUTRequest,
    'DELETE':DELETERequest,
    'HEAD':HEADRequest,
    }

HTTP_METHOD_INTERFACES = {
    'GET':repoze.bfg.interfaces.IGETRequest,
    'POST':repoze.bfg.interfaces.IPOSTRequest,
    'PUT':repoze.bfg.interfaces.IPUTRequest,
    'DELETE':repoze.bfg.interfaces.IDELETERequest,
    'HEAD':repoze.bfg.interfaces.IHEADRequest,
    }
    
