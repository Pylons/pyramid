import platform

WIN = platform.system() == 'Windows'

try:  # pragma: no cover
    import __pypy__

    PYPY = True
except BaseException:  # pragma: no cover
    __pypy__ = None
    PYPY = False


def text_(s, encoding='latin-1', errors='strict'):
    """ If ``s`` is an instance of ``bytes``, return
    ``s.decode(encoding, errors)``, otherwise return ``s``"""
    if isinstance(s, bytes):
        return s.decode(encoding, errors)
    return s


def bytes_(s, encoding='latin-1', errors='strict'):
    """ If ``s`` is an instance of ``str``, return
    ``s.encode(encoding, errors)``, otherwise return ``s``"""
    if isinstance(s, str):
        return s.encode(encoding, errors)
    return s


def ascii_native_(s):
    """
    If ``s`` is an instance of ``str``, return
    ``s.encode('ascii')``, otherwise return ``str(s, 'ascii', 'strict')``
    """
    if isinstance(s, str):
        s = s.encode('ascii')
    return str(s, 'ascii', 'strict')


def native_(s, encoding='latin-1', errors='strict'):
    """ If ``s`` is an instance of ``str``, return
    ``s``, otherwise return ``str(s, encoding, errors)``
    """
    if isinstance(s, str):
        return s
    return str(s, encoding, errors)
