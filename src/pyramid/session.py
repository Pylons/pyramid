import binascii
import os
import pickle
import time
from webob.cookies import JSONSerializer, SignedSerializer
from zope.deprecation import deprecated
from zope.interface import implementer

from pyramid.csrf import check_csrf_origin, check_csrf_token
from pyramid.interfaces import ISession
from pyramid.util import bytes_, text_


def manage_accessed(wrapped):
    """Decorator which causes a cookie to be renewed when an accessor
    method is called."""

    def accessed(session, *arg, **kw):
        session.accessed = now = int(time.time())
        if session._reissue_time is not None:
            if now - session.renewed > session._reissue_time:
                session.changed()
        return wrapped(session, *arg, **kw)

    accessed.__doc__ = wrapped.__doc__
    return accessed


def manage_changed(wrapped):
    """Decorator which causes a cookie to be set when a setter method
    is called."""

    def changed(session, *arg, **kw):
        session.accessed = int(time.time())
        session.changed()
        return wrapped(session, *arg, **kw)

    changed.__doc__ = wrapped.__doc__
    return changed


class PickleSerializer:
    """
    .. deprecated:: 2.0

    .. warning::

        In :app:`Pyramid` 2.0 the default ``serializer`` option changed to
        use :class:`pyramid.session.JSONSerializer`, and ``PickleSerializer``
        has been been removed from active Pyramid code.

        Pyramid will require JSON-serializable objects in :app:`Pyramid` 2.0.

        Please see :ref:`upgrading_session_20`.

    A serializer that uses the pickle protocol to dump Python data to bytes.

    This was the default serializer used by Pyramid, but has been deprecated.

    ``protocol`` may be specified to control the version of pickle used.
    Defaults to :attr:`pickle.HIGHEST_PROTOCOL`.
    """

    def __init__(self, protocol=pickle.HIGHEST_PROTOCOL):
        self.protocol = protocol

    def loads(self, bstruct):
        """Accept bytes and return a Python object."""
        try:
            return pickle.loads(bstruct)
        except Exception:
            # this block should catch at least:
            # ValueError, AttributeError, ImportError; but more to be safe
            raise ValueError

    def dumps(self, appstruct):
        """Accept a Python object and return bytes."""
        return pickle.dumps(appstruct, self.protocol)


deprecated(
    'PickleSerializer',
    'pyramid.session.PickleSerializer is deprecated as of Pyramid 2.0 for '
    'security concerns. Use pyramid.session.JSONSerializer or reference the '
    'narrative documentation for information on building a migration tool.',
)


JSONSerializer = JSONSerializer  # api


def BaseCookieSessionFactory(
    serializer,
    cookie_name='session',
    max_age=None,
    path='/',
    domain=None,
    secure=False,
    httponly=False,
    samesite='Lax',
    timeout=1200,
    reissue_time=0,
    set_on_exception=True,
):
    """
    Configure a :term:`session factory` which will provide cookie-based
    sessions.  The return value of this function is a :term:`session factory`,
    which may be provided as the ``session_factory`` argument of a
    :class:`pyramid.config.Configurator` constructor, or used as the
    ``session_factory`` argument of the
    :meth:`pyramid.config.Configurator.set_session_factory` method.

    The session factory returned by this function will create sessions
    which are limited to storing fewer than 4000 bytes of data (as the
    payload must fit into a single cookie).

    .. warning:

       This class provides no protection from tampering and is only intended
       to be used by framework authors to create their own cookie-based
       session factories.

    Parameters:

    ``serializer``
      An object with two methods: ``loads`` and ``dumps``.  The ``loads``
      method should accept bytes and return a Python object.  The ``dumps``
      method should accept a Python object and return bytes.  A ``ValueError``
      should be raised for malformed inputs.

    ``cookie_name``
      The name of the cookie used for sessioning. Default: ``'session'``.

    ``max_age``
      The maximum age of the cookie used for sessioning (in seconds).
      Default: ``None`` (browser scope).

    ``path``
      The path used for the session cookie. Default: ``'/'``.

    ``domain``
      The domain used for the session cookie.  Default: ``None`` (no domain).

    ``secure``
      The 'secure' flag of the session cookie. Default: ``False``.

    ``httponly``
      Hide the cookie from Javascript by setting the 'HttpOnly' flag of the
      session cookie. Default: ``False``.

    ``samesite``
      The 'samesite' option of the session cookie. Set the value to ``None``
      to turn off the samesite option.  Default: ``'Lax'``.

    ``timeout``
      A number of seconds of inactivity before a session times out. If
      ``None`` then the cookie never expires. This lifetime only applies
      to the *value* within the cookie. Meaning that if the cookie expires
      due to a lower ``max_age``, then this setting has no effect.
      Default: ``1200``.

    ``reissue_time``
      The number of seconds that must pass before the cookie is automatically
      reissued as the result of a request which accesses the session. The
      duration is measured as the number of seconds since the last session
      cookie was issued and 'now'.  If this value is ``0``, a new cookie
      will be reissued on every request accessing the session. If ``None``
      then the cookie's lifetime will never be extended.

      A good rule of thumb: if you want auto-expired cookies based on
      inactivity: set the ``timeout`` value to 1200 (20 mins) and set the
      ``reissue_time`` value to perhaps a tenth of the ``timeout`` value
      (120 or 2 mins).  It's nonsensical to set the ``timeout`` value lower
      than the ``reissue_time`` value, as the ticket will never be reissued.
      However, such a configuration is not explicitly prevented.

      Default: ``0``.

    ``set_on_exception``
      If ``True``, set a session cookie even if an exception occurs
      while rendering a view. Default: ``True``.

    .. versionadded: 1.5a3

    .. versionchanged: 1.10

       Added the ``samesite`` option and made the default ``'Lax'``.
    """

    @implementer(ISession)
    class CookieSession(dict):
        """Dictionary-like session object"""

        # configuration parameters
        _cookie_name = cookie_name
        _cookie_max_age = max_age if max_age is None else int(max_age)
        _cookie_path = path
        _cookie_domain = domain
        _cookie_secure = secure
        _cookie_httponly = httponly
        _cookie_samesite = samesite
        _cookie_on_exception = set_on_exception
        _timeout = timeout if timeout is None else int(timeout)
        _reissue_time = (
            reissue_time if reissue_time is None else int(reissue_time)
        )

        # dirty flag
        _dirty = False

        def __init__(self, request):
            self.request = request
            now = time.time()
            created = renewed = now
            new = True
            value = None
            state = {}
            cookieval = request.cookies.get(self._cookie_name)
            if cookieval is not None:
                try:
                    value = serializer.loads(bytes_(cookieval))
                except ValueError:
                    # the cookie failed to deserialize, dropped
                    value = None

            if value is not None:
                try:
                    # since the value is not necessarily signed, we have
                    # to unpack it a little carefully
                    rval, cval, sval = value
                    renewed = float(rval)
                    created = float(cval)
                    state = sval
                    new = False
                except (TypeError, ValueError):
                    # value failed to unpack properly or renewed was not
                    # a numeric type so we'll fail deserialization here
                    state = {}

            if self._timeout is not None:
                if now - renewed > self._timeout:
                    # expire the session because it was not renewed
                    # before the timeout threshold
                    state = {}

            self.created = created
            self.accessed = renewed
            self.renewed = renewed
            self.new = new
            dict.__init__(self, state)

        # ISession methods
        def changed(self):
            if not self._dirty:
                self._dirty = True

                def set_cookie_callback(request, response):
                    self._set_cookie(response)
                    self.request = None  # explicitly break cycle for gc

                self.request.add_response_callback(set_cookie_callback)

        def invalidate(self):
            self.clear()  # XXX probably needs to unset cookie

        # non-modifying dictionary methods
        get = manage_accessed(dict.get)
        __getitem__ = manage_accessed(dict.__getitem__)
        items = manage_accessed(dict.items)
        values = manage_accessed(dict.values)
        keys = manage_accessed(dict.keys)
        __contains__ = manage_accessed(dict.__contains__)
        __len__ = manage_accessed(dict.__len__)
        __iter__ = manage_accessed(dict.__iter__)

        # modifying dictionary methods
        clear = manage_changed(dict.clear)
        update = manage_changed(dict.update)
        setdefault = manage_changed(dict.setdefault)
        pop = manage_changed(dict.pop)
        popitem = manage_changed(dict.popitem)
        __setitem__ = manage_changed(dict.__setitem__)
        __delitem__ = manage_changed(dict.__delitem__)

        # flash API methods
        @manage_changed
        def flash(self, msg, queue='', allow_duplicate=True):
            storage = self.setdefault('_f_' + queue, [])
            if allow_duplicate or (msg not in storage):
                storage.append(msg)

        @manage_changed
        def pop_flash(self, queue=''):
            storage = self.pop('_f_' + queue, [])
            return storage

        @manage_accessed
        def peek_flash(self, queue=''):
            storage = self.get('_f_' + queue, [])
            return storage

        # CSRF API methods
        @manage_changed
        def new_csrf_token(self):
            token = text_(binascii.hexlify(os.urandom(20)))
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
                if (
                    exception is not None
                ):  # dont set a cookie during exceptions
                    return False
            cookieval = text_(
                serializer.dumps((self.accessed, self.created, dict(self)))
            )
            if len(cookieval) > 4064:
                raise ValueError(
                    'Cookie value is too long to store (%s bytes)'
                    % len(cookieval)
                )
            response.set_cookie(
                self._cookie_name,
                value=cookieval,
                max_age=self._cookie_max_age,
                path=self._cookie_path,
                domain=self._cookie_domain,
                secure=self._cookie_secure,
                httponly=self._cookie_httponly,
                samesite=self._cookie_samesite,
            )
            return True

    return CookieSession


def SignedCookieSessionFactory(
    secret,
    cookie_name='session',
    max_age=None,
    path='/',
    domain=None,
    secure=False,
    httponly=False,
    samesite='Lax',
    set_on_exception=True,
    timeout=1200,
    reissue_time=0,
    hashalg='sha512',
    salt='pyramid.session.',
    serializer=None,
):
    """
    Configure a :term:`session factory` which will provide signed
    cookie-based sessions.  The return value of this
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
      A string which is used to sign the cookie. The secret should be at
      least as long as the block size of the selected hash algorithm. For
      ``sha512`` this would mean a 512 bit (64 character) secret.  It should
      be unique within the set of secret values provided to Pyramid for
      its various subsystems (see :ref:`admonishment_against_secret_sharing`).

    ``hashalg``
      The HMAC digest algorithm to use for signing. The algorithm must be
      supported by the :mod:`hashlib` library. Default: ``'sha512'``.

    ``salt``
      A namespace to avoid collisions between different uses of a shared
      secret. Reusing a secret for different parts of an application is
      strongly discouraged (see :ref:`admonishment_against_secret_sharing`).
      Default: ``'pyramid.session.'``.

    ``cookie_name``
      The name of the cookie used for sessioning. Default: ``'session'``.

    ``max_age``
      The maximum age of the cookie used for sessioning (in seconds).
      Default: ``None`` (browser scope).

    ``path``
      The path used for the session cookie. Default: ``'/'``.

    ``domain``
      The domain used for the session cookie.  Default: ``None`` (no domain).

    ``secure``
      The 'secure' flag of the session cookie. Default: ``False``.

    ``httponly``
      Hide the cookie from Javascript by setting the 'HttpOnly' flag of the
      session cookie. Default: ``False``.

    ``samesite``
      The 'samesite' option of the session cookie. Set the value to ``None``
      to turn off the samesite option.  Default: ``'Lax'``.

    ``timeout``
      A number of seconds of inactivity before a session times out. If
      ``None`` then the cookie never expires. This lifetime only applies
      to the *value* within the cookie. Meaning that if the cookie expires
      due to a lower ``max_age``, then this setting has no effect.
      Default: ``1200``.

    ``reissue_time``
      The number of seconds that must pass before the cookie is automatically
      reissued as the result of accessing the session. The
      duration is measured as the number of seconds since the last session
      cookie was issued and 'now'.  If this value is ``0``, a new cookie
      will be reissued on every request accessing the session. If ``None``
      then the cookie's lifetime will never be extended.

      A good rule of thumb: if you want auto-expired cookies based on
      inactivity: set the ``timeout`` value to 1200 (20 mins) and set the
      ``reissue_time`` value to perhaps a tenth of the ``timeout`` value
      (120 or 2 mins).  It's nonsensical to set the ``timeout`` value lower
      than the ``reissue_time`` value, as the ticket will never be reissued.
      However, such a configuration is not explicitly prevented.

      Default: ``0``.

    ``set_on_exception``
      If ``True``, set a session cookie even if an exception occurs
      while rendering a view. Default: ``True``.

    ``serializer``
      An object with two methods: ``loads`` and ``dumps``.  The ``loads``
      method should accept bytes and return a Python object.  The ``dumps``
      method should accept a Python object and return bytes.  A ``ValueError``
      should be raised for malformed inputs.  If a serializer is not passed,
      the :class:`pyramid.session.JSONSerializer` serializer will be used.

    .. warning::

        In :app:`Pyramid` 2.0 the default ``serializer`` option changed to
        use :class:`pyramid.session.JSONSerializer`. See
        :ref:`upgrading_session_20` for more information about why this
        change was made.

    .. versionadded: 1.5a3

    .. versionchanged: 1.10

        Added the ``samesite`` option and made the default ``Lax``.

    .. versionchanged: 2.0

        Changed the default ``serializer`` to be an instance of
        :class:`pyramid.session.JSONSerializer`.

    """
    if serializer is None:
        serializer = JSONSerializer()

    signed_serializer = SignedSerializer(
        secret, salt, hashalg, serializer=serializer
    )

    return BaseCookieSessionFactory(
        signed_serializer,
        cookie_name=cookie_name,
        max_age=max_age,
        path=path,
        domain=domain,
        secure=secure,
        httponly=httponly,
        samesite=samesite,
        timeout=timeout,
        reissue_time=reissue_time,
        set_on_exception=set_on_exception,
    )


check_csrf_origin = check_csrf_origin  # api
deprecated(
    'check_csrf_origin',
    'pyramid.session.check_csrf_origin is deprecated as of Pyramid '
    '1.9. Use pyramid.csrf.check_csrf_origin instead.',
)

check_csrf_token = check_csrf_token  # api
deprecated(
    'check_csrf_token',
    'pyramid.session.check_csrf_token is deprecated as of Pyramid '
    '1.9. Use pyramid.csrf.check_csrf_token instead.',
)
