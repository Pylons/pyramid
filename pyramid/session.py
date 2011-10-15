
try:
    import cPickle as pickle
except ImportError: # pragma: no cover
    import pickle

from hashlib import sha1
import base64
import binascii
import hmac
import time
import os

from zope.interface import implements

from pyramid.interfaces import ISession
from pyramid.util import strings_differ

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

def UnencryptedCookieSessionFactoryConfig(
    secret,
    timeout=1200,
    cookie_name='session',
    cookie_max_age=None,
    cookie_path='/',
    cookie_domain=None,
    cookie_secure=False, 
    cookie_httponly=False,
    cookie_on_exception=True,
    ):
    """
    Configure a :term:`session factory` which will provide unencrypted
    (but signed) cookie-based sessions.  The return value of this
    function is a :term:`session factory`, which may be provided as
    the ``session_factory`` argument of a
    :class:`pyramid.config.Configurator` constructor, or used
    as the ``session_factory`` argument of the
    :meth:`pyramid.config.Configurator.set_session_factory`
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
      while rendering a view.  Default: ``True``.

    """

    class UnencryptedCookieSessionFactory(dict):
        """ Dictionary-like session object """
        implements(ISession)

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
            value = None
            state = {}
            cookieval = request.cookies.get(self._cookie_name)
            if cookieval is not None:
                try:
                    value = signed_deserialize(cookieval, self._secret)
                except ValueError:
                    value = None

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

        # flash API methods
        @manage_accessed
        def flash(self, msg, queue='', allow_duplicate=True):
            storage = self.setdefault('_f_' + queue, [])
            if allow_duplicate or (msg not in storage):
                storage.append(msg)

        @manage_accessed
        def pop_flash(self, queue=''):
            storage = self.pop('_f_' + queue, [])
            return storage

        @manage_accessed
        def peek_flash(self, queue=''):
            storage = self.get('_f_' + queue, [])
            return storage

        # CSRF API methods
        @manage_accessed
        def new_csrf_token(self):
            token = os.urandom(20).encode('hex')
            self['_csrft_'] = token
            return token

        @manage_accessed
        def get_csrf_token(self):
            token = self.get('_csrft_', None)
            if token is None:
                token = self.new_csrf_token()
            return token

        # non-API methods
        def _set_cookie(self, response):
            if not self._cookie_on_exception:
                exception = getattr(self.request, 'exception', None)
                if exception is not None: # dont set a cookie during exceptions
                    return False
            cookieval = signed_serialize(
                (self.accessed, self.created, dict(self)), self._secret
                )
            if len(cookieval) > 4064:
                raise ValueError(
                    'Cookie value is too long to store (%s bytes)' %
                    len(cookieval)
                    )
            response.set_cookie(
                self._cookie_name,
                value=cookieval,
                max_age = self._cookie_max_age,
                path = self._cookie_path,
                domain = self._cookie_domain,
                secure = self._cookie_secure,
                httponly = self._cookie_httponly,
                )
            return True

    return UnencryptedCookieSessionFactory

def signed_serialize(data, secret):
    """ Serialize any pickleable structure (``data``) and sign it
    using the ``secret`` (must be a string).  Return the
    serialization, which includes the signature as its first 40 bytes.
    The ``signed_deserialize`` method will deserialize such a value.

    This function is useful for creating signed cookies.  For example:

    .. code-block:: python

       cookieval = signed_serialize({'a':1}, 'secret')
       response.set_cookie('signed_cookie', cookieval)
    """
    pickled = pickle.dumps(data, pickle.HIGHEST_PROTOCOL)
    sig = hmac.new(secret, pickled, sha1).hexdigest()
    return sig + base64.standard_b64encode(pickled)

def signed_deserialize(serialized, secret, hmac=hmac):
    """ Deserialize the value returned from ``signed_serialize``.  If
    the value cannot be deserialized for any reason, a
    :exc:`ValueError` exception will be raised.

    This function is useful for deserializing a signed cookie value
    created by ``signed_serialize``.  For example:

    .. code-block:: python

       cookieval = request.cookies['signed_cookie']
       data = signed_deserialize(cookieval, 'secret')
    """
    # hmac parameterized only for unit tests
    try:
        input_sig, pickled = (serialized[:40],
                              base64.standard_b64decode(serialized[40:]))
    except (binascii.Error, TypeError), e:
        # Badly formed data can make base64 die
        raise ValueError('Badly formed base64 data: %s' % e)

    sig = hmac.new(secret, pickled, sha1).hexdigest()

    # Avoid timing attacks (see
    # http://seb.dbzteam.org/crypto/python-oauth-timing-hmac.pdf)
    if strings_differ(sig, input_sig):
        raise ValueError('Invalid signature')

    return pickle.loads(pickled)

