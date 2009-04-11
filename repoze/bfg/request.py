from zope.interface import implements
from webob import Request as WebobRequest

import repoze.bfg.interfaces

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
# ``HTTP_METHOD_FACTORIES`` lookup dict should be imported directly by
# user code.

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

