from zope.interface import implements

from repoze.bfg.interfaces import INewRequest
from repoze.bfg.interfaces import INewResponse

class NewRequest(object):
    """ An instance of this class is emitted as an event whenever
    repoze.bfg begins to process a new request.  The instance has an
    attribute, ``request``, which is the request object.  This class
    implements the ``repoze.bfg.interfaces.INewRequest`` interface."""
    implements(INewRequest)
    def __init__(self, request):
        self.request = request

class NewResponse(object):
    """ An instance of this class is emitted as an event whenever any
    repoze.bfg view returns a response..  The instance has an
    attribute, ``response``, which is the response object returned by
    the view.  This class implements the
    ``repoze.bfg.interfaces.INewResponse`` interface."""
    implements(INewResponse)
    def __init__(self, response):
        self.response = response
