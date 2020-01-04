from urllib.parse import quote as _url_quote, quote_plus as _quote_plus

from pyramid.util import is_nonstr_iter


def url_quote(val, safe=''):  # bw compat api
    cls = val.__class__
    if cls is str:
        val = val.encode('utf-8')
    elif cls is not bytes:
        val = str(val).encode('utf-8')
    return _url_quote(val, safe=safe)


# bw compat api (dnr)
def quote_plus(val, safe=''):
    cls = val.__class__
    if cls is str:
        val = val.encode('utf-8')
    elif cls is not bytes:
        val = str(val).encode('utf-8')
    return _quote_plus(val, safe=safe)


def urlencode(query, doseq=True, quote_via=quote_plus):
    """
    An alternate implementation of Python's stdlib
    :func:`urllib.parse.urlencode` function which accepts string keys and
    values within the ``query`` dict/sequence; all string keys and values are
    first converted to UTF-8 before being used to compose the query string.

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

    Both the key and value are encoded using the ``quote_via`` function which
    by default is using a similar algorithm to :func:`urllib.parse.quote_plus`
    which converts spaces into '+' characters and '/' into '%2F'.

    .. versionchanged:: 1.5
       In a key/value pair, if the value is ``None`` then it will be
       dropped from the resulting output.

    .. versionchanged:: 1.9
       Added the ``quote_via`` argument to allow alternate quoting algorithms
       to be used.

    """
    try:
        # presumed to be a dictionary
        query = query.items()
    except AttributeError:
        pass

    result = ''
    prefix = ''

    for (k, v) in query:
        k = quote_via(k)

        if is_nonstr_iter(v):
            for x in v:
                x = quote_via(x)
                result += '%s%s=%s' % (prefix, k, x)
                prefix = '&'
        elif v is None:
            result += '%s%s=' % (prefix, k)
        else:
            v = quote_via(v)
            result += '%s%s=%s' % (prefix, k, v)

        prefix = '&'

    return result
