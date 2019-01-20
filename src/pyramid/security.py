from zope.interface import providedBy

from pyramid.interfaces import (
    IAuthenticationPolicy,
    IAuthorizationPolicy,
    ISecuredView,
    IView,
    IViewClassifier,
)

from pyramid.threadlocal import get_current_registry

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


def _get_registry(request):
    try:
        reg = request.registry
    except AttributeError:
        reg = get_current_registry()  # b/c
    return reg


def _get_authentication_policy(request):
    registry = _get_registry(request)
    return registry.queryUtility(IAuthenticationPolicy)


def remember(request, userid, **kw):
    """
    Returns a sequence of header tuples (e.g. ``[('Set-Cookie', 'foo=abc')]``)
    on this request's response.
    These headers are suitable for 'remembering' a set of credentials
    implied by the data passed as ``userid`` and ``*kw`` using the
    current :term:`authentication policy`.  Common usage might look
    like so within the body of a view function (``response`` is
    assumed to be a :term:`WebOb` -style :term:`response` object
    computed previously by the view code):

    .. code-block:: python

       from pyramid.security import remember
       headers = remember(request, 'chrism', password='123', max_age='86400')
       response = request.response
       response.headerlist.extend(headers)
       return response

    If no :term:`authentication policy` is in use, this function will
    always return an empty sequence. If used, the composition and
    meaning of ``**kw`` must be agreed upon by the calling code and
    the effective authentication policy.

    .. versionchanged:: 1.6
        Deprecated the ``principal`` argument in favor of ``userid`` to clarify
        its relationship to the authentication policy.

    .. versionchanged:: 1.10
        Removed the deprecated ``principal`` argument.
    """
    policy = _get_authentication_policy(request)
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

    If no :term:`authentication policy` is in use, this function will
    always return an empty sequence.
    """
    policy = _get_authentication_policy(request)
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
    reg = _get_registry(request)
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


class AuthenticationAPIMixin(object):
    @property
    def authenticated_userid(self):
        """ Return the userid of the currently authenticated user or
        ``None`` if there is no :term:`authentication policy` in effect or
        there is no currently authenticated user.

        .. versionadded:: 1.5
        """
        policy = _get_authentication_policy(self)
        if policy is None:
            return None
        return policy.authenticated_userid(self)

    @property
    def unauthenticated_userid(self):
        """ Return an object which represents the *claimed* (not verified) user
        id of the credentials present in the request. ``None`` if there is no
        :term:`authentication policy` in effect or there is no user data
        associated with the current request.  This differs from
        :attr:`~pyramid.request.Request.authenticated_userid`, because the
        effective authentication policy will not ensure that a record
        associated with the userid exists in persistent storage.

        .. versionadded:: 1.5
        """
        policy = _get_authentication_policy(self)
        if policy is None:
            return None
        return policy.unauthenticated_userid(self)

    @property
    def effective_principals(self):
        """ Return the list of 'effective' :term:`principal` identifiers
        for the ``request``. If no :term:`authentication policy` is in effect,
        this will return a one-element list containing the
        :data:`pyramid.security.Everyone` principal.

        .. versionadded:: 1.5
        """
        policy = _get_authentication_policy(self)
        if policy is None:
            return [Everyone]
        return policy.effective_principals(self)


class AuthorizationAPIMixin(object):
    def has_permission(self, permission, context=None):
        """ Given a permission and an optional context, returns an instance of
        :data:`pyramid.security.Allowed` if the permission is granted to this
        request with the provided context, or the context already associated
        with the request.  Otherwise, returns an instance of
        :data:`pyramid.security.Denied`.  This method delegates to the current
        authentication and authorization policies.  Returns
        :data:`pyramid.security.Allowed` unconditionally if no authentication
        policy has been registered for this request.  If ``context`` is not
        supplied or is supplied as ``None``, the context used is the
        ``request.context`` attribute.

        :param permission: Does this request have the given permission?
        :type permission: str
        :param context: A resource object or ``None``
        :type context: object
        :returns: Either :class:`pyramid.security.Allowed` or
                  :class:`pyramid.security.Denied`.

        .. versionadded:: 1.5

        """
        if context is None:
            context = self.context
        reg = _get_registry(self)
        authn_policy = reg.queryUtility(IAuthenticationPolicy)
        if authn_policy is None:
            return Allowed('No authentication policy in use.')
        authz_policy = reg.queryUtility(IAuthorizationPolicy)
        if authz_policy is None:
            raise ValueError(
                'Authentication policy registered without '
                'authorization policy'
            )  # should never happen
        principals = authn_policy.effective_principals(self)
        return authz_policy.permits(context, principals, permission)


@implementer(IUserIdentity)
class PlainUserIdentity(object):
    def __init__(self, id):
        self.id = id


@implementer(ISecurityPolicy)
class CompatibilitySecurityPolicy(object):
    def __init__(self, authn_policy, authz_policy):
        self.authn_policy = authn_policy
        self.authz_policy = authz_policy

    def identify(self, request):
        userid = self.authn_policy.authenticated_userid(request)
        return PlainUserIdentity(userid)

    def remember(self, request, userid, **kw):
        return self.authn_policy.remember(request, userid, **kw)

    def forget(self, request):
        return self.authn_policy.forget(request)

    def permits(self, request, context, identity, permission):
        principles = self.authn_policy.effective_principles(request)
        return self.authz_policy.permits(principles)


@implementer(ISecurityPolicy)
class SessionSecurityPolicy(object):
    def __init__(self, prefix='auth.'):
        self.prefix = prefix or ''
        self.userid_key = prefix + 'userid'

    def identify(self, request):
        userid = request.session[self.userid_key]
        return PlainUserIdentity(userid)

    def remember(self, request, userid, **kw):
        """ Store a userid in the session."""
        request.session[self.userid_key] = userid
        return []

    def forget(self, request):
        """ Remove the stored userid from the session."""
        if self.userid_key in request.session:
            del request.session[self.userid_key]
        return []

    def permits(self, request, context, identity, permission):
        raise NotImplementedError(
            '`SessionSecurityPolicy` does not provide an implementation for '
            '`permits`.'
        )
