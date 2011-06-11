from zope.configuration.exceptions import ConfigurationError as ZCE

from pyramid.httpexceptions import HTTPNotFound
from pyramid.httpexceptions import HTTPForbidden

NotFound = HTTPNotFound # bw compat
Forbidden = HTTPForbidden # bw compat

class PredicateMismatch(HTTPNotFound):
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


