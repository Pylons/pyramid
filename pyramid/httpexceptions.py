"""
HTTP Exceptions
---------------

This module contains Pyramid HTTP exception classes.  Each class relates to a
single HTTP status code.  Each class is a subclass of the
:class:`~HTTPException`.  Each exception class is also a :term:`response`
object.

Each exception class has a status code according to `RFC 2068
<http://www.ietf.org/rfc/rfc2068.txt>`: codes with 100-300 are not really
errors; 400's are client errors, and 500's are server errors.

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

Each HTTP exception has the following attributes:

   ``code``
       the HTTP status code for the exception

   ``title``
       remainder of the status line (stuff after the code)

   ``explanation``
       a plain-text explanation of the error message that is
       not subject to environment or header substitutions;
       it is accessible in the template via ${explanation}

   ``detail``
       a plain-text message customization that is not subject
       to environment or header substitutions; accessible in
       the template via ${detail}

   ``body_template``
       a ``String.template``-format content fragment used for environment
       and header substitution; the default template includes both
       the explanation and further detail provided in the
       message.

Each HTTP exception accepts the following parameters:

   ``detail``
     a plain-text override of the default ``detail``

   ``headers``
     a list of (k,v) header pairs

   ``comment``
     a plain-text additional information which is
     usually stripped/hidden for end-users

   ``body_template``
     a ``string.Template`` object containing a content fragment in HTML
     that frames the explanation and further detail

Substitution of response headers into template values is always performed.
Substitution of WSGI environment values is performed if a ``request`` is
passed to the exception's constructor.

The subclasses of :class:`~_HTTPMove` 
(:class:`~HTTPMultipleChoices`, :class:`~HTTPMovedPermanently`,
:class:`~HTTPFound`, :class:`~HTTPSeeOther`, :class:`~HTTPUseProxy` and
:class:`~HTTPTemporaryRedirect`) are redirections that require a ``Location`` 
field. Reflecting this, these subclasses have one additional keyword argument:
``location``, which indicates the location to which to redirect.
"""

from pyramid.response import * # API



