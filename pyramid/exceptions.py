from zope.configuration.exceptions import ConfigurationError as ZCE
from zope.interface import implements

from pyramid.decorator import reify
from pyramid.interfaces import IExceptionResponse
import cgi

class ExceptionResponse(Exception):
    """ Abstract class to support behaving as a WSGI response object """
    implements(IExceptionResponse)
    status = None

    def __init__(self, message=''):
        Exception.__init__(self, message) # B / C
        self.message = message

    @reify # defer execution until asked explicitly
    def app_iter(self):
         return [
             """
             <html>
             <title>%s</title>
             <body>
             <h1>%s</h1>
             <code>%s</code>
             </body>
             </html>
             """ % (self.status, self.status, cgi.escape(self.message))
             ]

    @reify # defer execution until asked explicitly
    def headerlist(self):
        return [
            ('Content-Length', str(len(self.app_iter[0]))),
            ('Content-Type', 'text/html')
            ]
        
        
class Forbidden(ExceptionResponse):
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
    status = '403 Forbidden'
    def __init__(self, message='', result=None):
        ExceptionResponse.__init__(self, message)
        self.message = message
        self.result = result

class NotFound(ExceptionResponse):
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
    status = '404 Not Found'

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

