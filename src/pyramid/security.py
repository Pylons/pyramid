from codecs import utf_8_decode
from codecs import utf_8_encode
import hashlib
import base64
import time as time_mod
from urllib.parse import quote, unquote
import warnings
import re

from webob.cookies import CookieProfile

from zope.interface import implementer, providedBy

from pyramid.interfaces import (
    ISecurityPolicy,
    IAuthenticationPolicy,
    IAuthorizationPolicy,
    ISecuredView,
    IView,
    IViewClassifier,
)

from pyramid.location import lineage

from pyramid.util import is_nonstr_iter, strings_differ, bytes_, ascii_, text_

from pyramid.util import SimpleSerializer

from pyramid.threadlocal import get_current_registry

VALID_TOKEN = re.compile(r"^[A-Za-z][A-Za-z0-9+_-]*$")

Everyone = 'system.Everyone'
Authenticated = 'system.Authenticated'
Allow = 'Allow'
Deny = 'Deny'


class AllPermissionsList(object):
    """ Stand in 'permission list' to represent all permissions """

    def __iter__(self):
        return iter(())

    def __contains__(self, other):
        return True

    def __eq__(self, other):
        return isinstance(other, self.__class__)


ALL_PERMISSIONS = AllPermissionsList()
DENY_ALL = (Deny, Everyone, ALL_PERMISSIONS)

NO_PERMISSION_REQUIRED = '__no_permission_required__'


def _get_security_policy(request):
    return request.registry.queryUtility(ISecurityPolicy)


def _get_authentication_policy(request):
    return request.registry.queryUtility(IAuthenticationPolicy)


def remember(request, userid, **kw):
    """
    Returns a sequence of header tuples (e.g. ``[('Set-Cookie', 'foo=abc')]``)
    on this request's response.
    These headers are suitable for 'remembering' a set of credentials
    implied by the data passed as ``userid`` and ``*kw`` using the
    current :term:`security policy`.  Common usage might look
    like so within the body of a view function (``response`` is
    assumed to be a :term:`WebOb` -style :term:`response` object
    computed previously by the view code):

    .. code-block:: python

       from pyramid.security import remember
       headers = remember(request, 'chrism', password='123', max_age='86400')
       response = request.response
       response.headerlist.extend(headers)
       return response

    If no :term:`security policy` is in use, this function will
    always return an empty sequence. If used, the composition and
    meaning of ``**kw`` must be agreed upon by the calling code and
    the effective security policy.

    .. versionchanged:: 1.6
        Deprecated the ``principal`` argument in favor of ``userid`` to clarify
        its relationship to the authentication policy.

    .. versionchanged:: 1.10
        Removed the deprecated ``principal`` argument.
    """
    policy = _get_security_policy(request)
    if policy is None:
        return []
    return policy.remember(request, userid, **kw)


def forget(request):
    """
    Return a sequence of header tuples (e.g. ``[('Set-Cookie',
    'foo=abc')]``) suitable for 'forgetting' the set of credentials
    possessed by the currently authenticated user.  A common usage
    might look like so within the body of a view function
    (``response`` is assumed to be an :term:`WebOb` -style
    :term:`response` object computed previously by the view code):

    .. code-block:: python

       from pyramid.security import forget
       headers = forget(request)
       response.headerlist.extend(headers)
       return response

    If no :term:`security policy` is in use, this function will
    always return an empty sequence.
    """
    policy = _get_security_policy(request)
    if policy is None:
        return []
    return policy.forget(request)


def principals_allowed_by_permission(context, permission):
    """ Provided a ``context`` (a resource object), and a ``permission``
    string, if an :term:`authorization policy` is
    in effect, return a sequence of :term:`principal` ids that possess
    the permission in the ``context``.  If no authorization policy is
    in effect, this will return a sequence with the single value
    :mod:`pyramid.security.Everyone` (the special principal
    identifier representing all principals).

    .. note::

       Even if an :term:`authorization policy` is in effect,
       some (exotic) authorization policies may not implement the
       required machinery for this function; those will cause a
       :exc:`NotImplementedError` exception to be raised when this
       function is invoked.

    """
    reg = get_current_registry()
    policy = reg.queryUtility(IAuthorizationPolicy)
    if policy is None:
        return [Everyone]
    return policy.principals_allowed_by_permission(context, permission)


def view_execution_permitted(context, request, name=''):
    """ If the view specified by ``context`` and ``name`` is protected
    by a :term:`permission`, check the permission associated with the
    view using the effective authentication/authorization policies and
    the ``request``.  Return a boolean result.  If no
    :term:`authorization policy` is in effect, or if the view is not
    protected by a permission, return ``True``. If no view can view found,
    an exception will be raised.

    .. versionchanged:: 1.4a4
       An exception is raised if no view is found.

    """
    reg = request.registry
    provides = [IViewClassifier] + [providedBy(x) for x in (request, context)]
    # XXX not sure what to do here about using _find_views or analogue;
    # for now let's just keep it as-is
    view = reg.adapters.lookup(provides, ISecuredView, name=name)
    if view is None:
        view = reg.adapters.lookup(provides, IView, name=name)
        if view is None:
            raise TypeError(
                'No registered view satisfies the constraints. '
                'It would not make sense to claim that this view '
                '"is" or "is not" permitted.'
            )
        return Allowed(
            'Allowed: view name %r in context %r (no permission defined)'
            % (name, context)
        )
    return view.__permitted__(context, request)


class PermitsResult(int):
    def __new__(cls, s, *args):
        """
        Create a new instance.

        :param fmt: A format string explaining the reason for denial.
        :param args: Arguments are stored and used with the format string
                      to generate the ``msg``.

        """
        inst = int.__new__(cls, cls.boolval)
        inst.s = s
        inst.args = args
        return inst

    @property
    def msg(self):
        """ A string indicating why the result was generated."""
        return self.s % self.args

    def __str__(self):
        return self.msg

    def __repr__(self):
        return '<%s instance at %s with msg %r>' % (
            self.__class__.__name__,
            id(self),
            self.msg,
        )


class Denied(PermitsResult):
    """
    An instance of ``Denied`` is returned when a security-related
    API or other :app:`Pyramid` code denies an action unrelated to
    an ACL check.  It evaluates equal to all boolean false types.  It
    has an attribute named ``msg`` describing the circumstances for
    the deny.

    """

    boolval = 0


class Allowed(PermitsResult):
    """
    An instance of ``Allowed`` is returned when a security-related
    API or other :app:`Pyramid` code allows an action unrelated to
    an ACL check.  It evaluates equal to all boolean true types.  It
    has an attribute named ``msg`` describing the circumstances for
    the allow.

    """

    boolval = 1


class ACLPermitsResult(PermitsResult):
    def __new__(cls, ace, acl, permission, principals, context):
        """
        Create a new instance.

        :param ace: The :term:`ACE` that matched, triggering the result.
        :param acl: The :term:`ACL` containing ``ace``.
        :param permission: The required :term:`permission`.
        :param principals: The list of :term:`principals <principal>` provided.
        :param context: The :term:`context` providing the :term:`lineage`
                        searched.

        """
        fmt = (
            '%s permission %r via ACE %r in ACL %r on context %r for '
            'principals %r'
        )
        inst = PermitsResult.__new__(
            cls, fmt, cls.__name__, permission, ace, acl, context, principals
        )
        inst.permission = permission
        inst.ace = ace
        inst.acl = acl
        inst.principals = principals
        inst.context = context
        return inst


class ACLDenied(ACLPermitsResult, Denied):
    """
    An instance of ``ACLDenied`` is a specialization of
    :class:`pyramid.security.Denied` that represents that a security check
    made explicitly against ACL was denied.  It evaluates equal to all
    boolean false types.  It also has the following attributes: ``acl``,
    ``ace``, ``permission``, ``principals``, and ``context``.  These
    attributes indicate the security values involved in the request.  Its
    ``__str__`` method prints a summary of these attributes for debugging
    purposes. The same summary is available as the ``msg`` attribute.

    """


class ACLAllowed(ACLPermitsResult, Allowed):
    """
    An instance of ``ACLAllowed`` is a specialization of
    :class:`pyramid.security.Allowed` that represents that a security check
    made explicitly against ACL was allowed.  It evaluates equal to all
    boolean true types.  It also has the following attributes: ``acl``,
    ``ace``, ``permission``, ``principals``, and ``context``.  These
    attributes indicate the security values involved in the request.  Its
    ``__str__`` method prints a summary of these attributes for debugging
    purposes. The same summary is available as the ``msg`` attribute.

    """


class SecurityAPIMixin(object):
    @property
    def identity(self):
        """
        Return an opaque object identifying the current user or ``None`` if no
        user is authenticated or there is no :term:`security policy` in effect.

        """
        policy = _get_security_policy(self)
        if policy is None:
            return None
        return policy.identify(self)

    def has_permission(self, permission, context=None):
        """ Given a permission and an optional context, returns an instance of
        :data:`pyramid.security.Allowed` if the permission is granted to this
        request with the provided context, or the context already associated
        with the request.  Otherwise, returns an instance of
        :data:`pyramid.security.Denied`.  This method delegates to the current
        security policy.  Returns
        :data:`pyramid.security.Allowed` unconditionally if no security
        policy has been registered for this request.  If ``context`` is not
        supplied or is supplied as ``None``, the context used is the
        ``request.context`` attribute.

        :param permission: Does this request have the given permission?
        :type permission: str
        :param context: A resource object or ``None``
        :type context: object
        :returns: Either :class:`pyramid.security.Allowed` or
                  :class:`pyramid.security.Denied`.

        """
        if context is None:
            context = self.context
        policy = _get_security_policy(self)
        if policy is None:
            return Allowed('No security policy in use.')
        identity = policy.identify(self)
        return policy.permits(self, context, identity, permission)


class AuthenticationAPIMixin(object):
    @property
    def authenticated_userid(self):
        """ Return the userid of the currently authenticated user or
        ``None`` if there is no :term:`authentication policy` in effect or
        there is no currently authenticated user.

        .. deprecated:: 2.0

            Use ``request.identity`` instead.

        """
        authn = _get_authentication_policy(self)
        security = _get_security_policy(self)
        if authn is not None:
            return authn.authenticated_userid(self)
        elif security is not None:
            return str(security.identify(self))
        else:
            return None

    @property
    def unauthenticated_userid(self):
        """ Return an object which represents the *claimed* (not verified) user
        id of the credentials present in the request. ``None`` if there is no
        :term:`authentication policy` in effect or there is no user data
        associated with the current request.  This differs from
        :attr:`~pyramid.request.Request.authenticated_userid`, because the
        effective authentication policy will not ensure that a record
        associated with the userid exists in persistent storage.

        .. deprecated:: 2.0

            Use ``request.identity`` instead.

        """
        authn = _get_authentication_policy(self)
        security = _get_security_policy(self)
        if authn is not None:
            return authn.unauthenticated_userid(self)
        elif security is not None:
            return security.identify(self)
        else:
            return None

    @property
    def effective_principals(self):
        """ Return the list of 'effective' :term:`principal` identifiers
        for the ``request``. If no :term:`authentication policy` is in effect,
        this will return a one-element list containing the
        :data:`pyramid.security.Everyone` principal.

        .. deprecated:: 2.0

        """
        policy = _get_authentication_policy(self)
        if policy is None:
            return [Everyone]
        return policy.effective_principals(self)


@implementer(ISecurityPolicy)
class LegacySecurityPolicy:
    """
    A :term:`security policy` which provides a backwards compatibility shim for
    the :term:`authentication policy` and the :term:`authorization policy`.

    """

    def _get_authn_policy(self, request):
        return request.registry.getUtility(IAuthenticationPolicy)

    def _get_authz_policy(self, request):
        return request.registry.getUtility(IAuthorizationPolicy)

    def identify(self, request):
        authn = self._get_authn_policy(request)
        return authn.authenticated_userid(request)

    def remember(self, request, userid, **kw):
        authn = self._get_authn_policy(request)
        return authn.remember(request, userid, **kw)

    def forget(self, request):
        authn = self._get_authn_policy(request)
        return authn.forget(request)

    def permits(self, request, context, identity, permission):
        authn = self._get_authn_policy(request)
        authz = self._get_authz_policy(request)
        principals = authn.effective_principals(request)
        return authz.permits(context, principals, permission)


class ACLHelper:
    """ A helper for use with constructing a :term:`security policy` which
    consults an :term:`ACL` object attached to a :term:`context` to determine
    authorization information about a :term:`principal` or multiple principals.
    If the context is part of a :term:`lineage`, the context's parents are
    consulted for ACL information too.

    """

    def permits(self, context, principals, permission):
        """ Return an instance of :class:`pyramid.security.ACLAllowed` if the
        ACL allows access a user with the given principals, return an instance
        of :class:`pyramid.security.ACLDenied` if not.

        When checking if principals are allowed, the security policy consults
        the ``context`` for an ACL first.  If no ACL exists on the context, or
        one does exist but the ACL does not explicitly allow or deny access for
        any of the effective principals, consult the context's parent ACL, and
        so on, until the lineage is exhausted or we determine that the policy
        permits or denies.

        During this processing, if any :data:`pyramid.security.Deny`
        ACE is found matching any principal in ``principals``, stop
        processing by returning an
        :class:`pyramid.security.ACLDenied` instance (equals
        ``False``) immediately.  If any
        :data:`pyramid.security.Allow` ACE is found matching any
        principal, stop processing by returning an
        :class:`pyramid.security.ACLAllowed` instance (equals
        ``True``) immediately.  If we exhaust the context's
        :term:`lineage`, and no ACE has explicitly permitted or denied
        access, return an instance of
        :class:`pyramid.security.ACLDenied` (equals ``False``).

        """
        acl = '<No ACL found on any object in resource lineage>'

        for location in lineage(context):
            try:
                acl = location.__acl__
            except AttributeError:
                continue

            if acl and callable(acl):
                acl = acl()

            for ace in acl:
                ace_action, ace_principal, ace_permissions = ace
                if ace_principal in principals:
                    if not is_nonstr_iter(ace_permissions):
                        ace_permissions = [ace_permissions]
                    if permission in ace_permissions:
                        if ace_action == Allow:
                            return ACLAllowed(
                                ace, acl, permission, principals, location
                            )
                        else:
                            return ACLDenied(
                                ace, acl, permission, principals, location
                            )

        # default deny (if no ACL in lineage at all, or if none of the
        # principals were mentioned in any ACE we found)
        return ACLDenied(
            '<default deny>', acl, permission, principals, context
        )

    def principals_allowed_by_permission(self, context, permission):
        """ Return the set of principals explicitly granted the permission
        named ``permission`` according to the ACL directly attached to the
        ``context`` as well as inherited ACLs based on the :term:`lineage`.

        When computing principals allowed by a permission, we compute the set
        of principals that are explicitly granted the ``permission`` in the
        provided ``context``.  We do this by walking 'up' the object graph
        *from the root* to the context.  During this walking process, if we
        find an explicit :data:`pyramid.security.Allow` ACE for a principal
        that matches the ``permission``, the principal is included in the allow
        list.  However, if later in the walking process that principal is
        mentioned in any :data:`pyramid.security.Deny` ACE for the permission,
        the principal is removed from the allow list.  If a
        :data:`pyramid.security.Deny` to the principal
        :data:`pyramid.security.Everyone` is encountered during the walking
        process that matches the ``permission``, the allow list is cleared for
        all principals encountered in previous ACLs.  The walking process ends
        after we've processed the any ACL directly attached to ``context``; a
        set of principals is returned.

        """
        allowed = set()

        for location in reversed(list(lineage(context))):
            # NB: we're walking *up* the object graph from the root
            try:
                acl = location.__acl__
            except AttributeError:
                continue

            allowed_here = set()
            denied_here = set()

            if acl and callable(acl):
                acl = acl()

            for ace_action, ace_principal, ace_permissions in acl:
                if not is_nonstr_iter(ace_permissions):
                    ace_permissions = [ace_permissions]
                if (ace_action == Allow) and (permission in ace_permissions):
                    if ace_principal not in denied_here:
                        allowed_here.add(ace_principal)
                if (ace_action == Deny) and (permission in ace_permissions):
                    denied_here.add(ace_principal)
                    if ace_principal == Everyone:
                        # clear the entire allowed set, as we've hit a
                        # deny of Everyone ala (Deny, Everyone, ALL)
                        allowed = set()
                        break
                    elif ace_principal in allowed:
                        allowed.remove(ace_principal)

            allowed.update(allowed_here)

        return allowed


class SessionAuthenticationHelper:
    """ A helper for use with a :term:`security policy` which stores user data
    in the configured :term:`session`.

    Constructor Arguments

    ``prefix``

       A prefix used when storing the authentication parameters in the
       session. Defaults to 'auth.'. Optional.

    """

    def __init__(self, prefix='auth.'):
        self.userid_key = prefix + 'userid'

    def remember(self, request, userid, **kw):
        """ Store a userid in the session."""
        request.session[self.userid_key] = userid
        return []

    def forget(self, request):
        """ Remove the stored userid from the session."""
        if self.userid_key in request.session:
            del request.session[self.userid_key]
        return []

    def identify(self, request):
        return request.session.get(self.userid_key)


def b64encode(v):
    return base64.b64encode(bytes_(v)).strip().replace(b'\n', b'')


def b64decode(v):
    return base64.b64decode(bytes_(v))


# this class licensed under the MIT license (stolen from Paste)
class AuthTicket(object):
    """
    This class represents an authentication token.  You must pass in
    the shared secret, the userid, and the IP address.  Optionally you
    can include tokens (a list of strings, representing role names),
    'user_data', which is arbitrary data available for your own use in
    later scripts.  Lastly, you can override the cookie name and
    timestamp.

    Once you provide all the arguments, use .cookie_value() to
    generate the appropriate authentication ticket.

    Usage::

        token = AuthTicket('sharedsecret', 'username',
            os.environ['REMOTE_ADDR'], tokens=['admin'])
        val = token.cookie_value()

    """

    def __init__(
        self,
        secret,
        userid,
        ip,
        tokens=(),
        user_data='',
        time=None,
        cookie_name='auth_tkt',
        secure=False,
        hashalg='md5',
    ):
        self.secret = secret
        self.userid = userid
        self.ip = ip
        self.tokens = ','.join(tokens)
        self.user_data = user_data
        if time is None:
            self.time = time_mod.time()
        else:
            self.time = time
        self.cookie_name = cookie_name
        self.secure = secure
        self.hashalg = hashalg

    def digest(self):
        return calculate_digest(
            self.ip,
            self.time,
            self.secret,
            self.userid,
            self.tokens,
            self.user_data,
            self.hashalg,
        )

    def cookie_value(self):
        v = '%s%08x%s!' % (self.digest(), int(self.time), quote(self.userid))
        if self.tokens:
            v += self.tokens + '!'
        v += self.user_data
        return v


# this class licensed under the MIT license (stolen from Paste)
class BadTicket(Exception):
    """
    Exception raised when a ticket can't be parsed.  If we get far enough to
    determine what the expected digest should have been, expected is set.
    This should not be shown by default, but can be useful for debugging.
    """

    def __init__(self, msg, expected=None):
        self.expected = expected
        Exception.__init__(self, msg)


# this function licensed under the MIT license (stolen from Paste)
def parse_ticket(secret, ticket, ip, hashalg='md5'):
    """
    Parse the ticket, returning (timestamp, userid, tokens, user_data).

    If the ticket cannot be parsed, a ``BadTicket`` exception will be raised
    with an explanation.
    """
    ticket = text_(ticket).strip('"')
    digest_size = hashlib.new(hashalg).digest_size * 2
    digest = ticket[:digest_size]
    try:
        timestamp = int(ticket[digest_size : digest_size + 8], 16)
    except ValueError as e:
        raise BadTicket('Timestamp is not a hex integer: %s' % e)
    try:
        userid, data = ticket[digest_size + 8 :].split('!', 1)
    except ValueError:
        raise BadTicket('userid is not followed by !')
    userid = unquote(userid)
    if '!' in data:
        tokens, user_data = data.split('!', 1)
    else:  # pragma: no cover (never generated)
        # @@: Is this the right order?
        tokens = ''
        user_data = data

    expected = calculate_digest(
        ip, timestamp, secret, userid, tokens, user_data, hashalg
    )

    # Avoid timing attacks (see
    # http://seb.dbzteam.org/crypto/python-oauth-timing-hmac.pdf)
    if strings_differ(expected, digest):
        raise BadTicket(
            'Digest signature is not correct', expected=(expected, digest)
        )

    tokens = tokens.split(',')

    return (timestamp, userid, tokens, user_data)


# this function licensed under the MIT license (stolen from Paste)
def calculate_digest(
    ip, timestamp, secret, userid, tokens, user_data, hashalg='md5'
):
    secret = bytes_(secret, 'utf-8')
    userid = bytes_(userid, 'utf-8')
    tokens = bytes_(tokens, 'utf-8')
    user_data = bytes_(user_data, 'utf-8')
    hash_obj = hashlib.new(hashalg)

    # Check to see if this is an IPv6 address
    if ':' in ip:
        ip_timestamp = ip + str(int(timestamp))
        ip_timestamp = bytes_(ip_timestamp)
    else:
        # encode_ip_timestamp not required, left in for backwards compatibility
        ip_timestamp = encode_ip_timestamp(ip, timestamp)

    hash_obj.update(
        ip_timestamp + secret + userid + b'\0' + tokens + b'\0' + user_data
    )
    digest = hash_obj.hexdigest()
    hash_obj2 = hashlib.new(hashalg)
    hash_obj2.update(bytes_(digest) + secret)
    return hash_obj2.hexdigest()


# this function licensed under the MIT license (stolen from Paste)
def encode_ip_timestamp(ip, timestamp):
    ip_chars = ''.join(map(chr, map(int, ip.split('.'))))
    t = int(timestamp)
    ts = (
        (t & 0xFF000000) >> 24,
        (t & 0xFF0000) >> 16,
        (t & 0xFF00) >> 8,
        t & 0xFF,
    )
    ts_chars = ''.join(map(chr, ts))
    return bytes_(ip_chars + ts_chars)


class AuthTktCookieHelper:
    """
    A helper class used for constructing a :term:`security policy` with stores
    the user identity in a signed cookie.

    Constructor Arguments

    ``secret``

       The secret (a string) used for auth_tkt cookie signing.  This value
       should be unique across all values provided to Pyramid for various
       subsystem secrets (see :ref:`admonishment_against_secret_sharing`).
       Required.

    ``cookie_name``

       Default: ``auth_tkt``.  The cookie name used
       (string).  Optional.

    ``secure``

       Default: ``False``.  Only send the cookie back over a secure
       conn.  Optional.

    ``include_ip``

       Default: ``False``.  Make the requesting IP address part of
       the authentication data in the cookie.  Optional.

       For IPv6 this option is not recommended. The ``mod_auth_tkt``
       specification does not specify how to handle IPv6 addresses, so using
       this option in combination with IPv6 addresses may cause an
       incompatible cookie. It ties the authentication ticket to that
       individual's IPv6 address.

    ``timeout``

       Default: ``None``.  Maximum number of seconds which a newly
       issued ticket will be considered valid.  After this amount of
       time, the ticket will expire (effectively logging the user
       out).  If this value is ``None``, the ticket never expires.
       Optional.

    ``reissue_time``

       Default: ``None``.  If this parameter is set, it represents the number
       of seconds that must pass before an authentication token cookie is
       automatically reissued as the result of a request which requires
       authentication.  The duration is measured as the number of seconds
       since the last auth_tkt cookie was issued and 'now'.  If this value is
       ``0``, a new ticket cookie will be reissued on every request which
       requires authentication.

       A good rule of thumb: if you want auto-expired cookies based on
       inactivity: set the ``timeout`` value to 1200 (20 mins) and set the
       ``reissue_time`` value to perhaps a tenth of the ``timeout`` value
       (120 or 2 mins).  It's nonsensical to set the ``timeout`` value lower
       than the ``reissue_time`` value, as the ticket will never be reissued
       if so.  However, such a configuration is not explicitly prevented.

       Optional.

    ``max_age``

       Default: ``None``.  The max age of the auth_tkt cookie, in
       seconds.  This differs from ``timeout`` inasmuch as ``timeout``
       represents the lifetime of the ticket contained in the cookie,
       while this value represents the lifetime of the cookie itself.
       When this value is set, the cookie's ``Max-Age`` and
       ``Expires`` settings will be set, allowing the auth_tkt cookie
       to last between browser sessions.  It is typically nonsensical
       to set this to a value that is lower than ``timeout`` or
       ``reissue_time``, although it is not explicitly prevented.
       Optional.

    ``path``

       Default: ``/``. The path for which the auth_tkt cookie is valid.
       May be desirable if the application only serves part of a domain.
       Optional.

    ``http_only``

       Default: ``False``. Hide cookie from JavaScript by setting the
       HttpOnly flag. Not honored by all browsers.
       Optional.

    ``wild_domain``

       Default: ``True``. An auth_tkt cookie will be generated for the
       wildcard domain. If your site is hosted as ``example.com`` this
       will make the cookie available for sites underneath ``example.com``
       such as ``www.example.com``.
       Optional.

    ``parent_domain``

       Default: ``False``. An auth_tkt cookie will be generated for the
       parent domain of the current site. For example if your site is
       hosted under ``www.example.com`` a cookie will be generated for
       ``.example.com``. This can be useful if you have multiple sites
       sharing the same domain. This option supercedes the ``wild_domain``
       option.
       Optional.

    ``domain``

       Default: ``None``. If provided the auth_tkt cookie will only be
       set for this domain. This option is not compatible with ``wild_domain``
       and ``parent_domain``.
       Optional.

    ``hashalg``

       Default: ``sha512`` (the literal string).

       Any hash algorithm supported by Python's ``hashlib.new()`` function
       can be used as the ``hashalg``.

       Cookies generated by different instances of AuthTktAuthenticationPolicy
       using different ``hashalg`` options are not compatible. Switching the
       ``hashalg`` will imply that all existing users with a valid cookie will
       be required to re-login.

       Optional.

    ``samesite``

        Default: ``'Lax'``.  The 'samesite' option of the session cookie. Set
        the value to ``None`` to turn off the samesite option.

        This option is available as of :app:`Pyramid` 1.10.
    """

    parse_ticket = staticmethod(parse_ticket)  # for tests
    AuthTicket = AuthTicket  # for tests
    BadTicket = BadTicket  # for tests
    now = None  # for tests

    userid_type_decoders = {
        'int': int,
        'unicode': lambda x: utf_8_decode(x)[0],  # bw compat for old cookies
        'b64unicode': lambda x: utf_8_decode(b64decode(x))[0],
        'b64str': lambda x: b64decode(x),
    }

    userid_type_encoders = {
        int: ('int', str),
        str: ('b64unicode', lambda x: b64encode(utf_8_encode(x)[0])),
        bytes: ('b64str', lambda x: b64encode(x)),
    }

    def __init__(
        self,
        secret,
        cookie_name='auth_tkt',
        secure=False,
        include_ip=False,
        timeout=None,
        reissue_time=None,
        max_age=None,
        http_only=False,
        path="/",
        wild_domain=True,
        hashalg='md5',
        parent_domain=False,
        domain=None,
        samesite='Lax',
    ):
        self.cookie_profile = CookieProfile(
            cookie_name=cookie_name,
            secure=secure,
            max_age=max_age,
            httponly=http_only,
            path=path,
            serializer=SimpleSerializer(),
            samesite=samesite,
        )

        self.secret = secret
        self.cookie_name = cookie_name
        self.secure = secure
        self.include_ip = include_ip
        self.timeout = timeout if timeout is None else int(timeout)
        self.reissue_time = (
            reissue_time if reissue_time is None else int(reissue_time)
        )
        self.max_age = max_age if max_age is None else int(max_age)
        self.wild_domain = wild_domain
        self.parent_domain = parent_domain
        self.domain = domain
        self.hashalg = hashalg

    def _get_cookies(self, request, value, max_age=None):
        cur_domain = request.domain

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

        profile = self.cookie_profile(request)

        kw = {}
        kw['domains'] = domains
        if max_age is not None:
            kw['max_age'] = max_age

        headers = profile.get_headers(value, **kw)
        return headers

    def identify(self, request):
        """ Return a dictionary with authentication information, or ``None``
        if no valid auth_tkt is attached to ``request``"""
        environ = request.environ
        cookie = request.cookies.get(self.cookie_name)

        if cookie is None:
            return None

        if self.include_ip:
            remote_addr = environ['REMOTE_ADDR']
        else:
            remote_addr = '0.0.0.0'

        try:
            timestamp, userid, tokens, user_data = self.parse_ticket(
                self.secret, cookie, remote_addr, self.hashalg
            )
        except self.BadTicket:
            return None

        now = self.now  # service tests

        if now is None:
            now = time_mod.time()

        if self.timeout and ((timestamp + self.timeout) < now):
            # the auth_tkt data has expired
            return None

        userid_typename = 'userid_type:'
        user_data_info = user_data.split('|')
        for datum in filter(None, user_data_info):
            if datum.startswith(userid_typename):
                userid_type = datum[len(userid_typename) :]
                decoder = self.userid_type_decoders.get(userid_type)
                if decoder:
                    userid = decoder(userid)

        reissue = self.reissue_time is not None

        if reissue and not hasattr(request, '_authtkt_reissued'):
            if (now - timestamp) > self.reissue_time:
                # See https://github.com/Pylons/pyramid/issues#issue/108
                tokens = list(filter(None, tokens))
                headers = self.remember(
                    request, userid, max_age=self.max_age, tokens=tokens
                )

                def reissue_authtkt(request, response):
                    if not hasattr(request, '_authtkt_reissue_revoked'):
                        for k, v in headers:
                            response.headerlist.append((k, v))

                request.add_response_callback(reissue_authtkt)
                request._authtkt_reissued = True

        environ['REMOTE_USER_TOKENS'] = tokens
        environ['REMOTE_USER_DATA'] = user_data
        environ['AUTH_TYPE'] = 'cookie'

        identity = {}
        identity['timestamp'] = timestamp
        identity['userid'] = userid
        identity['tokens'] = tokens
        identity['userdata'] = user_data
        return identity

    def forget(self, request):
        """ Return a set of expires Set-Cookie headers, which will destroy
        any existing auth_tkt cookie when attached to a response"""
        request._authtkt_reissue_revoked = True
        return self._get_cookies(request, None)

    def remember(self, request, userid, max_age=None, tokens=()):
        """ Return a set of Set-Cookie headers; when set into a response,
        these headers will represent a valid authentication ticket.

        ``max_age``
          The max age of the auth_tkt cookie, in seconds.  When this value is
          set, the cookie's ``Max-Age`` and ``Expires`` settings will be set,
          allowing the auth_tkt cookie to last between browser sessions.  If
          this value is ``None``, the ``max_age`` value provided to the
          helper itself will be used as the ``max_age`` value.  Default:
          ``None``.

        ``tokens``
          A sequence of strings that will be placed into the auth_tkt tokens
          field.  Each string in the sequence must be of the Python ``str``
          type and must match the regex ``^[A-Za-z][A-Za-z0-9+_-]*$``.
          Tokens are available in the returned identity when an auth_tkt is
          found in the request and unpacked.  Default: ``()``.
        """
        max_age = self.max_age if max_age is None else int(max_age)

        environ = request.environ

        if self.include_ip:
            remote_addr = environ['REMOTE_ADDR']
        else:
            remote_addr = '0.0.0.0'

        user_data = ''

        encoding_data = self.userid_type_encoders.get(type(userid))

        if encoding_data:
            encoding, encoder = encoding_data
        else:
            warnings.warn(
                "userid is of type {}, and is not supported by the "
                "AuthTktAuthenticationPolicy. Explicitly converting to string "
                "and storing as base64. Subsequent requests will receive a "
                "string as the userid, it will not be decoded back to the "
                "type provided.".format(type(userid)),
                RuntimeWarning,
            )
            encoding, encoder = self.userid_type_encoders.get(str)
            userid = str(userid)

        userid = encoder(userid)
        user_data = 'userid_type:%s' % encoding

        new_tokens = []
        for token in tokens:
            if isinstance(token, str):
                try:
                    token = ascii_(token)
                except UnicodeEncodeError:
                    raise ValueError("Invalid token %r" % (token,))
            if not (isinstance(token, str) and VALID_TOKEN.match(token)):
                raise ValueError("Invalid token %r" % (token,))
            new_tokens.append(token)
        tokens = tuple(new_tokens)

        if hasattr(request, '_authtkt_reissued'):
            request._authtkt_reissue_revoked = True

        ticket = self.AuthTicket(
            self.secret,
            userid,
            remote_addr,
            tokens=tokens,
            user_data=user_data,
            cookie_name=self.cookie_name,
            secure=self.secure,
            hashalg=self.hashalg,
        )

        cookie_value = ticket.cookie_value()
        return self._get_cookies(request, cookie_value, max_age)
