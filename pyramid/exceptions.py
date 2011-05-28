from zope.configuration.exceptions import ConfigurationError as ZCE
from zope.interface import classImplements
from pyramid.interfaces import IExceptionResponse
from webob.response import Response

# Documentation proxy import
from webob.exc import __doc__

# API: status_map
from webob.exc import status_map
status_map = status_map.copy() # we mutate it

# API: parent classes
from webob.exc import HTTPException
from webob.exc import WSGIHTTPException
from webob.exc import HTTPOk
from webob.exc import HTTPRedirection
from webob.exc import HTTPError
from webob.exc import HTTPClientError
from webob.exc import HTTPServerError

# slightly nasty import-time side effect to provide WSGIHTTPException
# with IExceptionResponse interface (used during config.py exception view
# registration)
classImplements(WSGIHTTPException, IExceptionResponse)

# API: Child classes
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

# API: HTTPNotFound and HTTPForbidden (redefined for bw compat)

from webob.exc import HTTPForbidden as _HTTPForbidden
from webob.exc import HTTPNotFound as _HTTPNotFound

class HTTPNotFound(_HTTPNotFound):
    """
    Raise this exception within :term:`view` code to immediately
    return the :term:`Not Found view` to the invoking user.  Usually
    this is a basic ``404`` page, but the Not Found view can be
    customized as necessary.  See :ref:`changing_the_notfound_view`.

    This exception's constructor accepts a single positional argument, which
    should be a string.  The value of this string will be available as the
    ``message`` attribute of this exception, for availability to the
    :term:`Not Found View`.
    """
    def __init__(self, detail=None, headers=None, comment=None,
                 body_template=None, **kw):
        self.message = detail # prevent 2.6.X whining
        _HTTPNotFound.__init__(self, detail=detail, headers=headers,
                               comment=comment, body_template=body_template,
                               **kw)
        if not ('body' in kw or 'app_iter' in kw):
            if not self.empty_body:
                body = self.html_body(self.environ)
                if isinstance(body, unicode):
                    body = body.encode(self.charset)
                self.body = body

class HTTPForbidden(_HTTPForbidden):
    """
    Raise this exception within :term:`view` code to immediately return the
    :term:`forbidden view` to the invoking user.  Usually this is a basic
    ``403`` page, but the forbidden view can be customized as necessary.  See
    :ref:`changing_the_forbidden_view`.  A ``Forbidden`` exception will be
    the ``context`` of a :term:`Forbidden View`.

    This exception's constructor accepts two arguments.  The first argument,
    ``message``, should be a string.  The value of this string will be used
    as the ``message`` attribute of the exception object.  The second
    argument, ``result`` is usually an instance of
    :class:`pyramid.security.Denied` or :class:`pyramid.security.ACLDenied`
    each of which indicates a reason for the forbidden error.  However,
    ``result`` is also permitted to be just a plain boolean ``False`` object.
    The ``result`` value will be used as the ``result`` attribute of the
    exception object.

    The :term:`Forbidden View` can use the attributes of a Forbidden
    exception as necessary to provide extended information in an error
    report shown to a user.
    """
    def __init__(self, detail=None, headers=None, comment=None,
                 body_template=None, result=None, **kw):
        self.message = detail # prevent 2.6.X whining
        self.result = result # bw compat
        _HTTPForbidden.__init__(self, detail=detail, headers=headers,
                                comment=comment, body_template=body_template,
                                **kw)
        if not ('body' in kw or 'app_iter' in kw):
            if not self.empty_body:
                body = self.html_body(self.environ)
                if isinstance(body, unicode):
                    body = body.encode(self.charset)
                self.body = body

NotFound = HTTPNotFound # bw compat
Forbidden = HTTPForbidden # bw compat

# patch our status map with subclasses
status_map[403] = HTTPForbidden
status_map[404] = HTTPNotFound

class PredicateMismatch(NotFound):
    """
    Internal exception (not an API) raised by multiviews when no
    view matches.  This exception subclasses the ``NotFound``
    exception only one reason: if it reaches the main exception
    handler, it should be treated like a ``NotFound`` by any exception
    view registrations.
    """

class URLDecodeError(UnicodeDecodeError):
    """
    This exception is raised when :app:`Pyramid` cannot
    successfully decode a URL or a URL path segment.  This exception
    it behaves just like the Python builtin
    :exc:`UnicodeDecodeError`. It is a subclass of the builtin
    :exc:`UnicodeDecodeError` exception only for identity purposes,
    mostly so an exception view can be registered when a URL cannot be
    decoded.
    """

class ConfigurationError(ZCE):
    """ Raised when inappropriate input values are supplied to an API
    method of a :term:`Configurator`"""


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

def is_response(ob):
    """ Return ``True`` if ``ob`` implements the interface implied by
    :ref:`the_response`. ``False`` if not.

    .. note:: This isn't a true interface or subclass check.  Instead, it's a
        duck-typing check, as response objects are not obligated to be of a
        particular class or provide any particular Zope interface."""

    # response objects aren't obligated to implement a Zope interface,
    # so we do it the hard way
    if ( hasattr(ob, 'app_iter') and hasattr(ob, 'headerlist') and
         hasattr(ob, 'status') ):
        return True
    return False

newstyle_exceptions = issubclass(Exception, object)

if newstyle_exceptions:
    # webob exceptions will be Response objects (Py 2.5+)
    def default_exceptionresponse_view(context, request):
        if not isinstance(context, Exception):
            # backwards compat for an exception response view registered via
            # config.set_notfound_view or config.set_forbidden_view
            # instead of as a proper exception view
            context = request.exception or context
        # WSGIHTTPException, a Response (2.5+)
        return context

else:
    # webob exceptions will not be Response objects (Py 2.4)
    def default_exceptionresponse_view(context, request):
        if not isinstance(context, Exception):
            # backwards compat for an exception response view registered via
            # config.set_notfound_view or config.set_forbidden_view
            # instead of as a proper exception view
            context = request.exception or context
        # HTTPException, not a Response (2.4)
        get_response = getattr(request, 'get_response', lambda c: c) # testing
        return get_response(context)
