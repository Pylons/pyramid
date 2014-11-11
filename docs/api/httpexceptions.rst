.. _httpexceptions_module:

:mod:`pyramid.httpexceptions`
--------------------------------

.. automodule:: pyramid.httpexceptions

  .. attribute:: status_map

     A mapping of integer status code to HTTP exception class (eg. the integer
     "401" maps to :class:`pyramid.httpexceptions.HTTPUnauthorized`).  All
     mapped exception classes are children of :class:`pyramid.httpexceptions`,

  .. autofunction:: exception_response

  .. autoexception:: HTTPException

  .. autoexception:: HTTPOk

  .. autoexception:: HTTPRedirection

  .. autoexception:: HTTPError

  .. autoexception:: HTTPClientError

  .. autoexception:: HTTPServerError

  .. autoexception:: HTTPCreated

  .. autoexception:: HTTPAccepted

  .. autoexception:: HTTPNonAuthoritativeInformation

  .. autoexception:: HTTPNoContent

  .. autoexception:: HTTPResetContent

  .. autoexception:: HTTPPartialContent

  .. autoexception:: HTTPMultipleChoices

  .. autoexception:: HTTPMovedPermanently

  .. autoexception:: HTTPFound

  .. autoexception:: HTTPSeeOther

  .. autoexception:: HTTPNotModified

  .. autoexception:: HTTPUseProxy

  .. autoexception:: HTTPTemporaryRedirect

  .. autoexception:: HTTPBadRequest

  .. autoexception:: HTTPUnauthorized

  .. autoexception:: HTTPPaymentRequired

  .. autoexception:: HTTPForbidden

  .. autoexception:: HTTPNotFound

  .. autoexception:: HTTPMethodNotAllowed

  .. autoexception:: HTTPNotAcceptable

  .. autoexception:: HTTPProxyAuthenticationRequired

  .. autoexception:: HTTPRequestTimeout

  .. autoexception:: HTTPConflict

  .. autoexception:: HTTPGone

  .. autoexception:: HTTPLengthRequired

  .. autoexception:: HTTPPreconditionFailed

  .. autoexception:: HTTPRequestEntityTooLarge

  .. autoexception:: HTTPRequestURITooLong

  .. autoexception:: HTTPUnsupportedMediaType

  .. autoexception:: HTTPRequestRangeNotSatisfiable

  .. autoexception:: HTTPExpectationFailed

  .. autoexception:: HTTPUnprocessableEntity

  .. autoexception:: HTTPLocked

  .. autoexception:: HTTPFailedDependency

  .. autoexception:: HTTPInternalServerError

  .. autoexception:: HTTPNotImplemented

  .. autoexception:: HTTPBadGateway

  .. autoexception:: HTTPServiceUnavailable

  .. autoexception:: HTTPGatewayTimeout

  .. autoexception:: HTTPVersionNotSupported

  .. autoexception:: HTTPInsufficientStorage
