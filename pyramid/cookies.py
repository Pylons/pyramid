import base64
import binascii
import hashlib
import hmac

from pyramid.compat import (
    bytes_,
    pickle,
)
from pyramid.util import strings_differ

try:
    from webob.cookies import make_cookie
except ImportError: # pragma: no cover
    # compat with webob <= 1.2.3
    from webob.cookies import Morsel
    from datetime import timedelta

    def make_cookie(name, value, **kw):
        if value is None:
            value = ''
            kw['max_age'] = 0
            kw['expires'] = timedelta(days=-5)
        morsel = Morsel(bytes_(name), bytes_(value))
        morsel.path = bytes_(kw['path'])
        morsel.domain = bytes_(kw['domain'])
        morsel.max_age = kw['max_age']
        morsel.httponly = kw['httponly']
        morsel.secure = kw['secure']
        morsel.expires = kw.get('expires')
        return morsel.serialize()

class PickleSerializer(object):
    def dumps(self, appstruct):
        return pickle.dumps(appstruct, pickle.HIGHEST_PROTOCOL)

    def loads(self, cstruct):
        return pickle.loads(cstruct)

class SignedSerializer(object):
    """
    A helper to cryptographically sign arbitrary content using HMAC.

    The serializer accepts arbitrary functions for performing the actual
    serialization and deserialization.

    ``secret``
      A string which is used to sign the cookie. The secret should be at
      least as long as the block size of the selected hash algorithm. For
      ``sha512`` this would mean a 128 bit (64 character) secret.  It should
      be unique within the set of secret values provided to Pyramid for
      its various subsystems (see :ref:`admonishment_against_secret_sharing`).

    ``salt``
      A namespace to avoid collisions between different uses of a shared
      secret. Reusing a secret for different parts of an application is
      strongly discouraged (see :ref:`admonishment_against_secret_sharing`).

    ``hashalg``
      The HMAC digest algorithm to use for signing. The algorithm must be
      supported by the :mod:`hashlib` library. Default: ``'sha512'``.

    ``serialize``
      A callable accepting a Python object and returning a bytestring. A
      ``ValueError`` should be raised for malformed inputs.
      Default: ``None`, which will use :func:`pickle.dumps`.

    ``deserialize``
      A callable accepting a bytestring and returning a Python object. A
      ``ValueError`` should be raised for malformed inputs.
      Default: ``None`, which will use :func:`pickle.loads`.
    """
    _default_serializer = PickleSerializer()

    def __init__(self,
                 secret,
                 salt,
                 hashalg='sha512',
                 serialize=None,
                 deserialize=None,
                 ):
        self.salt = salt
        self.secret = secret
        self.hashalg = hashalg

        self.salted_secret = bytes_(salt or '') + bytes_(secret)

        self.digestmod = lambda string=b'': hashlib.new(self.hashalg, string)
        self.digest_size = self.digestmod().digest_size

        if serialize is None:
            serialize = self._default_serializer.dumps
        if deserialize is None:
            deserialize = self._default_serializer.loads

        self.serialize = serialize
        self.deserialize = deserialize

    def dumps(self, appstruct):
        """
        Given an ``appstruct``, serialize and sign the data.

        Returns a bytestring.
        """
        cstruct = self.serialize(appstruct)
        sig = hmac.new(self.salted_secret, cstruct, self.digestmod).digest()
        return base64.urlsafe_b64encode(sig + cstruct).rstrip(b'=')

    def loads(self, bstruct):
        """
        Given a ``bstruct``, verify the signature and then deserialize.

        A ``ValueError` will be raised if the signature fails to validate.
        """
        try:
            b64padding = b'=' * (-len(bstruct) % 4)
            fstruct = base64.urlsafe_b64decode(bytes_(bstruct) + b64padding)
        except (binascii.Error, TypeError) as e:
            raise ValueError('Badly formed base64 data: %s' % e)

        cstruct = fstruct[:-self.digest_size]
        expected_sig = fstruct[-self.digest_size:]

        sig = hmac.new(self.salted_secret, cstruct, self.digestmod).digest()
        if strings_differ(sig, expected_sig):
            raise ValueError('Invalid signature')

        return self.deserialize(cstruct)

_default = object()

class CookieHelper(object):
    """
    A helper class that helps bring some sanity to the insanity that is cookie
    handling.

    The helper is capable of generating multiple cookies if necessary to
    support subdomains and parent domains.

    ``cookie_name``
      The name of the cookie used for sessioning. Default: ``'session'``.

    ``max_age``
      The maximum age of the cookie used for sessioning (in seconds).
      Default: ``None`` (browser scope).

    ``secure``
      The 'secure' flag of the session cookie. Default: ``False``.

    ``httponly``
      Hide the cookie from Javascript by setting the 'HttpOnly' flag of the
      session cookie. Default: ``False``.

    ``path``
      The path used for the session cookie. Default: ``'/'``.

    ``domain``
      The domain used for the session cookie.  Default: ``None`` (no domain).

    ``wild_domain``
      A cookie will be generated for the wildcard domain. If your site is
      hosted as ``example.com`` this will make the cookie available for
      sites underneath ``example.com`` such as ``www.example.com``.
      Default: ``False``.

    ``parent_domain``
      A cookie will be generated for the parent domain of the current site.
      For example if your site is hosted under ``www.example.com`` a cookie
      will be generated for ``.example.com``. This can be useful if you have
      multiple sites sharing the same domain. This option supercedes
      the ``wild_domain`` option. Default: ``False``.

    ``serialize``
      A callable accepting a Python object and returning a bytestring. A
      ``ValueError`` should be raised for malformed inputs.
      Default: ``None`, which will use :func:`pickle.dumps`.

    ``deserialize``
      A callable accepting a bytestring and returning a Python object. A
      ``ValueError`` should be raised for malformed inputs.
      Default: ``None`, which will use :func:`pickle.loads`.

    .. versionadded: 1.5a3
    """
    _default_serializer = PickleSerializer()

    def __init__(self,
                 cookie_name,
                 secure=False,
                 max_age=None,
                 httponly=False,
                 path='/',
                 domain=None,
                 wild_domain=False,
                 parent_domain=False,
                 serialize=None,
                 deserialize=None,
                 ):
        self.cookie_name = cookie_name
        self.secure = secure
        self.max_age = max_age
        self.httponly = httponly
        self.path = path
        self.domain = domain
        self.wild_domain = wild_domain
        self.parent_domain = parent_domain

        if serialize is None:
            serialize = self._default_serializer.dumps
        if deserialize is None:
            deserialize = self._default_serializer.loads

        self.serialize = serialize
        self.deserialize = deserialize

    def raw_headers(self, request, value, max_age=_default):
        """ Retrieve raw headers for setting cookies.

        Returns a list of headers that should be set for the cookies to
        be correctly tracked.
        """
        if value is None:
            max_age = 0
            bstruct = None
        else:
            bstruct = self.serialize(value)

        return self._get_cookies(request.environ, bstruct, max_age=max_age)

    def set_cookies(self, request, response, value, max_age=_default):
        """ Set the cookies on a response."""
        cookies = self.raw_headers(request, value, max_age=max_age)
        response.headerlist.extend(cookies)
        return response

    def get_value(self, request):
        """ Looks for a cookie by name, and returns its value

        Looks for the cookie in the cookies jar, and if it can find it it will
        attempt to deserialize it. Throws a ValueError if it fails due to an
        error, or returns None if there is no cookie.
        """
        cookie = request.cookies.get(self.cookie_name)

        if cookie:
            return self.deserialize(bytes_(cookie))

    def _get_cookies(self, environ, value, max_age):
        """Internal function

        This returns a list of cookies that are valid HTTP Headers.

        :environ: The request environment
        :value: The value to store in the cookie
        """

        # If the user doesn't provide max_age, grab it from self
        if max_age is _default:
            max_age = self.max_age

        # Length selected based upon http://browsercookielimits.x64.me
        if value is not None and len(value) > 4093:
            raise ValueError(
                'Cookie value is too long to store (%s bytes)' %
                len(value)
            )

        cur_domain = environ.get('HTTP_HOST', environ.get('SERVER_NAME', ''))

        # While Chrome, IE, and Firefox can cope, Opera (at least) cannot
        # cope with a port number in the cookie domain when the URL it
        # receives the cookie from does not also have that port number in it
        # (e.g via a proxy).  In the meantime, HTTP_HOST is sent with port
        # number, and neither Firefox nor Chrome do anything with the
        # information when it's provided in a cookie domain except strip it
        # out.  So we strip out any port number from the cookie domain
        # aggressively to avoid problems.  See also
        # https://github.com/Pylons/pyramid/issues/131
        if ':' in cur_domain:
            cur_domain = cur_domain.split(':', 1)[0]

        domains = []
        if self.domain:
            domains.append(self.domain)
        else:
            if self.parent_domain and cur_domain.count('.') > 1:
                domains.append('.' + cur_domain.split('.', 1)[1])
            else:
                domains.append(None)
                domains.append(cur_domain)
                if self.wild_domain:
                    domains.append('.' + cur_domain)

        cookies = []
        for domain in domains:
            cookievalue = make_cookie(
                self.cookie_name,
                value,
                path=self.path,
                domain=domain,
                max_age=max_age,
                httponly=self.httponly,
                secure=self.secure,
            )
            cookies.append(('Set-Cookie', cookievalue))

        return cookies

class SignedCookieHelper(CookieHelper):
    """
    A helper for generating cookies that are signed to prevent tampering.

    By default this will create a single cookie, given a value it will
    serialize it, then use HMAC to cryptographically sign the data. Finally
    the result is base64-encoded for transport. This way a remote user can
    not tamper with the value without uncovering the secret/salt used.

    ``secret``
      A string which is used to sign the cookie. The secret should be at
      least as long as the block size of the selected hash algorithm. For
      ``sha512`` this would mean a 128 bit (64 character) secret.  It should
      be unique within the set of secret values provided to Pyramid for
      its various subsystems (see :ref:`admonishment_against_secret_sharing`).

    ``salt``
      A namespace to avoid collisions between different uses of a shared
      secret. Reusing a secret for different parts of an application is
      strongly discouraged (see :ref:`admonishment_against_secret_sharing`).

    ``hashalg``
      The HMAC digest algorithm to use for signing. The algorithm must be
      supported by the :mod:`hashlib` library. Default: ``'sha512'``.

    ``cookie_name``
      The name of the cookie used for sessioning. Default: ``'session'``.

    ``max_age``
      The maximum age of the cookie used for sessioning (in seconds).
      Default: ``None`` (browser scope).

    ``secure``
      The 'secure' flag of the session cookie. Default: ``False``.

    ``httponly``
      Hide the cookie from Javascript by setting the 'HttpOnly' flag of the
      session cookie. Default: ``False``.

    ``path``
      The path used for the session cookie. Default: ``'/'``.

    ``domain``
      The domain used for the session cookie.  Default: ``None`` (no domain).

    ``wild_domain``
      A cookie will be generated for the wildcard domain. If your site is
      hosted as ``example.com`` this will make the cookie available for
      sites underneath ``example.com`` such as ``www.example.com``.
      Default: ``False``.

    ``parent_domain``
      A cookie will be generated for the parent domain of the current site.
      For example if your site is hosted under ``www.example.com`` a cookie
      will be generated for ``.example.com``. This can be useful if you have
      multiple sites sharing the same domain. This option supercedes
      the ``wild_domain`` option. Default: ``False``.

    ``serialize``
      A callable accepting a Python object and returning a bytestring. A
      ``ValueError`` should be raised for malformed inputs.
      Default: ``None`, which will use :func:`pickle.dumps`.

    ``deserialize``
      A callable accepting a bytestring and returning a Python object. A
      ``ValueError`` should be raised for malformed inputs.
      Default: ``None`, which will use :func:`pickle.loads`.

    .. versionadded: 1.5a3
    """
    def __init__(self,
                 secret,
                 salt,
                 cookie_name,
                 secure=False,
                 max_age=None,
                 httponly=False,
                 path="/",
                 domain=None,
                 wild_domain=False,
                 parent_domain=False,
                 hashalg='sha512',
                 serialize=None,
                 deserialize=None,
                 ):
        self.secret = secret
        self.salt = salt
        self.hashalg = hashalg

        if serialize is None:
            serialize = self.default_serializer.dumps
        if deserialize is None:
            deserialize = self.default_serializer.loads

        serializer = SignedSerializer(secret,
                                      salt,
                                      hashalg,
                                      serialize=serialize,
                                      deserialize=deserialize)
        CookieHelper.__init__(self,
                              cookie_name,
                              secure=secure,
                              max_age=max_age,
                              httponly=httponly,
                              path=path,
                              domain=domain,
                              wild_domain=wild_domain,
                              parent_domain=parent_domain,
                              serialize=serializer.dumps,
                              deserialize=serializer.loads)
