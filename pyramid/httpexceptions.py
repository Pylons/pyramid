"""HTTP Exceptions

HTTP Exceptions can be returned from handlers and views, or when using Python 
2.5+ may be raised as normal (Python 2.4 doesn't support raising new-style
class exceptions).

All HTTP Exceptions are sub-classes of HTTPException, with additional
sub-classes for each of the major types of HTTP Response. For example, all
200-class HTTP exceptions sub-class HTTPOk, which sub-classes HTTPException.

A status_map dict is also provided, which allows for key based access to
exception objects by the HTTP status code.

The exceptions are ordered into a class hierarchy based on status code
divisions to allow for capturing of various types of HTTP exceptions as
well.

Exception
  HTTPException
    HTTPOk
      * 200 - HTTPOk
      * 201 - HTTPCreated
      * 202 - HTTPAccepted
      * 203 - HTTPNonAuthoritativeInformation
      * 204 - HTTPNoContent
      * 205 - HTTPResetContent
      * 206 - HTTPPartialContent
    HTTPRedirection
      * 300 - HTTPMultipleChoices
      * 301 - HTTPMovedPermanently
      * 302 - HTTPFound
      * 303 - HTTPSeeOther
      * 304 - HTTPNotModified
      * 305 - HTTPUseProxy
      * 306 - Unused (not implemented, obviously)
      * 307 - HTTPTemporaryRedirect
    HTTPError
      HTTPClientError
        * 400 - HTTPBadRequest
        * 401 - HTTPUnauthorized
        * 402 - HTTPPaymentRequired
        * 403 - HTTPForbidden
        * 404 - HTTPNotFound
        * 405 - HTTPMethodNotAllowed
        * 406 - HTTPNotAcceptable
        * 407 - HTTPProxyAuthenticationRequired
        * 408 - HTTPRequestTimeout
        * 409 - HTTPConflict
        * 410 - HTTPGone
        * 411 - HTTPLengthRequired
        * 412 - HTTPPreconditionFailed
        * 413 - HTTPRequestEntityTooLarge
        * 414 - HTTPRequestURITooLong
        * 415 - HTTPUnsupportedMediaType
        * 416 - HTTPRequestRangeNotSatisfiable
        * 417 - HTTPExpectationFailed
      HTTPServerError
        * 500 - HTTPInternalServerError
        * 501 - HTTPNotImplemented
        * 502 - HTTPBadGateway
        * 503 - HTTPServiceUnavailable
        * 504 - HTTPGatewayTimeout
        * 505 - HTTPVersionNotSupported

"""
from webob.exc import status_map

# Parent classes
from webob.exc import HTTPException
from webob.exc import HTTPOk
from webob.exc import HTTPRedirection
from webob.exc import HTTPError
from webob.exc import HTTPClientError
from webob.exc import HTTPServerError

# Child classes
from webob.exc import HTTPOk
from webob.exc import HTTPCreated
from webob.exc import HTTPAccepted
from webob.exc import HTTPNonAuthoritativeInformation
from webob.exc import HTTPNoContent
from webob.exc import HTTPResetContent
from webob.exc import HTTPPartialContent
from webob.exc import HTTPMultipleChoices
from webob.exc import HTTPMovedPermanently
from webob.exc import HTTPFound
from webob.exc import HTTPSeeOther
from webob.exc import HTTPNotModified
from webob.exc import HTTPUseProxy
from webob.exc import HTTPTemporaryRedirect
from webob.exc import HTTPBadRequest
from webob.exc import HTTPUnauthorized
from webob.exc import HTTPPaymentRequired
from webob.exc import HTTPForbidden
from webob.exc import HTTPNotFound
from webob.exc import HTTPMethodNotAllowed
from webob.exc import HTTPNotAcceptable
from webob.exc import HTTPProxyAuthenticationRequired
from webob.exc import HTTPRequestTimeout
from webob.exc import HTTPConflict
from webob.exc import HTTPGone
from webob.exc import HTTPLengthRequired
from webob.exc import HTTPPreconditionFailed
from webob.exc import HTTPRequestEntityTooLarge
from webob.exc import HTTPRequestURITooLong
from webob.exc import HTTPUnsupportedMediaType
from webob.exc import HTTPRequestRangeNotSatisfiable
from webob.exc import HTTPExpectationFailed
from webob.exc import HTTPInternalServerError
from webob.exc import HTTPNotImplemented
from webob.exc import HTTPBadGateway
from webob.exc import HTTPServiceUnavailable
from webob.exc import HTTPGatewayTimeout
from webob.exc import HTTPVersionNotSupported
