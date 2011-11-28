from pyramid.compat import (
    text_type,
    binary_type,
    is_nonstr_iter,
    url_quote as _url_quote,
    url_quote_plus as quote_plus, # bw compat api (dnr)
    )

def url_quote(s, safe=''): # bw compat api
    return _url_quote(s, safe=safe)

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
        k = _enc(k)

        if is_nonstr_iter(v):
            for x in v:
                x = _enc(x)
                result += '%s%s=%s' % (prefix, k, x)
                prefix = '&'
        else:
            v = _enc(v)
            result += '%s%s=%s' % (prefix, k, v)

        prefix = '&'

    return result

def _enc(val):
    cls = val.__class__
    if cls is text_type:
        val = val.encode('utf-8')
    elif cls is not binary_type:
        val = str(val).encode('utf-8')
    return quote_plus(val)

