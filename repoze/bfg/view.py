from paste.urlparser import StaticURLParser
from webob import Response

from zope.component import queryMultiAdapter
from zope.component import queryUtility

from repoze.bfg.interfaces import ISecurityPolicy
from repoze.bfg.interfaces import IViewPermission
from repoze.bfg.interfaces import IView

from repoze.bfg.security import Unauthorized
from repoze.bfg.security import Allowed

_marker = ()

def view_execution_permitted(context, request, name=''):
    """ If the view specified by ``context`` and ``name`` is protected
    by a permission, return the result of checking the permission
    associated with the view using the effective security policy and
    the ``request``.  If no security policy is in effect, or if the
    view is not protected by a permission, return a True value. """
    security_policy = queryUtility(ISecurityPolicy)
    if security_policy:
        permission = queryMultiAdapter((context, request), IViewPermission,
                                       name=name)
        if permission is None:
            return Allowed(
                'Allowed: view name %r in context %r (no permission '
                'registered for name %r).' % (name, context, name)
                )
        return permission(security_policy)
    return Allowed('Allowed: view name %r in context %r (no security policy '
                   'in use).' % (name, context))

def render_view_to_response(context, request, name='', secure=True):
    """ Render the view named ``name`` against the specified
    ``context`` and ``request`` to an object implementing
    ``repoze.bfg.interfaces.IResponse`` or ``None`` if no such view
    exists.  This function will return ``None`` if a corresponding
    view cannot be found.  Additionally, this function will raise a
    ``ValueError`` if a view function is found and called but the view
    returns an object which does not implement
    ``repoze.bfg.interfaces.IResponse``.  If ``secure`` is ``True``,
    and the view is protected by a permission, the permission will be
    checked before calling the view function.  If the permission check
    disallows view execution (based on the current security policy), a
    ``repoze.bfg.security.Unauthorized`` exception will be raised; its
    ``args`` attribute explains why the view access was disallowed.
    If ``secure`` is ``False``, no permission checking is done."""
    if secure:
        permitted = view_execution_permitted(context, request, name)
        if not permitted:
            raise Unauthorized(permitted)

    response = queryMultiAdapter((context, request), IView, name=name,
                                 default=_marker)

    if response is _marker:
        return None

    if not is_response(response):
        raise ValueError('response did not implement IResponse: %r' % response)

    return response

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

class static(object):
    """ An instance of this class is a callable which can act as a BFG
    view; this view will serve static files from a directory on disk
    based on the ``root_dir`` you provide to its constructor.  The
    directory may contain subdirectories (recursively); the static
    view implementation will descend into these directories as
    necessary based on the components of the URL in order to resolve a
    path into a response

    Pass the absolute filesystem path to the directory containing
    static files directory to the constructor as the ``root_dir``
    argument.  ``cache_max_age`` influences the Expires and Max-Age
    response headers returned by the view (default is 3600 seconds or
    five minutes).
    """
    def __init__(self, root_dir, cache_max_age=3600):
        self.app = StaticURLParser(root_dir, cache_max_age=cache_max_age)

    def __call__(self, context, request):
        subpath = '/'.join(request.subpath)
        caught = []
        def catch_start_response(status, headers, exc_info=None):
            caught[:] = (status, headers, exc_info)
        ecopy = request.environ.copy()
        # Fix up PATH_INFO to get rid of everything but the "subpath"
        # (the actual path to the file relative to the root dir).
        # Zero out SCRIPT_NAME for good measure.
        ecopy['PATH_INFO'] = '/' + subpath
        ecopy['SCRIPT_NAME'] = ''
        body = self.app(ecopy, catch_start_response)
        if caught: 
            status, headers, exc_info = caught
            response = Response()
            response.app_iter = body
            response.status = status
            response.headerlist = headers
            return response
        else:
            raise RuntimeError('WSGI start_response not called')

