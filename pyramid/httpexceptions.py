from webob.exc import __doc__
from webob.exc import status_map

# Parent classes
from webob.exc import HTTPException
from webob.exc import WSGIHTTPException
from webob.exc import HTTPOk
from webob.exc import HTTPRedirection
from webob.exc import HTTPError
from webob.exc import HTTPClientError
from webob.exc import HTTPServerError

# Child classes
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

from webob.response import Response

def abort(status_code, **kw):
    """Aborts the request immediately by raising an HTTP exception.  The
    values in ``*kw`` will be passed to the HTTP exception constructor.
    Example::

        abort(404) # raises an HTTPNotFound exception.
    """
    exc = status_map[status_code](**kw)
    raise exc.exception


def redirect(url, code=302, **kw):
    """Raises a redirect exception to the specified URL.

    Optionally, a code variable may be passed with the status code of
    the redirect, ie::

        redirect(route_url('foo', request), code=303)

    """
    exc = status_map[code]
    raise exc(location=url, **kw).exception

def default_httpexception_view(context, request):
    if isinstance(context, Response):
        # WSGIHTTPException, a Response (2.5+)
        return context
    # HTTPException, a WSGI app (2.4)
    return request.get_response(context)

