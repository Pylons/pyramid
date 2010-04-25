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

class ConfigurationError(ZCE):
    """ Raised when inappropriate input values are supplied to an API
    method of a :term:`Configurator`"""
