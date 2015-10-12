import inspect
import platform
import sys
import types

if platform.system() == 'Windows':  # pragma: no cover
    WIN = True
else:  # pragma: no cover
    WIN = False

try:  # pragma: no cover
    import __pypy__
    PYPY = True
except:  # pragma: no cover
    __pypy__ = None
    PYPY = False

try:
    import cPickle as pickle
except ImportError:  # pragma: no cover
    import pickle

# True if we are running on Python 3.
PY3 = sys.version_info[0] == 3
PY35 = (
    sys.version_info[0] == 3
    and sys.version_info[1] == 5
    and sys.version_info[2] == 0
)

if PY3:
    string_types = str,
    integer_types = int,
    class_types = type,
    text_type = str
    binary_type = bytes
    long = int
else:
    string_types = basestring,
    integer_types = (int, long)
    class_types = (type, types.ClassType)
    text_type = unicode
    binary_type = str
    long = long

if PY35:
    from traceback import StackSummary, walk_stack
    # backport fix of extract_stack from python 3.5.1
    def extract_stack(f=None, limit=None):
        """Extract the raw traceback from the current stack frame.

        The return value has the same format as for extract_tb().  The
        optional 'f' and 'limit' arguments have the same meaning as for
        print_stack().  Each item in the list is a quadruple (filename,
        line number, function name, text), and the entries are in order
        from oldest to newest stack frame.
        """
        if f is None:
            f = sys._getframe().f_back
        stack = StackSummary.extract(walk_stack(f), limit=limit)
        stack.reverse()
        return stack
else:
    from traceback import extract_stack

def text_(s, encoding='latin-1', errors='strict'):
    """ If ``s`` is an instance of ``binary_type``, return
    ``s.decode(encoding, errors)``, otherwise return ``s``"""
    if isinstance(s, binary_type):
        return s.decode(encoding, errors)
    return s

def bytes_(s, encoding='latin-1', errors='strict'):
    """ If ``s`` is an instance of ``text_type``, return
    ``s.encode(encoding, errors)``, otherwise return ``s``"""
    if isinstance(s, text_type):
        return s.encode(encoding, errors)
    return s

if PY3:
    def ascii_native_(s):
        if isinstance(s, text_type):
            s = s.encode('ascii')
        return str(s, 'ascii', 'strict')
else:
    def ascii_native_(s):
        if isinstance(s, text_type):
            s = s.encode('ascii')
        return str(s)

ascii_native_.__doc__ = """
Python 3: If ``s`` is an instance of ``text_type``, return
``s.encode('ascii')``, otherwise return ``str(s, 'ascii', 'strict')``

Python 2: If ``s`` is an instance of ``text_type``, return
``s.encode('ascii')``, otherwise return ``str(s)``
"""


if PY3:
    def native_(s, encoding='latin-1', errors='strict'):
        """ If ``s`` is an instance of ``text_type``, return
        ``s``, otherwise return ``str(s, encoding, errors)``"""
        if isinstance(s, text_type):
            return s
        return str(s, encoding, errors)
else:
    def native_(s, encoding='latin-1', errors='strict'):
        """ If ``s`` is an instance of ``text_type``, return
        ``s.encode(encoding, errors)``, otherwise return ``str(s)``"""
        if isinstance(s, text_type):
            return s.encode(encoding, errors)
        return str(s)

native_.__doc__ = """
Python 3: If ``s`` is an instance of ``text_type``, return ``s``, otherwise
return ``str(s, encoding, errors)``

Python 2: If ``s`` is an instance of ``text_type``, return
``s.encode(encoding, errors)``, otherwise return ``str(s)``
"""

if PY3:
    from urllib import parse
    urlparse = parse
    from urllib.parse import quote as url_quote
    from urllib.parse import quote_plus as url_quote_plus
    from urllib.parse import unquote as url_unquote
    from urllib.parse import urlencode as url_encode
    from urllib.request import urlopen as url_open
    url_unquote_text = url_unquote
    url_unquote_native = url_unquote
else:
    import urlparse
    from urllib import quote as url_quote
    from urllib import quote_plus as url_quote_plus
    from urllib import unquote as url_unquote
    from urllib import urlencode as url_encode
    from urllib2 import urlopen as url_open

    def url_unquote_text(v, encoding='utf-8', errors='replace'): # pragma: no cover
        v = url_unquote(v)
        return v.decode(encoding, errors)

    def url_unquote_native(v, encoding='utf-8', errors='replace'): # pragma: no cover
        return native_(url_unquote_text(v, encoding, errors))


if PY3:  # pragma: no cover
    import builtins
    exec_ = getattr(builtins, "exec")

    def reraise(tp, value, tb=None):
        if value is None:
            value = tp
        if value.__traceback__ is not tb:
            raise value.with_traceback(tb)
        raise value

    del builtins

else:  # pragma: no cover
    def exec_(code, globs=None, locs=None):
        """Execute code in a namespace."""
        if globs is None:
            frame = sys._getframe(1)
            globs = frame.f_globals
            if locs is None:
                locs = frame.f_locals
            del frame
        elif locs is None:
            locs = globs
        exec("""exec code in globs, locs""")

    exec_("""def reraise(tp, value, tb=None):
    raise tp, value, tb
""")


if PY3:  # pragma: no cover
    def iteritems_(d):
        return d.items()

    def itervalues_(d):
        return d.values()

    def iterkeys_(d):
        return d.keys()
else:  # pragma: no cover
    def iteritems_(d):
        return d.iteritems()

    def itervalues_(d):
        return d.itervalues()

    def iterkeys_(d):
        return d.iterkeys()


if PY3:
    def map_(*arg):
        return list(map(*arg))
else:
    map_ = map

if PY3:
    def is_nonstr_iter(v):
        if isinstance(v, str):
            return False
        return hasattr(v, '__iter__')
else:
    def is_nonstr_iter(v):
        return hasattr(v, '__iter__')

if PY3:
    im_func = '__func__'
    im_self = '__self__'
else:
    im_func = 'im_func'
    im_self = 'im_self'

try:
    import configparser
except ImportError:
    import ConfigParser as configparser

try:
    from http.cookies import SimpleCookie
except ImportError:
    from Cookie import SimpleCookie

if PY3:
    from html import escape
else:
    from cgi import escape

if PY3:
    input_ = input
else:
    input_ = raw_input

if PY3:
    from inspect import getfullargspec as getargspec
else:
    from inspect import getargspec

if PY3:
    from io import StringIO as NativeIO
else:
    from io import BytesIO as NativeIO

# "json" is not an API; it's here to support older pyramid_debugtoolbar
# versions which attempt to import it
import json

if PY3:
    # see PEP 3333 for why we encode WSGI PATH_INFO to latin-1 before
    # decoding it to utf-8
    def decode_path_info(path):
        return path.encode('latin-1').decode('utf-8')
else:
    def decode_path_info(path):
        return path.decode('utf-8')

if PY3:
    # see PEP 3333 for why we decode the path to latin-1 
    from urllib.parse import unquote_to_bytes

    def unquote_bytes_to_wsgi(bytestring):
        return unquote_to_bytes(bytestring).decode('latin-1')
else:
    from urlparse import unquote as unquote_to_bytes

    def unquote_bytes_to_wsgi(bytestring):
        return unquote_to_bytes(bytestring)


def is_bound_method(ob):
    return inspect.ismethod(ob) and getattr(ob, im_self, None) is not None

# support annotations and keyword-only arguments in PY3
if PY3: # pragma: no cover
    from inspect import getfullargspec as getargspec
else:
    from inspect import getargspec

if PY3: # pragma: no cover
    from itertools import zip_longest
else:
    from itertools import izip_longest as zip_longest

def is_unbound_method(fn):
    """
    This consistently verifies that the callable is bound to a
    class.
    """
    is_bound = is_bound_method(fn)

    if not is_bound and inspect.isroutine(fn):
        spec = getargspec(fn)
        has_self = len(spec.args) > 0 and spec.args[0] == 'self'

        if PY3 and inspect.isfunction(fn) and has_self:  # pragma: no cover
            return True
        elif inspect.ismethod(fn):
            return True

    return False
