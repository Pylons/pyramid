truthy = frozenset(('t', 'true', 'y', 'yes', 'on', '1'))
falsey = frozenset(('f', 'false', 'n', 'no', 'off', '0'))


def asbool(s):
    """Return the boolean value ``True`` if the case-lowered value of string
    input ``s`` is a :term:`truthy string`. If ``s`` is already one of the
    boolean values ``True`` or ``False``, return it."""
    if s is None:
        return False
    if isinstance(s, bool):
        return s
    s = str(s).strip()
    return s.lower() in truthy


def aslist_cronly(value):
    if isinstance(value, str):
        value = filter(None, [x.strip() for x in value.splitlines()])
    return list(value)


def aslist(value, flatten=True):
    """Return a list, separating the input based on newlines.
    Also if ``flatten`` is ``True`` (the default), and if the line
    is a string, then the line will be split on spaces.
    """
    values = aslist_cronly(value)
    if not flatten:
        return values
    result = []
    for value in values:
        if isinstance(value, str):
            value = value.split()
            result.extend(value)
        else:
            result.append(value)
    return result
