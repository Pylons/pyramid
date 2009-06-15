import inspect

from paste.urlparser import StaticURLParser
from zope.component import queryMultiAdapter
from zope.deprecation import deprecated

from repoze.bfg.interfaces import IView
from repoze.bfg.path import caller_path
from repoze.bfg.security import view_execution_permitted
from repoze.bfg.security import Unauthorized

deprecated('view_execution_permitted',
    "('from repoze.bfg.view import view_execution_permitted' is now "
    "deprecated; instead use 'from repoze.bfg.security import "
    "view_execution_permitted')",
    )

_marker = object()

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
        permitted = view_execution_permitted(context, request, name)
        if not permitted:
            raise Unauthorized(permitted)
        
    # It's no use trying to distinguish below whether response is None
    # because a) we were returned a default or b) because the view
    # function returned None: the zope.component/zope.interface
    # machinery doesn't distinguish a None returned from the view from
    # a sentinel None returned during queryMultiAdapter (even if we
    # pass a non-None default).

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
    path into a response.

    You may pass an absolute or relative filesystem path to the
    directory containing static files directory to the constructor as
    the ``root_dir`` argument.  If the path is relative, it will be
    considered relative to the directory in which the Python file
    which calls ``static`` resides.  ``cache_max_age`` influences the
    Expires and Max-Age response headers returned by the view (default
    is 3600 seconds or five minutes).  ``level`` influences how
    relative directories are resolved (the number of hops in the call
    stack), not used very often.
    """
    def __init__(self, root_dir, cache_max_age=3600, level=2):
        root_dir = caller_path(root_dir, level=level)
        self.app = StaticURLParser(root_dir, cache_max_age=cache_max_age)

    def __call__(self, context, request):
        subpath = '/'.join(request.subpath)
        request_copy = request.copy()
        # Fix up PATH_INFO to get rid of everything but the "subpath"
        # (the actual path to the file relative to the root dir).
        request_copy.environ['PATH_INFO'] = '/' + subpath
        # Zero out SCRIPT_NAME for good measure.
        request_copy.environ['SCRIPT_NAME'] = ''
        return request_copy.get_response(self.app)

class bfg_view(object):
    """ Function or class decorator which allows Python code to make
    view registrations instead of using ZCML for the same purpose.

    E.g. in the module ``views.py``::

      from models import IMyModel
      from repoze.bfg.interfaces import IRequest

      @bfg_view(name='my_view', request_type=IRequest, for_=IMyModel,
                permission='read', route_name='site1'))
      def my_view(context, request):
          return render_template_to_response('templates/my.pt')

    Equates to the ZCML::

      <view
       for='.models.IMyModel'
       view='.views.my_view'
       name='my_view'
       permission='read'
       route_name='site1'
       />

    If ``name`` is not supplied, the empty string is used (implying
    the default view).

    If ``request_type`` is not supplied, the interface
    ``repoze.bfg.interfaces.IRequest`` is used.

    If ``for_`` is not supplied, the interface
    ``zope.interface.Interface`` (implying *all* interfaces) is used.

    If ``permission`` is not supplied, no permission is registered for
    this view (it's accessible by any caller).

    If ``route_name`` is not supplied, the view declaration is
    considered to be made against a URL that doesn't match any defined
    :term:`route`.  The use of a ``route_name`` is an advanced
    feature, useful only if you're using :term:`url dispatch`.

    Any individual or all parameters can be omitted.  The simplest
    bfg_view declaration then becomes::

        @bfg_view()
        def my_view(...):
            ...

    Such a registration implies that the view name will be
    ``my_view``, registered for models with the
    ``zope.interface.Interface`` interface, using no permission,
    registered against requests which implement the default IRequest
    interface when no urldispatch route matches.

    The ``bfg_view`` decorator can also be used as a class decorator
    in Python 2.6 and better (Python 2.5 and below do not support
    class decorators)::

        from webob import Response
        from repoze.bfg.view import bfg_view

        @bfg_view()
        class MyView(object):
            def __init__(self, context, request):
                self.context = context
                self.request = request
            def __call__(self):
                return Response('hello from %s!' % self.context)

    In Python 2.5 and below, the bfg_view decorator can still be used
    against a class, although not in decorator form::

        from webob import Response
        from repoze.bfg.view import bfg_view

        class MyView(object):
            def __init__(self, context, request):
                self.context = context
                self.request = request
            def __call__(self):
                return Response('hello from %s!' % self.context)

        MyView = bfg_view()(MyView)

    .. note:: When a view is a class, the calling semantics are
              different than when it is a function or another
              non-class callable.  See :ref:`class_as_view` for more
              information.

    .. warning:: Using a class as a view is a new feature in 0.8.1+.

    To make use of any bfg_view declaration, you *must* insert the
    following boilerplate into your application registry's ZCML::
    
      <scan package="."/>
    """
    def __init__(self, name='', request_type=None, for_=None, permission=None,
                 route_name=None):
        self.name = name
        self.request_type = request_type
        self.for_ = for_
        self.permission = permission
        self.route_name = route_name

    def __call__(self, wrapped):
        _bfg_view = wrapped
        if inspect.isclass(_bfg_view):
            # If the object we're decorating is a class, turn it into
            # a function that operates like a Zope view (when it's
            # invoked, construct an instance using 'context' and
            # 'request' as position arguments, then immediately invoke
            # the __call__ method of the instance with no arguments;
            # __call__ should return an IResponse).
            def _bfg_class_view(context, request):
                inst = wrapped(context, request)
                return inst()
            _bfg_class_view.__module__ = wrapped.__module__
            _bfg_class_view.__name__ = wrapped.__name__
            _bfg_class_view.__doc__ = wrapped.__doc__
            _bfg_view = _bfg_class_view
        _bfg_view.__is_bfg_view__ = True
        _bfg_view.__permission__ = self.permission
        _bfg_view.__for__ = self.for_
        _bfg_view.__view_name__ = self.name
        _bfg_view.__request_type__ = self.request_type
        _bfg_view.__route_name__ = self.route_name
        return _bfg_view

