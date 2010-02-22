import cgi
import mimetypes
import os
import sys

# See http://bugs.python.org/issue5853 which is a recursion bug
# that seems to effect Python 2.6, Python 2.6.1, and 2.6.2 (a fix
# has been applied on the Python 2 trunk).  This workaround should
# really be in Paste if anywhere, but it's easiest to just do it
# here and get it over with to avoid needing to deal with any
# fallout.

if hasattr(mimetypes, 'init'):
    mimetypes.init()

from webob import Response
from webob.exc import HTTPFound

from paste.urlparser import StaticURLParser

from zope.deprecation import deprecated
from zope.interface import providedBy
from zope.interface.advice import getFrameInfo

from repoze.bfg.interfaces import IResponseFactory
from repoze.bfg.interfaces import IRoutesMapper
from repoze.bfg.interfaces import IView

from repoze.bfg.path import caller_package
from repoze.bfg.path import package_path
from repoze.bfg.resource import resolve_resource_spec
from repoze.bfg.resource import resource_spec_from_abspath
from repoze.bfg.static import PackageURLParser
from repoze.bfg.threadlocal import get_current_registry

# b/c imports
from repoze.bfg.security import view_execution_permitted

view_execution_permitted # prevent PyFlakes from complaining

deprecated('view_execution_permitted',
    "('from repoze.bfg.view import view_execution_permitted' was  "
    "deprecated as of repoze.bfg 1.0; instead use 'from "
    "repoze.bfg.security import view_execution_permitted')",
    )

deprecated('NotFound',
    "('from repoze.bfg.view import NotFound' was  "
    "deprecated as of repoze.bfg 1.1; instead use 'from "
    "repoze.bfg.exceptions import NotFound')",
    )

_marker = object()

def render_view_to_response(context, request, name='', secure=True):
    """ Call the :term:`view callable` configured with a :term:`view
    configuration` that matches the :term:`view name` ``name``
    registered against the specified ``context`` and ``request`` and
    return a :term:`response` object.  This function will return
    ``None`` if a corresponding :term:`view callable` cannot be found
    (when no :term:`view configuration` matches the combination of
    ``name`` / ``context`` / and ``request``).

    If `secure`` is ``True``, and the :term:`view callable` found is
    protected by a permission, the permission will be checked before
    calling the view function.  If the permission check disallows view
    execution (based on the current :term:`authorization policy`), a
    :exc:`repoze.bfg.exceptions.Forbidden` exception will be raised.
    The exception's ``args`` attribute explains why the view access
    was disallowed.

    If ``secure`` is ``False``, no permission checking is done."""
    provides = map(providedBy, (request, context))
    try:
        reg = request.registry
    except AttributeError:
        reg = get_current_registry()
    view = reg.adapters.lookup(provides, IView, name=name)
    if view is None:
        return None

    if not secure:
        # the view will have a __call_permissive__ attribute if it's
        # secured; otherwise it won't.
        view = getattr(view, '__call_permissive__', view)

    # if this view is secured, it will raise a Forbidden
    # appropriately if the executing user does not have the proper
    # permission
    return view(context, request)

def render_view_to_iterable(context, request, name='', secure=True):
    """ Call the :term:`view callable` configured with a :term:`view
    configuration` that matches the :term:`view name` ``name``
    registered against the specified ``context`` and ``request`` and
    return an iterable object which represents the body of a response.
    This function will return ``None`` if a corresponding :term:`view
    callable` cannot be found (when no :term:`view configuration`
    matches the combination of ``name`` / ``context`` / and
    ``request``).  Additionally, this function will raise a
    :exc:`ValueError` if a view function is found and called but the
    view function's result does not have an ``app_iter`` attribute.

    You can usually get the string representation of the return value
    of this function by calling ``''.join(iterable)``, or just use
    :func:`repoze.bfg.view.render_view` instead.

    If ``secure`` is ``True``, and the view is protected by a
    permission, the permission will be checked before the view
    function is invoked.  If the permission check disallows view
    execution (based on the current :term:`authentication policy`), a
    :exc:`repoze.bfg.exceptions.Forbidden` exception will be raised;
    its ``args`` attribute explains why the view access was
    disallowed.

    If ``secure`` is ``False``, no permission checking is
    done."""
    response = render_view_to_response(context, request, name, secure)
    if response is None:
        return None
    return response.app_iter

def render_view(context, request, name='', secure=True):
    """ Call the :term:`view callable` configured with a :term:`view
    configuration` that matches the :term:`view name` ``name``
    registered against the specified ``context`` and ``request``
    and unwind the view response's ``app_iter`` (see
    :ref:`the_response`) into a single string.  This function will
    return ``None`` if a corresponding :term:`view callable` cannot be
    found (when no :term:`view configuration` matches the combination
    of ``name`` / ``context`` / and ``request``).  Additionally, this
    function will raise a :exc:`ValueError` if a view function is
    found and called but the view function's result does not have an
    ``app_iter`` attribute. This function will return ``None`` if a
    corresponding view cannot be found.

    If ``secure`` is ``True``, and the view is protected by a
    permission, the permission will be checked before the view is
    invoked.  If the permission check disallows view execution (based
    on the current :term:`authorization policy`), a
    :exc:`repoze.bfg.exceptions.Forbidden` exception will be raised;
    its ``args`` attribute explains why the view access was
    disallowed.

    If ``secure`` is ``False``, no permission checking is done."""
    iterable = render_view_to_iterable(context, request, name, secure)
    if iterable is None:
        return None
    return ''.join(iterable)

def is_response(ob):
    """ Return ``True`` if ``ob`` implements the interface implied by
    :ref:`the_response`. ``False`` if not.

    .. note:: this isn't a true interface check (in Zope terms), it's a
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
    """ An instance of this class is a callable which can act as a
    :mod:`repoze.bfg` :term:`view callable`; this view will serve
    static files from a directory on disk based on the ``root_dir``
    you provide to its constructor.

    The directory may contain subdirectories (recursively); the static
    view implementation will descend into these directories as
    necessary based on the components of the URL in order to resolve a
    path into a response.

    You may pass an absolute or relative filesystem path or a
    :term:`resource specification` representing the directory
    containing static files as the ``root_dir`` argument to this
    class' constructor.

    If the ``root_dir`` path is relative, and the ``package_name``
    argument is ``None``, ``root_dir`` will be considered relative to
    the directory in which the Python file which *calls* ``static``
    resides.  If the ``package_name`` name argument is provided, and a
    relative ``root_dir`` is provided, the ``root_dir`` will be
    considered relative to the Python :term:`package` specified by
    ``package_name`` (a dotted path to a Python package).

    ``cache_max_age`` influences the ``Expires`` and ``Max-Age``
    response headers returned by the view (default is 3600 seconds or
    five minutes).

    .. note:: If the ``root_dir`` is relative to a :term:`package`, or
         is a :term:`resource specification` the :mod:`repoze.bfg`
         ``resource`` ZCML directive or
         :class:`repoze.bfg.configuration.Configurator` method can be
         used to override resources within the named ``root_dir``
         package-relative directory.  However, if the ``root_dir`` is
         absolute, the ``resource`` directive will not be able to
         override the resources it contains.  """
    
    def __init__(self, root_dir, cache_max_age=3600, package_name=None):
        # package_name is for bw compat; it is preferred to pass in a
        # package-relative path as root_dir
        # (e.g. ``anotherpackage:foo/static``).
        caller_package_name = caller_package().__name__
        package_name = package_name or caller_package_name
        package_name, root_dir = resolve_resource_spec(root_dir, package_name)
        if package_name is None:
            app = StaticURLParser(root_dir, cache_max_age=cache_max_age)
        else:
            app = PackageURLParser(
                package_name, root_dir, cache_max_age=cache_max_age)
        self.app = app

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
    """ A function, class or method :term:`decorator` which allows a
    developer to create view registrations nearer to a :term:`view
    callable` definition than use of :term:`ZCML` or :term:`imperative
    configuration` to do the same.

    For example, this code in a module ``views.py``::

      from models import MyModel

      @bfg_view(name='my_view', context=MyModel, permission='read',
                route_name='site1')
      def my_view(context, request):
          return 'OK'

    Might replace the following call to the
    :meth:`repoze.bfg.configuration.Configurator.add_view` method::

       import views
       import models
       config.add_view(views.my_view, context=models.MyModel, name='my_view',
                       permission='read', 'route_name='site1')

    Or might replace the following ZCML ``view`` declaration::

      <view
       for='.models.MyModel'
       view='.views.my_view'
       name='my_view'
       permission='read'
       route_name='site1'
       />

    The following arguments are supported as arguments to
    ``bfg_view``: ``context``, ``permission``, ``name``,
    ``request_type``, ``route_name``, ``request_method``,
    ``request_param``, ``containment``, ``xhr``, ``accept``,
    ``header`` and ``path_info``.

    If ``context`` is not supplied, the interface
    ``zope.interface.Interface`` (matching any context) is used.  An alias
    for ``context`` is ``for_``.

    If ``permission`` is not supplied, no permission is registered for
    this view (it's accessible by any caller).

    If ``name`` is not supplied, the empty string is used (implying
    the default view name).

    If ``attr`` is not supplied, ``None`` is used (implying the
    function itself if the view is a function, or the ``__call__``
    callable attribute if the view is a class).

    If ``renderer`` is not supplied, ``None`` is used (meaning that no
    renderer is associated with this view).

    If ``wrapper`` is not supplied, ``None`` is used (meaning that no
    view wrapper is associated with this view).

    If ``request_type`` is not supplied, the interface
    :class:`repoze.bfg.interfaces.IRequest` is used, implying the
    standard request interface type.

    If ``route_name`` is not supplied, the view configuration is
    considered to be made against a URL that doesn't match any defined
    :term:`route`.  The use of a ``route_name`` is an advanced
    feature, useful only if you're also using :term:`url dispatch`.

    If ``request_method`` is not supplied, this view will match a
    request with any HTTP ``REQUEST_METHOD``
    (GET/POST/PUT/HEAD/DELETE).  If this parameter *is* supplied, it
    must be a string naming an HTTP ``REQUEST_METHOD``, indicating
    that this view will only match when the current request has a
    ``REQUEST_METHOD`` that matches this value.

    If ``request_param`` is not supplied, this view will be called
    when a request with any (or no) request GET or POST parameters is
    encountered.  If the value is present, it must be a string.  If
    the value supplied to the parameter has no ``=`` sign in it, it
    implies that the key must exist in the ``request.params``
    dictionary for this view to 'match' the current request.  If the value
    supplied to the parameter has a ``=`` sign in it, e.g.
    ``request_params="foo=123"``, then the key (``foo``) must both exist
    in the ``request.params`` dictionary, and the value must match the
    right hand side of the expression (``123``) for the view to "match" the
    current request.

    If ``containment`` is not supplied, this view will be called when
    the context of the request has any (or no) :term:`lineage`.  If
    ``containment`` *is* supplied, it must be a class or
    :term:`interface`, denoting that the view 'matches' the current
    request only if any graph :term:`lineage` node possesses this
    class or interface.

    If ``xhr`` is specified, it must be a boolean value.  If the value
    is ``True``, the view will only be invoked if the request's
    ``X-Requested-With`` header has the value ``XMLHttpRequest``.

    If ``accept`` is specified, it must be a mimetype value.  If
    ``accept`` is specified, the view will only be invoked if the
    ``Accept`` HTTP header matches the value requested.  See the
    description of ``accept`` in :ref:`view_directive` for information
    about the allowable composition and matching behavior of this
    value.

    If ``header`` is specified, it must be a header name or a
    ``headername:headervalue`` pair.  If ``header`` is specified, and
    possesses a value the view will only be invoked if an HTTP header
    matches the value requested.  If ``header`` is specified without a
    value (a bare header name only), the view will only be invoked if
    the HTTP header exists with any value in the request.  See the
    description of ``header`` in :ref:`view_directive` for information
    about the allowable composition and matching behavior of this
    value.

    If ``path_info`` is specified, it must be a regular
    expression. The view will only be invoked if the ``PATH_INFO``
    WSGI environment variable matches the expression.

    If ``custom_predicates`` is specified, it must be a sequence of
    :term:`predicate` callables (a predicate callable accepts two
    arguments: ``context`` and ``request`` and returns ``True`` or
    ``False``).  The view will only be invoked if all custom
    predicates return ``True``.

    Any individual or all parameters can be omitted.  The simplest
    ``bfg_view`` declaration is::

        @bfg_view()
        def my_view(...):
            ...

    Such a registration implies that the view name will be
    ``my_view``, registered for any :term:`context` object, using no
    permission, registered against all non-URL-dispatch-based
    requests, with any ``REQUEST_METHOD``, any set of request.params
    values, without respect to any object in the :term:`lineage`.

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

    In Python 2.5 and below, the ``bfg_view`` decorator can still be
    used against a class, although not in decorator form::

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

    The bfg_view decorator can also be used against a class method::

        from webob import Response
        from repoze.bfg.view import bfg_view

        class MyView(object):
            def __init__(self, context, request):
                self.context = context
                self.request = request

            @bfg_view(name='hello')
            def amethod(self):
                return Response('hello from %s!' % self.context)

    When the ``bfg_view`` decorator is used against a class method, a
    view is registered for the *class* (as described above), so the
    class constructor must accept either ``request`` or ``context,
    request``.  The method which is decorated must return a response
    (or rely on a :term:`renderer` to generate one). Using the
    decorator against a particular method of a class is equivalent to
    using the ``attr`` parameter in a decorator attached to the class
    itself.  For example, the above registration implied by the
    decorator being used against the ``amethod`` method could be
    spelled equivalently as::

        from webob import Response
        from repoze.bfg.view import bfg_view

        @bfg_view(attr='amethod', name='hello')
        class MyView(object):
            def __init__(self, context, request):
                self.context = context
                self.request = request

            def amethod(self):
                return Response('hello from %s!' % self.context)

    .. warning:: The ability to use the ``bfg_view`` decorator as a
                 method decorator is new in :mod:`repoze.bfg` version
                 1.1.

    To make use of any ``bfg_view`` declaration, you must perform a
    :term:`scan`.  To do so, either insert the following boilerplate
    into your application registry's ZCML::
    
      <scan package="."/>

    See :ref:`scan_directive` for more information about the ZCML
    ``scan`` directive.

    Or, if you don't use ZCML, use the
    :meth:`repoze.bfg.configuration.Configurator.scan` method::

      config.scan()
    """
    def __init__(self, name='', request_type=None, for_=None, permission=None,
                 route_name=None, request_method=None, request_param=None,
                 containment=None, attr=None, renderer=None, wrapper=None,
                 xhr=False, accept=None, header=None, path_info=None,
                 custom_predicates=(), context=None):
        self.name = name
        self.request_type = request_type
        self.context = context or for_
        self.permission = permission
        self.route_name = route_name
        self.request_method = request_method
        self.request_param = request_param
        self.containment = containment
        self.attr = attr
        self.renderer = renderer
        self.wrapper = wrapper
        self.xhr = xhr
        self.accept = accept
        self.header = header
        self.path_info = path_info
        self.custom_predicates = custom_predicates

    def __call__(self, wrapped):
        setting = self.__dict__.copy()
        frame = sys._getframe(1)
        scope, module, f_locals, f_globals = getFrameInfo(frame)
        if scope == 'class':
            # we're in the midst of a class statement; the setdefault
            # below actually adds a __bfg_view_settings__ attr to the
            # class __dict__ if one does not already exist
            settings = f_locals.setdefault('__bfg_view_settings__', [])
            if setting['attr'] is None:
                setting['attr'] = wrapped.__name__
        else:
            settings = getattr(wrapped, '__bfg_view_settings__', [])
            wrapped.__bfg_view_settings__ = settings

        # try to convert the renderer provided into a fully qualified
        # resource specification
        abspath = setting.get('renderer')
        if abspath is not None and '.' in abspath:
            isabs = os.path.isabs(abspath)
            if not (':' in abspath and not isabs):
                # not already a resource spec
                if not isabs:
                    pp = package_path(module)
                    abspath = os.path.join(pp, abspath)
                resource = resource_spec_from_abspath(abspath, module)
                setting['renderer'] = resource

        settings.append(setting)
        return wrapped

def default_view(context, request, status):
    try:
        msg = cgi.escape(request.environ['repoze.bfg.message'])
    except KeyError:
        msg = ''
    html = """
    <html>
    <title>%s</title>
    <body>
    <h1>%s</h1>
    <code>%s</code>
    </body>
    </html>
    """ % (status, status, msg)
    headers = [('Content-Length', str(len(html))),
               ('Content-Type', 'text/html')]
    response_factory = Response
    registry = getattr(request, 'registry', None)
    if registry is not None:
        # be kind to old tests
        response_factory = registry.queryUtility(IResponseFactory,
                                                 default=Response)
    return response_factory(status = status,
                            headerlist = headers,
                            app_iter = [html])

def default_forbidden_view(context, request):
    return default_view(context, request, '401 Unauthorized')

def default_notfound_view(context, request):
    return default_view(context, request, '404 Not Found')

def append_slash_notfound_view(context, request):
    """For behavior like Django's ``APPEND_SLASH=True``, use this view
    as the :term:`Not Found view` in your application.

    When this view is the Not Found view (indicating that no view was
    found), and any routes have been defined in the configuration of
    your application, if the value of the ``PATH_INFO`` WSGI
    environment variable does not already end in a slash, and if the
    value of ``PATH_INFO`` *plus* a slash matches any route's path, do
    an HTTP redirect to the slash-appended PATH_INFO.  Note that this
    will *lose* ``POST`` data information (turning it into a GET), so
    you shouldn't rely on this to redirect POST requests.

    If you use :term:`ZCML`, add the following to your application's
    ``configure.zcml`` to use this view as the Not Found view::

      <notfound
         view="repoze.bfg.view.append_slash_notfound_view"/>

    Or use the
    :meth:`repoze.bfg.configuration.Configurator.set_notfound_view`
    method if you don't use ZCML::

      from repoze.bfg.view import append_slash_notfound_view
      config.set_notfound_view(append_slash_notfound_view)

    See also :ref:`changing_the_notfound_view`.

    .. note:: This function is new as of :mod:`repoze.bfg` version 1.1.

    """
    path = request.environ.get('PATH_INFO', '/')
    registry = request.registry
    mapper = registry.queryUtility(IRoutesMapper)
    if mapper is not None and not path.endswith('/'):
        slashpath = path + '/'
        for route in mapper.get_routes():
            if route.match(slashpath) is not None:
                return HTTPFound(location=slashpath)
    return default_view(context, request, '404 Not Found')

