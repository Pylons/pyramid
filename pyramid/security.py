from zope.interface import providedBy

from pyramid.interfaces import (
    IAuthenticationPolicy,
    IAuthorizationPolicy,
    ISecuredView,
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

def has_permission(permission, context, request):
    """ Provided a permission (a string or unicode object), a context
    (a :term:`resource` instance) and a request object, return an
    instance of :data:`pyramid.security.Allowed` if the permission
    is granted in this context to the user implied by the
    request. Return an instance of :mod:`pyramid.security.Denied`
    if this permission is not granted in this context to this user.
    This function delegates to the current authentication and
    authorization policies.  Return
    :data:`pyramid.security.Allowed` unconditionally if no
    authentication policy has been configured in this application."""
    try:
        reg = request.registry
    except AttributeError:
        reg = get_current_registry() # b/c
    authn_policy = reg.queryUtility(IAuthenticationPolicy)
    if authn_policy is None:
        return Allowed('No authentication policy in use.')

    authz_policy = reg.queryUtility(IAuthorizationPolicy)
    if authz_policy is None:
        raise ValueError('Authentication policy registered without '
                         'authorization policy') # should never happen
    principals = authn_policy.effective_principals(request)
    return authz_policy.permits(context, principals, permission)

def authenticated_userid(request):
    """ Return the userid of the currently authenticated user or
    ``None`` if there is no :term:`authentication policy` in effect or
    there is no currently authenticated user."""
    try:
        reg = request.registry
    except AttributeError:
        reg = get_current_registry() # b/c

    policy = reg.queryUtility(IAuthenticationPolicy)
    if policy is None:
        return None
    return policy.authenticated_userid(request)

def unauthenticated_userid(request):
    """ Return an object which represents the *claimed* (not verified) user
    id of the credentials present in the request. ``None`` if there is no
    :term:`authentication policy` in effect or there is no user data
    associated with the current request.  This differs from
    :func:`~pyramid.security.authenticated_userid`, because the effective
    authentication policy will not ensure that a record associated with the
    userid exists in persistent storage."""
    try:
        reg = request.registry
    except AttributeError:
        reg = get_current_registry() # b/c

    policy = reg.queryUtility(IAuthenticationPolicy)
    if policy is None:
        return None
    return policy.unauthenticated_userid(request)

def effective_principals(request):
    """ Return the list of 'effective' :term:`principal` identifiers
    for the ``request``.  This will include the userid of the
    currently authenticated user if a user is currently
    authenticated. If no :term:`authentication policy` is in effect,
    this will return an empty sequence."""
    try:
        reg = request.registry
    except AttributeError:
        reg = get_current_registry() # b/c

    policy = reg.queryUtility(IAuthenticationPolicy)
    if policy is None:
        return []
    return policy.effective_principals(request)

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
    protected by a permission, return ``True``."""
    try:
        reg = request.registry
    except AttributeError:
        reg = get_current_registry() # b/c
    provides = [IViewClassifier] + map_(providedBy, (request, context))
    view = reg.adapters.lookup(provides, ISecuredView, name=name)
    if view is None:
        return Allowed(
            'Allowed: view name %r in context %r (no permission defined)' %
            (name, context))
    return view.__permitted__(context, request)

def remember(request, principal, **kw):
    """ Return a sequence of header tuples (e.g. ``[('Set-Cookie',
    'foo=abc')]``) suitable for 'remembering' a set of credentials
    implied by the data passed as ``principal`` and ``*kw`` using the
    current :term:`authentication policy`.  Common usage might look
    like so within the body of a view function (``response`` is
    assumed to be a :term:`WebOb` -style :term:`response` object
    computed previously by the view code)::

      from pyramid.security import remember
      headers = remember(request, 'chrism', password='123', max_age='86400')
      response.headerlist.extend(headers)
      return response

    If no :term:`authentication policy` is in use, this function will
    always return an empty sequence.  If used, the composition and
    meaning of ``**kw`` must be agreed upon by the calling code and
    the effective authentication policy."""
    try:
        reg = request.registry
    except AttributeError:
        reg = get_current_registry() # b/c
    policy = reg.queryUtility(IAuthenticationPolicy)
    if policy is None:
        return []
    else:
        return policy.remember(request, principal, **kw)

def forget(request):
    """ Return a sequence of header tuples (e.g. ``[('Set-Cookie',
    'foo=abc')]``) suitable for 'forgetting' the set of credentials
    possessed by the currently authenticated user.  A common usage
    might look like so within the body of a view function
    (``response`` is assumed to be an :term:`WebOb` -style
    :term:`response` object computed previously by the view code)::

      from pyramid.security import forget
      headers = forget(request)
      response.headerlist.extend(headers)
      return response

    If no :term:`authentication policy` is in use, this function will
    always return an empty sequence."""
    try:
        reg = request.registry
    except AttributeError:
        reg = get_current_registry() # b/c
    policy = reg.queryUtility(IAuthenticationPolicy)
    if policy is None:
        return []
    else:
        return policy.forget(request)

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

