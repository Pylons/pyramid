class Forbidden(Exception):
    """\
    Raise this exception within :term:`view` code to immediately
    return the Forbidden view to the invoking user.  Usually this is a
    basic ``401`` page, but the Forbidden view can be customized as
    necessary.  See :ref:`changing_the_forbidden_view`.

    This exception's constructor accepts a single positional argument,
    which should be a string.  The value of this string will be placed
    into the WSGI environment under the ``repoze.bfg.message`` key,
    for availability to the Forbidden view."""

class NotFound(Exception):
    """\
    Raise this exception within :term:`view` code to immediately
    return the Not Found view to the invoking user.  Usually this is a
    basic ``404`` page, but the Not Found view can be customized as
    necessary.  See :ref:`changing_the_notfound_view`.

    This exception's constructor accepts a single positional argument,
    which should be a string.  The value of this string will be placed
    into the WSGI environment under the ``repoze.bfg.message`` key,
    for availability to the Not Found view."""

class Respond(Exception):
    """\
    Raise this exception during view execution to return a response
    immediately without proceeeding any further through the codepath.
    Use of this exception is effectively a 'goto': its target is the
    exception handler within the :mod:`repoze.bfg' router that catches
    the exception and returns a response immediately.  Note that
    because this exception is caught by the router, it will not
    propagate to any WSGI middleware.  Note that this exception is
    typically only used by the framework itself and by authentication
    plugins to the framework.

    The exception must be initialized which a single argument, which
    is a :term:`response` object.

    An example:

    .. code-block:: python
       :linenos:

       from webob.exc import HTTPFound
       from repoze.bfg.exceptions import Respond
       response = HTTPFound(location='http://example.com')
       raise Respond(response)
    """
    
