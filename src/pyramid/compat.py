import inspect
import platform
import sys
import types

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


# see PEP 3333 for why we encode WSGI PATH_INFO to latin-1 before
# decoding it to utf-8
def decode_path_info(path):
    return path.encode('latin-1').decode('utf-8')


# see PEP 3333 for why we decode the path to latin-1
from urllib.parse import unquote_to_bytes


def unquote_bytes_to_wsgi(bytestring):
    return unquote_to_bytes(bytestring).decode('latin-1')
