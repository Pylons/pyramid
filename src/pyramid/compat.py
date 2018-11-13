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


from urllib import parse

urlparse = parse
from urllib.parse import quote as url_quote
from urllib.parse import quote_plus as url_quote_plus
from urllib.parse import unquote as url_unquote
from urllib.parse import urlencode as url_encode
from urllib.request import urlopen as url_open

url_unquote_text = url_unquote
url_unquote_native = url_unquote


import builtins

exec_ = getattr(builtins, "exec")


def reraise(tp, value, tb=None):
    if value is None:
        value = tp
    if value.__traceback__ is not tb:
        raise value.with_traceback(tb)
    raise value


del builtins


def iteritems_(d):
    return d.items()


def itervalues_(d):
    return d.values()


def iterkeys_(d):
    return d.keys()


def map_(*arg):
    return list(map(*arg))


def is_nonstr_iter(v):
    if isinstance(v, str):
        return False
    return hasattr(v, '__iter__')


im_func = '__func__'
im_self = '__self__'

import configparser

from http.cookies import SimpleCookie

from html import escape

input_ = input

from io import StringIO as NativeIO

# "json" is not an API; it's here to support older pyramid_debugtoolbar
# versions which attempt to import it
import json

# see PEP 3333 for why we encode WSGI PATH_INFO to latin-1 before
# decoding it to utf-8
def decode_path_info(path):
    return path.encode('latin-1').decode('utf-8')


# see PEP 3333 for why we decode the path to latin-1
from urllib.parse import unquote_to_bytes


def unquote_bytes_to_wsgi(bytestring):
    return unquote_to_bytes(bytestring).decode('latin-1')


def is_bound_method(ob):
    return inspect.ismethod(ob) and getattr(ob, im_self, None) is not None


# support annotations and keyword-only arguments in PY3
from inspect import getfullargspec as getargspec

from itertools import zip_longest


def is_unbound_method(fn):
    """
    This consistently verifies that the callable is bound to a
    class.
    """
    is_bound = is_bound_method(fn)

    if not is_bound and inspect.isroutine(fn):
        spec = getargspec(fn)
        has_self = len(spec.args) > 0 and spec.args[0] == 'self'

        if inspect.isfunction(fn) and has_self:
            return True

    return False
