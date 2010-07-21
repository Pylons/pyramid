from zope.configuration.exceptions import ConfigurationError as ZCE

class Forbidden(Exception):
    """\
    Raise this exception within :term:`view` code to immediately
    return the :term:`forbidden view` to the invoking user.  Usually
    this is a basic ``401`` page, but the forbidden view can be
    customized as necessary.  See :ref:`changing_the_forbidden_view`.

    This exception's constructor accepts a single positional argument,
    which should be a string.  The value of this string will be placed
    into the WSGI environment by the router under the
    ``repoze.bfg.message`` key, for availability to the
    :term:`Forbidden View`."""

class NotFound(Exception):
    """\
    Raise this exception within :term:`view` code to immediately
    return the :term:`Not Found view` to the invoking user.  Usually
    this is a basic ``404`` page, but the Not Found view can be
    customized as necessary.  See :ref:`changing_the_notfound_view`.

    This exception's constructor accepts a single positional argument,
    which should be a string.  The value of this string will be placed
    into the WSGI environment by the router under the
    ``repoze.bfg.message`` key, for availability to the :term:`Not Found
    View`."""

class URLDecodeError(UnicodeDecodeError):
    """
    This exception is raised when :mod:`repoze.bfg` cannot
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

class PredicateMismatch(NotFound):
    """ Internal exception (not an API) raised by multiviews when no
    view matches.  This exception subclasses the ``NotFound``
    exception only one reason: if it reaches the main exception
    handler, it should be treated like a ``NotFound`` by any exception
    view registrations."""

