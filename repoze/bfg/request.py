from zope.interface import implements
from webob import Request as WebobRequest

import repoze.bfg.interfaces

# We use 'precooked' Request subclasses that correspond to HTTP
# request methods within ``router.py`` when constructing a request
# object rather than using ``alsoProvides`` to attach the proper
# interface to an unsubclassed webob.Request.  This pattern is purely
# an optimization (e.g. preventing calls to ``alsoProvides`` means the
# difference between 590 r/s and 690 r/s on a MacBook 2GHz).  These
# classes are *not* APIs.  None of these classes, nor the
# ``HTTP_METHOD_FACTORIES`` lookup dict should be imported directly by
# user code.

class Request(WebobRequest):
    implements(repoze.bfg.interfaces.IRequest)

class GETRequest(WebobRequest):
    implements(repoze.bfg.interfaces.IGETRequest)

class POSTRequest(WebobRequest):
    implements(repoze.bfg.interfaces.IPOSTRequest)

class PUTRequest(WebobRequest):
    implements(repoze.bfg.interfaces.IPUTRequest)

class DELETERequest(WebobRequest):
    implements(repoze.bfg.interfaces.IDELETERequest)

class HEADRequest(WebobRequest):
    implements(repoze.bfg.interfaces.IHEADRequest)

HTTP_METHOD_FACTORIES = {
    'GET':GETRequest,
    'POST':POSTRequest,
    'PUT':PUTRequest,
    'DELETE':DELETERequest,
    'HEAD':HEADRequest,
    }

