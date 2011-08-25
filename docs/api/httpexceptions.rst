.. _httpexceptions_module:

:mod:`pyramid.httpexceptions`
--------------------------------

.. automodule:: pyramid.httpexceptions

  .. attribute:: status_map

     A mapping of integer status code to exception class (eg. the
     integer "401" maps to
     :class:`pyramid.httpexceptions.HTTPUnauthorized`).

  .. autofunction:: exception_response

  .. autoclass:: HTTPException

  .. autoclass:: HTTPOk

  .. autoclass:: HTTPRedirection

  .. autoclass:: HTTPError

  .. autoclass:: HTTPClientError

  .. autoclass:: HTTPServerError

  .. autoclass:: HTTPCreated

  .. autoclass:: HTTPAccepted

  .. autoclass:: HTTPNonAuthoritativeInformation

  .. autoclass:: HTTPNoContent

  .. autoclass:: HTTPResetContent

  .. autoclass:: HTTPPartialContent

  .. autoclass:: HTTPMultipleChoices

  .. autoclass:: HTTPMovedPermanently

  .. autoclass:: HTTPFound

  .. autoclass:: HTTPSeeOther

  .. autoclass:: HTTPNotModified

  .. autoclass:: HTTPUseProxy

  .. autoclass:: HTTPTemporaryRedirect

  .. autoclass:: HTTPBadRequest

  .. autoclass:: HTTPUnauthorized

  .. autoclass:: HTTPPaymentRequired

  .. autoclass:: HTTPForbidden

  .. autoclass:: HTTPNotFound

  .. autoclass:: HTTPMethodNotAllowed

  .. autoclass:: HTTPNotAcceptable

  .. autoclass:: HTTPProxyAuthenticationRequired

  .. autoclass:: HTTPRequestTimeout

  .. autoclass:: HTTPConflict

  .. autoclass:: HTTPGone

  .. autoclass:: HTTPLengthRequired

  .. autoclass:: HTTPPreconditionFailed

  .. autoclass:: HTTPRequestEntityTooLarge

  .. autoclass:: HTTPRequestURITooLong

  .. autoclass:: HTTPUnsupportedMediaType

  .. autoclass:: HTTPRequestRangeNotSatisfiable

  .. autoclass:: HTTPExpectationFailed

  .. autoclass:: HTTPUnprocessableEntity

  .. autoclass:: HTTPLocked

  .. autoclass:: HTTPFailedDependency

  .. autoclass:: HTTPInternalServerError

  .. autoclass:: HTTPNotImplemented

  .. autoclass:: HTTPBadGateway

  .. autoclass:: HTTPServiceUnavailable

  .. autoclass:: HTTPGatewayTimeout

  .. autoclass:: HTTPVersionNotSupported

  .. autoclass:: HTTPInsufficientStorage
