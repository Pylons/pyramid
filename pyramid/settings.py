from zope.deprecation import deprecated

from pyramid.threadlocal import get_current_registry
from pyramid.compat import string_types

def get_settings():
    """
    Return a :term:`deployment settings` object for the current application.
    The object is a dictionary-like object that contains key/value pairs
    based on the dictionary passed as the ``settings`` argument to the
    :class:`pyramid.config.Configurator` constructor or the
    :func:`pyramid.router.make_app` API.

    .. warning:: This method is deprecated as of Pyramid 1.0.  Use
       ``pyramid.threadlocal.get_current_registry().settings`` instead or use
       the ``settings`` attribute of the registry available from the request
       (``request.registry.settings``).
    """
    reg = get_current_registry()
    return reg.settings

deprecated(
    'get_settings',
    '(pyramid.settings.get_settings is deprecated as of Pyramid 1.0.  Use'
    '``pyramid.threadlocal.get_current_registry().settings`` instead or use '
    'the ``settings`` attribute of the registry available from the request '
    '(``request.registry.settings``)).')

truthy = frozenset(('t', 'true', 'y', 'yes', 'on', '1'))

def asbool(s):
    """ Return the boolean value ``True`` if the case-lowered value of string
    input ``s`` is any of ``t``, ``true``, ``y``, ``on``, or ``1``, otherwise
    return the boolean value ``False``.  If ``s`` is the value ``None``,
    return ``False``.  If ``s`` is already one of the boolean values ``True``
    or ``False``, return it."""
    if s is None:
        return False
    if isinstance(s, bool):
        return s
    s = str(s).strip()
    return s.lower() in truthy

def aslist_cronly(value):
    if isinstance(value, string_types):
        value = filter(None, [x.strip() for x in value.splitlines()])
    return list(value)

def aslist(value, flatten=True):
    """ Return a list of strings, separating the input based on newlines
    and, if flatten=True (the default), also split on spaces within
    each line."""
    values = aslist_cronly(value)
    if not flatten:
        return values
    result = []
    for value in values:
        subvalues = value.split()
        result.extend(subvalues)
    return result
