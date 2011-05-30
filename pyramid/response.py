from webob import Response as _Response
from zope.interface import implements

from pyramid.interfaces import IExceptionResponse

class Response(_Response, Exception):
    implements(IExceptionResponse)
    
