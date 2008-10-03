from zope.component import queryMultiAdapter
from zope.component import queryUtility

from repoze.bfg.interfaces import ISecurityPolicy
from repoze.bfg.interfaces import IViewPermission
from repoze.bfg.interfaces import IView
from repoze.bfg.security import Unauthorized

def render_view_to_response(context, request, name='', secure=True):
    """ Render the view named ``name`` against the specified
    ``context`` and ``request`` to an object implementing
    ``repoze.bfg.interfaces.IResponse`` or ``None`` if no such view
    exists.  This function will return ``None`` if a corresponding
    view cannot be found.  If ``secure`` is ``True``, and the view is
    protected by a permission, the permission will be checked before
    calling the view function.  If the permission check disallows view
    execution (based on the current security policy), a
    ``repoze.bfg.security.Unauthorized`` exception will be raised; its
    ``args`` attribute explains why the view access was disallowed.
    If ``secure`` is ``False``, no permission checking is done."""
    if secure:
        security_policy = queryUtility(ISecurityPolicy)
        if security_policy:
            permission = queryMultiAdapter((context, request), IViewPermission,
                                           name=name)
            if permission is not None:
                result = permission(security_policy)
                if not result:
                    raise Unauthorized(result)
    return queryMultiAdapter((context, request), IView, name=name)

def render_view_to_iterable(context, request, name='', secure=True):
    """ Render the view named ``name`` against the specified
    ``context`` and ``request``, and return an iterable representing
    the view response's ``app_iter`` (see the interface named
    ``repoze.bfg.interfaces.IResponse``).  This function will return
    ``None`` if a corresponding view cannot be found.  Additionally,
    this function will raise a ``ValueError`` if a view function is
    found and called but the view does not return an object which
    implements ``repoze.bfg.interfaces.IResponse``.  You can usually
    get the string representation of the return value of this function
    by calling ``''.join(iterable)``, or just use ``render_view``
    instead.  If ``secure`` is ``True``, and the view is protected by
    a permission, the permission will be checked before calling the
    view function.  If the permission check disallows view execution
    (based on the current security policy), a
    ``repoze.bfg.security.Unauthorized`` exception will be raised; its
    ``args`` attribute explains why the view access was disallowed.
    If ``secure`` is ``False``, no permission checking is done."""
    response = render_view_to_response(context, request, name, secure)
    if response is None:
        return None
    if not is_response(response):
        raise ValueError('response did not implement IResponse: %r' % response)
    return response.app_iter

def render_view(context, request, name='', secure=True):
    """ Render the view named ``name`` against the specified
    ``context`` and ``request``, and unwind the the view response's
    ``app_iter`` (see the interface named
    ``repoze.bfg.interfaces.IResponse``) into a single string.  This
    function will return ``None`` if a corresponding view cannot be
    found.  Additionally, this function will raise a ``ValueError`` if
    a view function is found and called but the view does not return
    an object which implements ``repoze.bfg.interfaces.IResponse``.
    If ``secure`` is ``True``, and the view is protected by a
    permission, the permission will be checked before calling the view
    function.  If the permission check disallows view execution (based
    on the current security policy), a
    ``repoze.bfg.security.Unauthorized`` exception will be raised; its
    ``args`` attribute explains why the view access was disallowed.
    If ``secure`` is ``False``, no permission checking is done."""
    iterable = render_view_to_iterable(context, request, name, secure)
    if iterable is None:
        return None
    return ''.join(iterable)

def is_response(ob):
    """ Return True if ``ob`` implements the
    ``repoze.bfg.interfaces.IResponse`` interface, False if not.  Note
    that this isn't actually a true Zope interface check, it's a
    duck-typing check, as response objects are not obligated to
    actually implement a Zope interface."""
    # response objects aren't obligated to implement a Zope interface,
    # so we do it the hard way
    if ( hasattr(ob, 'app_iter') and hasattr(ob, 'headerlist') and
         hasattr(ob, 'status') ):
        if ( hasattr(ob.app_iter, '__iter__') and
             hasattr(ob.headerlist, '__iter__') and
             isinstance(ob.status, basestring) ) :
            return True
    return False

