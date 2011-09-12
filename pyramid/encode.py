import re

always_safe = ('ABCDEFGHIJKLMNOPQRSTUVWXYZ'
               'abcdefghijklmnopqrstuvwxyz'
               '0123456789' '_.-')
_safemaps = {}
_must_quote = {}

def url_quote(s, safe=''):
    """quote('abc def') -> 'abc%20def'

    Each part of a URL, e.g. the path info, the query, etc., has a
    different set of reserved characters that must be quoted.

    RFC 2396 Uniform Resource Identifiers (URI): Generic Syntax lists
    the following reserved characters::

     reserved    = ";" | "/" | "?" | ":" | "@" | "&" | "=" | "+" |
                   "$" | ","

    Each of these characters is reserved in some component of a URL,
    but not necessarily in all of them.

    Unlike the default version of this function in the Python stdlib, by
    default, the url_quote function is intended for quoting individual path
    segments instead of an already composed path that might have ``/``
    characters in it.  Thus, it *will* encode any ``/`` character it finds in a
    string unless ``/`` is marked as 'safe'.  It is also slightly faster than
    the stdlib version.
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
            if c in safe:
                safe_map[c] = c
            else:
                safe_map[c] = '%%%02X' % i
        _safemaps[cachekey] = safe_map
    res = map(safe_map.__getitem__, s)
    return ''.join(res)

def quote_plus(s, safe=''):
    """ Version of stdlib quote_plus which uses faster url_quote """
    if ' ' in s:
        s = url_quote(s, safe + ' ')
        return s.replace(' ', '+')
    return url_quote(s, safe)

def urlencode(query, doseq=True):
    """
    An alternate implementation of Python's stdlib `urllib.urlencode
    function <http://docs.python.org/library/urllib.html>`_ which
    accepts unicode keys and values within the ``query``
    dict/sequence; all Unicode keys and values are first converted to
    UTF-8 before being used to compose the query string.

    The value of ``query`` must be a sequence of two-tuples
    representing key/value pairs *or* an object (often a dictionary)
    with an ``.items()`` method that returns a sequence of two-tuples
    representing key/value pairs.

    For minimal calling convention backwards compatibility, this
    version of urlencode accepts *but ignores* a second argument
    conventionally named ``doseq``.  The Python stdlib version behaves
    differently when ``doseq`` is False and when a sequence is
    presented as one of the values.  This version always behaves in
    the ``doseq=True`` mode, no matter what the value of the second
    argument.

    See the Python stdlib documentation for ``urllib.urlencode`` for
    more information.
    """
    try:
        # presumed to be a dictionary
        query = query.items()
    except AttributeError:
        pass

    result = ''
    prefix = ''

    for (k, v) in query:
        if k.__class__ is unicode:
            k = k.encode('utf-8')
        k = quote_plus(str(k))
        if hasattr(v, '__iter__'):
            for x in v:
                if x.__class__ is unicode:
                    x = x.encode('utf-8')
                x = quote_plus(str(x))
                result += '%s%s=%s' % (prefix, k, x)
                prefix = '&'
        else:
            if v.__class__ is unicode:
                v = v.encode('utf-8')
            v = quote_plus(str(v))
            result += '%s%s=%s' % (prefix, k, v)
        prefix = '&'

    return result
