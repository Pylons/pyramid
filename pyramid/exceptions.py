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

class ConfigurationError(Exception):
    """ Raised when inappropriate input values are supplied to an API
    method of a :term:`Configurator`"""

class ConfigurationConflictError(ConfigurationError):
    """ Raised when a configuration conflict is detected during action
    processing"""

    def __init__(self, conflicts):
        self._conflicts = conflicts

    def __str__(self):
        r = ["Conflicting configuration actions"]
        items = self._conflicts.items()
        items.sort()
        for discriminator, infos in items:
            r.append("  For: %s" % (discriminator, ))
            for info in infos:
                for line in unicode(info).rstrip().split(u'\n'):
                    r.append(u"    "+line)

        return "\n".join(r)


class ConfigurationExecutionError(ConfigurationError):
    """An error occurred during execution of a configuration action
    """

    def __init__(self, etype, evalue, info):
        self.etype, self.evalue, self.info = etype, evalue, info

    def __str__(self):
        return "%s: %s\n  in:\n  %s" % (self.etype, self.evalue, self.info)
