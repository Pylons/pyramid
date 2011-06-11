from webob import Response as _Response
from zope.interface import implements
from pyramid.interfaces import IResponse

class Response(_Response):
    implements(IResponse)
    
