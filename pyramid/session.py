try:
    from hashlib import sha1
except ImportError: # pragma: no cover
    import sha as sha1

try:
    import cPickle as pickle
except ImportError: # pragma: no cover
    import pickle

from webob import Response

import hmac
import binascii
import time
import base64

def manage_accessed(wrapped):
    """ Decorator which causes a cookie to be set when a wrapped
    method is called"""
    def accessed(session, *arg, **kw):
        session.accessed = int(time.time())
        if not session._dirty:
            session._dirty = True
            def set_cookie_callback(request, response):
                session._set_cookie(response)
                session.request = None # explicitly break cycle for gc
            session.request.add_response_callback(set_cookie_callback)
        return wrapped(session, *arg, **kw)
    accessed.__doc__ = wrapped.__doc__
    return accessed

def InsecureCookieSessionFactoryConfig(
    secret,
    timeout=1200,
    cookie_name='session',
    cookie_max_age=None,
    cookie_path='/',
    cookie_domain=None,
    cookie_secure=False, 
    cookie_httponly=False,
    cookie_on_exception=False,
    ):
    """
    Configure a :term:`session factory` which will provide insecure
    (but signed) cookie-based sessions.  The return value of this
    function is a :term:`session factory`, which may be provided as
    the ``session_factory`` argument of a
    :class:`pyramid.configuration.Configurator` constructor, or used
    as the ``session_factory`` argument of the
    :meth:`pyramid.configuration.Configurator.set_session_factory`
    method.

    The session factory returned by this function will create sessions
    which are limited to storing fewer than 4000 bytes of data (as the
    payload must fit into a single cookie).

    Parameters:

    ``secret``
      A string which is used to sign the cookie.

    ``timeout``
      A number of seconds of inactivity before a session times out.

    ``cookie_name``
      The name of the cookie used for sessioning.  Default: ``session``.

    ``cookie_max_age``
      The maximum age of the cookie used for sessioning (in seconds).
      Default: ``None`` (browser scope).

    ``cookie_path``
      The path used for the session cookie.  Default: ``/``.

    ``cookie_domain``
      The domain used for the session cookie.  Default: ``None`` (no domain).

    ``cookie_secure``
      The 'secure' flag of the session cookie.  Default: ``False``.

    ``cookie_httponly``
      The 'httpOnly' flag of the session cookie.  Default: ``False``.

    ``cookie_on_exception``
      If ``True``, set a session cookie even if an exception occurs
      while rendering a view.  Default: ``False``.

    """

    class InsecureCookieSessionFactory(dict):
        """ Dictionary-like session object """

        # configuration parameters
        _cookie_name = cookie_name
        _cookie_max_age = cookie_max_age
        _cookie_path = cookie_path
        _cookie_domain = cookie_domain
        _cookie_secure = cookie_secure
        _cookie_httponly = cookie_httponly
        _cookie_on_exception = cookie_on_exception
        _secret = secret
        _timeout = timeout

        # dirty flag
        _dirty = False

        def __init__(self, request):
            self.request = request
            now = time.time()
            created = accessed = now
            new = True
            cookieval = request.cookies.get(self._cookie_name)
            value = deserialize(cookieval, self._secret)
            state = {}
            if value is not None:
                accessed, created, state = value
                new = False
                if now - accessed > self._timeout:
                    state = {}

            self.created = created
            self.accessed = accessed
            self.new = new
            dict.__init__(self, state)

        # ISession methods
        def changed(self):
            """ This is intentionally a noop; the session is
            serialized on every access, so unnecessary"""
            pass

        def invalidate(self):
            self.clear() # XXX probably needs to unset cookie

        # non-modifying dictionary methods
        get = manage_accessed(dict.get)
        __getitem__ = manage_accessed(dict.__getitem__)
        items = manage_accessed(dict.items)
        iteritems = manage_accessed(dict.iteritems)
        values = manage_accessed(dict.values)
        itervalues = manage_accessed(dict.itervalues)
        keys = manage_accessed(dict.keys)
        iterkeys = manage_accessed(dict.iterkeys)
        __contains__ = manage_accessed(dict.__contains__)
        has_key = manage_accessed(dict.has_key)
        __len__ = manage_accessed(dict.__len__)
        __iter__ = manage_accessed(dict.__iter__)

        # modifying dictionary methods
        clear = manage_accessed(dict.clear)
        update = manage_accessed(dict.update)
        setdefault = manage_accessed(dict.setdefault)
        pop = manage_accessed(dict.pop)
        popitem = manage_accessed(dict.popitem)
        __setitem__ = manage_accessed(dict.__setitem__)
        __delitem__ = manage_accessed(dict.__delitem__)

        # non-API methods
        def _set_cookie(self, response):
            if not self._cookie_on_exception:
                exception = getattr(self.request, 'exception', None)
                if exception is not None: # dont set a cookie during exceptions
                    return False
            cookieval = serialize(
                (self.accessed, self.created, dict(self)), self._secret
                )
            if len(cookieval) > 4064:
                raise ValueError(
                    'Cookie value is too long to store (%s bytes)' %
                    len(cookieval)
                    )
            if hasattr(response, 'set_cookie'):
                # ``response`` is a "real" webob response
                set_cookie = response.set_cookie
            else:
                # ``response`` is not a "real" webob response, cope
                def set_cookie(*arg, **kw):
                    tmp_response = Response()
                    tmp_response.set_cookie(*arg, **kw)
                    response.headerlist.append(
                        tmp_response.headerlist[-1])
            set_cookie(
                self._cookie_name,
                value=cookieval,
                max_age = self._cookie_max_age,
                path = self._cookie_path,
                domain = self._cookie_domain,
                secure = self._cookie_secure,
                httponly = self._cookie_httponly,
                )
            return True

    return InsecureCookieSessionFactory

def serialize(data, secret):
    pickled = pickle.dumps(data, pickle.HIGHEST_PROTOCOL)
    sig = hmac.new(secret, pickled, sha1).hexdigest()
    return sig + base64.standard_b64encode(pickled)

def deserialize(serialized, secret, hmac=hmac):
    # hmac parameterized only for unit tests
    if serialized is None:
        return None

    try:
        input_sig, pickled = (serialized[:40],
                              base64.standard_b64decode(serialized[40:]))
    except (binascii.Error, TypeError):
        # Badly formed data can make base64 die
        return None

    sig = hmac.new(secret, pickled, sha1).hexdigest()

    # Avoid timing attacks (note that this is cadged from Pylons and I
    # have no idea what it means)

    if len(sig) != len(input_sig):
        return None

    invalid_bits = 0

    for a, b in zip(sig, input_sig):
        invalid_bits += a != b

    if invalid_bits:
        return None

    return pickle.loads(pickled)

