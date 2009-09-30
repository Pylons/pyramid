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

