from zope.deprecation import deprecated
from zope.interface import implementer, providedBy

from pyramid.interfaces import (
    IAuthenticationPolicy,
    IAuthorizationPolicy,
    ISecuredView,
    ISecurityPolicy,
    IView,
    IViewClassifier,
)
from pyramid.threadlocal import get_current_registry

NO_PERMISSION_REQUIRED = '__no_permission_required__'


def _get_security_policy(request):
    return request.registry.queryUtility(ISecurityPolicy)


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
        its relationship to the security policy.

    .. versionchanged:: 1.10
        Removed the deprecated ``principal`` argument.
    """
    policy = _get_security_policy(request)
    if policy is None:
        return []
    return policy.remember(request, userid, **kw)


def forget(request, **kw):
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
    return policy.forget(request, **kw)


def principals_allowed_by_permission(context, permission):
    """
    .. deprecated:: 2.0

        The new security policy has removed the concept of principals.  See
        :ref:`upgrading_auth_20` for more information.

    Provided a ``context`` (a resource object), and a ``permission``
    string, if an :term:`authorization policy` is
    in effect, return a sequence of :term:`principal` ids that possess
    the permission in the ``context``.  If no authorization policy is
    in effect, this will return a sequence with the single value
    :mod:`pyramid.authorization.Everyone` (the special principal
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
        from pyramid.authorization import Everyone  # noqa: F811

        return [Everyone]
    return policy.principals_allowed_by_permission(context, permission)


deprecated(
    'principals_allowed_by_permission',
    'The new security policy has removed the concept of principals.  See '
    '"Upgrading Authentication/Authorization" in "What\'s New in Pyramid 2.0" '
    'of the documentation for more information.',
)


def view_execution_permitted(context, request, name=''):
    """If the view specified by ``context`` and ``name`` is protected
    by a :term:`permission`, check the permission associated with the
    view using the effective authentication/authorization policies and
    the ``request``.  Return a boolean result.  If no
    :term:`security policy` is in effect, or if the view is not
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
        """A string indicating why the result was generated."""
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


class SecurityAPIMixin:
    """Mixin for Request class providing auth-related properties."""

    @property
    def identity(self):
        """
        Return an opaque object identifying the current user or ``None`` if no
        user is authenticated or there is no :term:`security policy` in effect.

        """
        policy = _get_security_policy(self)
        if policy is None:
            return None
        return policy.identity(self)

    @property
    def authenticated_userid(self):
        """
        Return the :term:`userid` of the currently authenticated user or
        ``None`` if there is no :term:`security policy` in effect or there is
        no currently authenticated user.

        .. versionchanged:: 2.0

           This property delegates to the effective :term:`security policy`,
           ignoring old-style :term:`authentication policy`.

        """
        policy = _get_security_policy(self)
        if policy is None:
            return None
        return policy.authenticated_userid(self)

    @property
    def is_authenticated(self):
        """Return ``True`` if a user is authenticated for this request."""
        return self.authenticated_userid is not None

    def has_permission(self, permission, context=None):
        """Given a permission and an optional context, returns an instance of
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
        return policy.permits(self, context, permission)


class AuthenticationAPIMixin:
    """Mixin for Request class providing compatibility properties."""

    @property
    def unauthenticated_userid(self):
        """
        .. deprecated:: 2.0

            ``unauthenticated_userid`` does not have an equivalent in the new
            security system. Use :attr:`.authenticated_userid` or
            :attr:`.identity` instead. See :ref:`upgrading_auth_20` for more
            information.

        Return an object which represents the *claimed* (not verified) user
        id of the credentials present in the request. ``None`` if there is no
        :term:`authentication policy` in effect or there is no user data
        associated with the current request.  This differs from
        :attr:`~pyramid.request.Request.authenticated_userid`, because the
        effective authentication policy will not ensure that a record
        associated with the userid exists in persistent storage.

        """
        security = _get_security_policy(self)
        if security is None:
            return None
        if isinstance(security, LegacySecurityPolicy):
            authn = security._get_authn_policy(self)
            return authn.unauthenticated_userid(self)
        return security.authenticated_userid(self)

    unauthenticated_userid = deprecated(
        unauthenticated_userid,
        (
            'The new security policy has deprecated unauthenticated_userid. '
            'See "Upgrading Authentication/Authorization" in "What\'s New in '
            'Pyramid 2.0" of the documentation for more information.'
        ),
    )

    @property
    def effective_principals(self):
        """
        .. deprecated:: 2.0

            The new security policy has removed the concept of principals.  See
            :ref:`upgrading_auth_20` for more information.

        Return the list of 'effective' :term:`principal` identifiers
        for the ``request``. If no :term:`authentication policy` is in effect,
        this will return a one-element list containing the
        :data:`pyramid.authorization.Everyone` principal.

        """
        from pyramid.authorization import Everyone  # noqa: F811

        security = _get_security_policy(self)
        if security is not None and isinstance(security, LegacySecurityPolicy):
            authn = security._get_authn_policy(self)
            return authn.effective_principals(self)
        return [Everyone]

    effective_principals = deprecated(
        effective_principals,
        (
            'The new security policy has deprecated effective_principals. '
            'See "Upgrading Authentication/Authorization" in "What\'s New in '
            'Pyramid 2.0" of the documentation for more information.'
        ),
    )


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

    def identity(self, request):
        return self.authenticated_userid(request)

    def authenticated_userid(self, request):
        authn = self._get_authn_policy(request)
        return authn.authenticated_userid(request)

    def remember(self, request, userid, **kw):
        authn = self._get_authn_policy(request)
        return authn.remember(request, userid, **kw)

    def forget(self, request, **kw):
        if kw:
            raise ValueError(
                'Legacy authentication policies do not support keyword '
                'arguments for `forget`'
            )
        authn = self._get_authn_policy(request)
        return authn.forget(request)

    def permits(self, request, context, permission):
        authn = self._get_authn_policy(request)
        authz = self._get_authz_policy(request)
        principals = authn.effective_principals(request)
        return authz.permits(context, principals, permission)


Everyone = 'system.Everyone'
Authenticated = 'system.Authenticated'
Allow = 'Allow'
Deny = 'Deny'


class AllPermissionsList:
    """Stand in 'permission list' to represent all permissions"""

    def __iter__(self):
        return iter(())

    def __contains__(self, other):
        return True

    def __eq__(self, other):
        return isinstance(other, self.__class__)


ALL_PERMISSIONS = AllPermissionsList()
DENY_ALL = (Deny, Everyone, ALL_PERMISSIONS)


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


for attr in (
    'ALL_PERMISSIONS',
    'DENY_ALL',
    'ACLAllowed',
    'ACLDenied',
    'AllPermissionsList',
    'Allow',
    'Authenticated',
    'Deny',
    'Everyone',
):
    deprecated(
        attr,
        '"pyramid.security.{attr}" is deprecated in Pyramid 2.0. Adjust your '
        'import to "pyramid.authorization.{attr}"'.format(attr=attr),
    )
