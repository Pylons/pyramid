""" Utility functions for dealing with URLs in repoze.bfg """

import re
import urllib

from zope.component import queryMultiAdapter
from repoze.bfg.interfaces import IContextURL

def model_url(model, request, *elements, **kw):
    """
    Generate a string representing the absolute URL of the model (or
    context) object based on the ``wsgi.url_scheme``, ``HTTP_HOST`` or
    ``SERVER_NAME`` in the request, plus any ``SCRIPT_NAME``.  If a
    'virtual root path' is present in the request environment (the
    value of the WSGI environ key ``HTTP_X_VHM_ROOT``), and the
    ``model`` was obtained via traversal, the URL path will not
    include the virtual root prefix (it will be stripped out of the
    generated URL).  If a ``query`` keyword argument is provided, a
    query string based on its value will be composed and appended to
    the generated URL string (see details below).  The overall result
    of this function is always a UTF-8 encoded string (never unicode).

    .. note:: If the ``model`` used is the result of a traversal, it
       must be :term:`location`-aware.  The 'model' can also be the
       context of a URL dispatch; contexts found this way do not need
       to be location-aware.

    Any positional arguments passed in as ``elements`` must be strings
    or unicode objects.  These will be joined by slashes and appended
    to the generated model URL.  Each of the elements passed in is
    URL-quoted before being appended; if any element is unicode, it
    will converted to a UTF-8 bytestring before being URL-quoted.

    .. warning:: if no ``elements`` arguments are specified, the model
                 URL will end with a trailing slash.  If any
                 ``elements`` are used, the generated URL will *not*
                 end in trailing a slash.

    If a keyword argument ``query`` is present, it will used to
    compose a query string that will be tacked on to the end of the
    URL.  The value of ``query`` must be a sequence of two-tuples *or*
    a data structure with an ``.items()`` method that returns a
    sequence of two-tuples (presumably a dictionary).  This data
    structure will be turned into a query string per the documentation
    of ``repoze.url.urlencode`` function.  After the query data is
    turned into a query string, a leading ``?`` is prepended, and the
    the resulting string is appended to the generated URL.

    .. note:: Python data structures that are passed as ``query``
              which are sequences or dictionaries are turned into a
              string under the same rules as when run through
              urllib.urlencode with the ``doseq`` argument equal to
              ``True``.  This means that sequences can be passed as
              values, and a k=v pair will be placed into the query
              string for each value.
    """
    
    context_url = queryMultiAdapter((model, request), IContextURL)
    if context_url is None:
        # b/w compat for unit tests
        from repoze.bfg.traversal import TraversalContextURL
        context_url = TraversalContextURL(model, request)
    model_url = context_url()

    if 'query' in kw:
        qs = '?' + urlencode(kw['query'], doseq=True)
    else:
        qs = ''

    if elements:
        suffix = '/'.join([_urlsegment(s) for s in elements])
    else:
        suffix = ''

    return model_url + suffix + qs

def urlencode(query, doseq=False):
    """
    A wrapper around Python's stdlib `urllib.urlencode function
    <http://docs.python.org/library/urllib.html>`_ which accepts
    unicode keys and values within the ``query`` dict/sequence; all
    Unicode keys and values are first converted to UTF-8 before being
    used to compose the query string.  The behavior of the function is
    otherwise the same as the stdlib version.

    The value of ``query`` must be a sequence of two-tuples
    representing key/value pairs *or* an object (often a dictionary)
    with an ``.items()`` method that returns a sequence of two-tuples
    representing key/value pairs.  ``doseq`` controls what happens
    when a sequence is presented as one of the values.  See the Python
    stdlib documentation for more information.
    """
    if hasattr(query, 'items'):
        # dictionary
        query = query.items()
    # presumed to be a sequence of two-tuples
    newquery = []
    for k, v in query:
        if k.__class__ is unicode:
            k = k.encode('utf-8')

        if isinstance(v, (tuple, list)):
            L = []
            for x in v:
                if x.__class__ is unicode:
                    x = x.encode('utf-8')
                L.append(x)
            v = L
        elif v.__class__ is unicode:
            v = v.encode('utf-8')
        newquery.append((k, v))

    return urllib.urlencode(newquery, doseq=doseq)

_segment_cache = {}

def _urlsegment(s):
    """ The bit of this code that deals with ``_segment_cache`` is an
    optimization: we cache all the computation of URL path segments in
    this module-scope dictionary with the original string (or unicode
    value) as the key, so we can look it up later without needing to
    reencode or re-url-quote it """
    result = _segment_cache.get(s)
    if result is None:
        if s.__class__ is unicode: # isinstance slighly slower (~15%)
            result = _url_quote(s.encode('utf-8'))
        else:
            result = _url_quote(s)
        # we don't need a lock to mutate _segment_cache, as the below
        # will generate exactly one Python bytecode (STORE_SUBSCR)
        _segment_cache[s] = result
    return result


always_safe = ('ABCDEFGHIJKLMNOPQRSTUVWXYZ'
               'abcdefghijklmnopqrstuvwxyz'
               '0123456789' '_.-')
_safemaps = {}
_must_quote = {}

def _url_quote(s, safe = '/'):
    """quote('abc def') -> 'abc%20def'

    Faster version of Python stdlib urllib.quote.  See
    http://bugs.python.org/issue1285086 for more information.

    Each part of a URL, e.g. the path info, the query, etc., has a
    different set of reserved characters that must be quoted.

    RFC 2396 Uniform Resource Identifiers (URI): Generic Syntax lists
    the following reserved characters.

    reserved    = ";" | "/" | "?" | ":" | "@" | "&" | "=" | "+" |
                  "$" | ","

    Each of these characters is reserved in some component of a URL,
    but not necessarily in all of them.

    By default, the quote function is intended for quoting the path
    section of a URL.  Thus, it will not encode '/'.  This character
    is reserved, but in typical usage the quote function is being
    called on a path where the existing slash characters are used as
    reserved characters.
    """
    cachekey = (safe, always_safe)
    try:
        safe_map = _safemaps[cachekey]
        if not _must_quote[cachekey].search(s):
            return s
    except KeyError:
        safe += always_safe
        _must_quote[cachekey] = re.compile(r'[^%s]' % safe)
        safe_map = {}
        for i in range(256):
            c = chr(i)
            safe_map[c] = (c in safe) and c or ('%%%02X' % i)
        _safemaps[cachekey] = safe_map
    res = map(safe_map.__getitem__, s)
    return ''.join(res)

