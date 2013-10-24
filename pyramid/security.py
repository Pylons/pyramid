from zope.interface import providedBy

from pyramid.interfaces import (
    IAuthenticationPolicy,
    IAuthorizationPolicy,
    ISecuredView,
    IView,
    IViewClassifier,
    )

from pyramid.compat import map_
from pyramid.threadlocal import get_current_registry

Everyone = 'system.Everyone'
Authenticated = 'system.Authenticated'
Allow = 'Allow'
Deny = 'Deny'

class AllPermissionsList(object):
    """ Stand in 'permission list' to represent all permissions """
    def __iter__(self):
        return ()
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
        reg = get_current_registry() # b/c
    return reg

# b/c
def backwards_compat_request_proxier(proxy_func):
    proxy_func.__doc__ = """ Backwards compatible wrapper.

    Proxies to ``pyramid.request.Request`` object.
    """
    return proxy_func

# b/c
@backwards_compat_request_proxier
def has_permission(permission, context, request):
    return request.has_permission(permission, context)

# b/c
@backwards_compat_request_proxier
def authenticated_userid(request):
    return request.authenticated_userid

# b/c
@backwards_compat_request_proxier
def unauthenticated_userid(request):
    return request.unauthenticated_userid

# b/c
@backwards_compat_request_proxier
def effective_principals(request):
    return request.effective_principals

# b/c
@backwards_compat_request_proxier
def remember(request, principal, **kw):
    return request.remember_userid(principal, **kw)

# b/c
@backwards_compat_request_proxier
def forget(request):
    return request.forget_userid()


def principals_allowed_by_permission(context, permission):
    """ Provided a ``context`` (a resource object), and a ``permission``
    (a string or unicode object), if a :term:`authorization policy` is
    in effect, return a sequence of :term:`principal` ids that possess
    the permission in the ``context``.  If no authorization policy is
    in effect, this will return a sequence with the single value
    :mod:`pyramid.security.Everyone` (the special principal
    identifier representing all principals).

    .. note::

       even if an :term:`authorization policy` is in effect,
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
    try:
        reg = request.registry
    except AttributeError:
        reg = get_current_registry() # b/c
    provides = [IViewClassifier] + map_(providedBy, (request, context))
    view = reg.adapters.lookup(provides, ISecuredView, name=name)
    if view is None:
        view = reg.adapters.lookup(provides, IView, name=name)
        if view is None:
            raise TypeError('No registered view satisfies the constraints. '
                            'It would not make sense to claim that this view '
                            '"is" or "is not" permitted.')
        return Allowed(
            'Allowed: view name %r in context %r (no permission defined)' %
            (name, context))
    return view.__permitted__(context, request)


class PermitsResult(int):
    def __new__(cls, s, *args):
        inst = int.__new__(cls, cls.boolval)
        inst.s = s
        inst.args = args
        return inst

    @property
    def msg(self):
        return self.s % self.args

    def __str__(self):
        return self.msg

    def __repr__(self):
        return '<%s instance at %s with msg %r>' % (self.__class__.__name__,
                                                    id(self),
                                                    self.msg)

class Denied(PermitsResult):
    """ An instance of ``Denied`` is returned when a security-related
    API or other :app:`Pyramid` code denies an action unrelated to
    an ACL check.  It evaluates equal to all boolean false types.  It
    has an attribute named ``msg`` describing the circumstances for
    the deny."""
    boolval = 0

class Allowed(PermitsResult):
    """ An instance of ``Allowed`` is returned when a security-related
    API or other :app:`Pyramid` code allows an action unrelated to
    an ACL check.  It evaluates equal to all boolean true types.  It
    has an attribute named ``msg`` describing the circumstances for
    the allow."""
    boolval = 1

class ACLPermitsResult(int):
    def __new__(cls, ace, acl, permission, principals, context):
        inst = int.__new__(cls, cls.boolval)
        inst.permission = permission
        inst.ace = ace
        inst.acl = acl
        inst.principals = principals
        inst.context = context
        return inst

    @property
    def msg(self):
        s = ('%s permission %r via ACE %r in ACL %r on context %r for '
             'principals %r')
        return s % (self.__class__.__name__,
                    self.permission,
                    self.ace,
                    self.acl,
                    self.context,
                    self.principals)

    def __str__(self):
        return self.msg

    def __repr__(self):
        return '<%s instance at %s with msg %r>' % (self.__class__.__name__,
                                                    id(self),
                                                    self.msg)

class ACLDenied(ACLPermitsResult):
    """ An instance of ``ACLDenied`` represents that a security check made
    explicitly against ACL was denied.  It evaluates equal to all boolean
    false types.  It also has the following attributes: ``acl``, ``ace``,
    ``permission``, ``principals``, and ``context``.  These attributes
    indicate the security values involved in the request.  Its __str__ method
    prints a summary of these attributes for debugging purposes.  The same
    summary is available as the ``msg`` attribute."""
    boolval = 0

class ACLAllowed(ACLPermitsResult):
    """ An instance of ``ACLAllowed`` represents that a security check made
    explicitly against ACL was allowed.  It evaluates equal to all boolean
    true types.  It also has the following attributes: ``acl``, ``ace``,
    ``permission``, ``principals``, and ``context``.  These attributes
    indicate the security values involved in the request.  Its __str__ method
    prints a summary of these attributes for debugging purposes.  The same
    summary is available as the ``msg`` attribute."""
    boolval = 1

class AuthenticationAPIMixin(object):

    def _get_authentication_policy(self):
        reg = _get_registry(self)
        return reg.queryUtility(IAuthenticationPolicy)

    @property
    def authenticated_userid(self):
        """ Return the userid of the currently authenticated user or
        ``None`` if there is no :term:`authentication policy` in effect or
        there is no currently authenticated user."""
        policy = self._get_authentication_policy()
        if policy is None:
            return None
        return policy.authenticated_userid(self)

    @property
    def unauthenticated_userid(self):
        """ Return an object which represents the *claimed* (not verified) user
        id of the credentials present in the request. ``None`` if there is no
        :term:`authentication policy` in effect or there is no user data
        associated with the current request.  This differs from
        :func:`~pyramid.security.authenticated_userid`, because the effective
        authentication policy will not ensure that a record associated with the
        userid exists in persistent storage."""
        policy = self._get_authentication_policy()
        if policy is None:
            return None
        return policy.unauthenticated_userid(self)

    @property
    def effective_principals(self):
        """ Return the list of 'effective' :term:`principal` identifiers
        for the ``request``.  This will include the userid of the
        currently authenticated user if a user is currently
        authenticated. If no :term:`authentication policy` is in effect,
        this will return an empty sequence."""
        policy = self._get_authentication_policy()
        if policy is None:
            return [Everyone]
        return policy.effective_principals(self)

    def _set_response_headers(self, response, headers):
        response.headerlist.extend(headers)

    def remember_userid(self, principal, **kw):
        """ Sets a sequence of header tuples (e.g. ``[('Set-Cookie',
        'foo=abc')]``) on this request's response.
        These headers are suitable for 'remembering' a set of credentials
        implied by the data passed as ``principal`` and ``*kw`` using the
        current :term:`authentication policy`.  Common usage might look
        like so within the body of a view function (``response`` is
        assumed to be a :term:`WebOb` -style :term:`response` object
        computed previously by the view code)::

          request.remember_userid('chrism', password='123', max_age='86400')

        If no :term:`authentication policy` is in use, this function will
        do nothing. If used, the composition and
        meaning of ``**kw`` must be agreed upon by the calling code and
        the effective authentication policy."""
        policy = self._get_authentication_policy()
        if policy is None:
            return
        headers = policy.remember(self, principal, **kw)
        callback = lambda req, resp: self._set_response_headers(resp, headers)
        self.add_response_callback(callback)

    def forget_userid(self):
        """ Sets a sequence of header tuples (e.g. ``[('Set-Cookie',
        'foo=abc')]``) suitable for 'forgetting' the set of credentials
        possessed by the currently authenticated user on the response.
        A common usage might look like so within the body of a view function
        (``response`` is assumed to be an :term:`WebOb` -style
        :term:`response` object computed previously by the view code)::

          request.forget_userid()

        If no :term:`authentication policy` is in use, this function will
        be a noop."""
        policy = self._get_authentication_policy()
        if policy is None:
            return
        headers = policy.forget(self)
        callback = lambda req, resp: self._set_response_headers(resp, headers)
        self.add_response_callback(callback)

class AuthorizationAPIMixin(object):

    def has_permission(self, permission, context=None):
        """ Given a permission and an optional context,
        returns an instance of :data:`pyramid.security.Allowed if the
        permission is granted to this request with the provided context,
        or the context already associated with the request. Otherwise,
        returns an instance of :data:`pyramid.security.Denied`.
        This method delegates to the current authentication and
        authorization policies. Returns :data:`pyramid.security.Allowed`
        unconditionally if no authentication policy has been registered
        for this request.

        .. versionchanged:: 1.5a3
           If context is None, then attempt to use the context attribute
           of self, if not set then the  AttributeError is propergated.

        :param permission: Does this request have the given permission?
        :type permission: unicode, str
        :param context: Typically a resource of a regsitered type.
        :type context: object
        :returns: `pyramid.security.PermitsResult`
        """
        if context is None:
            context = self.context
        reg = _get_registry(self)
        authn_policy = reg.queryUtility(IAuthenticationPolicy)
        if authn_policy is None:
            return Allowed('No authentication policy in use.')
        authz_policy = reg.queryUtility(IAuthorizationPolicy)
        if authz_policy is None:
            raise ValueError('Authentication policy registered without '
                             'authorization policy') # should never happen
        principals = authn_policy.effective_principals(self)
        return authz_policy.permits(context, principals, permission)
