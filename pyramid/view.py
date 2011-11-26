import venusian

from zope.interface import providedBy
from zope.deprecation import deprecated

from pyramid.interfaces import IRoutesMapper
from pyramid.interfaces import IView
from pyramid.interfaces import IViewClassifier

from pyramid.httpexceptions import HTTPFound
from pyramid.httpexceptions import default_exceptionresponse_view
from pyramid.path import caller_package
from pyramid.static import static_view
from pyramid.threadlocal import get_current_registry

_marker = object()

class static(static_view):
    """ Backwards compatibility alias for
    :class:`pyramid.static.static_view`; it overrides that class' constructor
    to pass ``use_subpath=True`` by default.  This class is deprecated as of
    :app:`Pyramid` 1.1.  Use :class:`pyramid.static.static_view` instead
    (probably with a ``use_subpath=True`` argument).
    """
    def __init__(self, root_dir, cache_max_age=3600, package_name=None):
        if package_name is None:
            package_name = caller_package().__name__
        static_view.__init__(self, root_dir, cache_max_age=cache_max_age,
                             package_name=package_name, use_subpath=True)

deprecated(
    'static',
    'The "pyramid.view.static" class is deprecated as of Pyramid 1.1; '
    'use the "pyramid.static.static_view" class instead with the '
    '"use_subpath" argument set to True.')

def render_view_to_response(context, request, name='', secure=True):
    """ Call the :term:`view callable` configured with a :term:`view
    configuration` that matches the :term:`view name` ``name``
    registered against the specified ``context`` and ``request`` and
    return a :term:`response` object.  This function will return
    ``None`` if a corresponding :term:`view callable` cannot be found
    (when no :term:`view configuration` matches the combination of
    ``name`` / ``context`` / and ``request``).

    If `secure`` is ``True``, and the :term:`view callable` found is
    protected by a permission, the permission will be checked before calling
    the view function.  If the permission check disallows view execution
    (based on the current :term:`authorization policy`), a
    :exc:`pyramid.httpexceptions.HTTPForbidden` exception will be raised.
    The exception's ``args`` attribute explains why the view access was
    disallowed.

    If ``secure`` is ``False``, no permission checking is done."""
    provides = [IViewClassifier] + map(providedBy, (request, context))
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
    :func:`pyramid.view.render_view` instead.

    If ``secure`` is ``True``, and the view is protected by a permission, the
    permission will be checked before the view function is invoked.  If the
    permission check disallows view execution (based on the current
    :term:`authentication policy`), a
    :exc:`pyramid.httpexceptions.HTTPForbidden` exception will be raised; its
    ``args`` attribute explains why the view access was disallowed.

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

    If ``secure`` is ``True``, and the view is protected by a permission, the
    permission will be checked before the view is invoked.  If the permission
    check disallows view execution (based on the current :term:`authorization
    policy`), a :exc:`pyramid.httpexceptions.HTTPForbidden` exception will be
    raised; its ``args`` attribute explains why the view access was
    disallowed.

    If ``secure`` is ``False``, no permission checking is done."""
    iterable = render_view_to_iterable(context, request, name, secure)
    if iterable is None:
        return None
    return ''.join(iterable)

class view_config(object):
    """ A function, class or method :term:`decorator` which allows a
    developer to create view registrations nearer to a :term:`view
    callable` definition than use :term:`imperative
    configuration` to do the same.

    For example, this code in a module ``views.py``::

      from resources import MyResource

      @view_config(name='my_view', context=MyResource, permission='read',
                   route_name='site1')
      def my_view(context, request):
          return 'OK'

    Might replace the following call to the
    :meth:`pyramid.config.Configurator.add_view` method::

       import views
       from resources import MyResource
       config.add_view(views.my_view, context=MyResource, name='my_view',
                       permission='read', 'route_name='site1')

    .. note: :class:`pyramid.view.view_config` is also importable, for
             backwards compatibility purposes, as the name
             :class:`pyramid.view.bfg_view`.

    The following arguments are supported to
    :class:`pyramid.view.view_config`: ``context``, ``permission``, ``name``,
    ``request_type``, ``route_name``, ``request_method``, ``request_param``,
    ``containment``, ``xhr``, ``accept``, ``header``, ``path_info``,
    ``custom_predicates``, ``decorator``, ``mapper``, ``http_cache``,
    and ``match_param``.

    The meanings of these arguments are the same as the arguments passed to
    :meth:`pyramid.config.Configurator.add_view`.

    See :ref:`mapping_views_using_a_decorator_section` for details about
    using :class:`view_config`.

    """
    venusian = venusian # for testing injection
    def __init__(self, name='', request_type=None, for_=None, permission=None,
                 route_name=None, request_method=None, request_param=None,
                 containment=None, attr=None, renderer=None, wrapper=None,
                 xhr=False, accept=None, header=None, path_info=None,
                 custom_predicates=(), context=None, decorator=None,
                 mapper=None, http_cache=None, match_param=None):
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
        self.decorator = decorator
        self.mapper = mapper
        self.http_cache = http_cache
        self.match_param = match_param

    def __call__(self, wrapped):
        settings = self.__dict__.copy()

        def callback(context, name, ob):
            config = context.config.with_package(info.module)
            config.add_view(view=ob, **settings)

        info = self.venusian.attach(wrapped, callback, category='pyramid')

        if info.scope == 'class':
            # if the decorator was attached to a method in a class, or
            # otherwise executed at class scope, we need to set an
            # 'attr' into the settings if one isn't already in there
            if settings['attr'] is None:
                settings['attr'] = wrapped.__name__

        settings['_info'] = info.codeinfo # fbo "action_method"
        return wrapped

bfg_view = view_config # bw compat (forever)

class AppendSlashNotFoundViewFactory(object):
    """ There can only be one :term:`Not Found view` in any
    :app:`Pyramid` application.  Even if you use
    :func:`pyramid.view.append_slash_notfound_view` as the Not
    Found view, :app:`Pyramid` still must generate a ``404 Not
    Found`` response when it cannot redirect to a slash-appended URL;
    this not found response will be visible to site users.

    If you don't care what this 404 response looks like, and you only
    need redirections to slash-appended route URLs, you may use the
    :func:`pyramid.view.append_slash_notfound_view` object as the
    Not Found view.  However, if you wish to use a *custom* notfound
    view callable when a URL cannot be redirected to a slash-appended
    URL, you may wish to use an instance of this class as the Not
    Found view, supplying a :term:`view callable` to be used as the
    custom notfound view as the first argument to its constructor.
    For instance:

    .. code-block:: python

       from pyramid.httpexceptions import HTTPNotFound
       from pyramid.view import AppendSlashNotFoundViewFactory

       def notfound_view(context, request): return HTTPNotFound('nope')

       custom_append_slash = AppendSlashNotFoundViewFactory(notfound_view)
       config.add_view(custom_append_slash, context=HTTPNotFound)

    The ``notfound_view`` supplied must adhere to the two-argument
    view callable calling convention of ``(context, request)``
    (``context`` will be the exception object).

    """
    def __init__(self, notfound_view=None):
        if notfound_view is None:
            notfound_view = default_exceptionresponse_view
        self.notfound_view = notfound_view

    def __call__(self, context, request):
        if not isinstance(context, Exception):
            # backwards compat for an append_notslash_view registered via
            # config.set_notfound_view instead of as a proper exception view
            context = getattr(request, 'exception', None) or context
        path = request.path
        registry = request.registry
        mapper = registry.queryUtility(IRoutesMapper)
        if mapper is not None and not path.endswith('/'):
            slashpath = path + '/'
            for route in mapper.get_routes():
                if route.match(slashpath) is not None:
                    qs = request.query_string
                    if qs:
                        slashpath += '?' + qs
                    return HTTPFound(location=slashpath)
        return self.notfound_view(context, request)

append_slash_notfound_view = AppendSlashNotFoundViewFactory()
append_slash_notfound_view.__doc__ = """\
For behavior like Django's ``APPEND_SLASH=True``, use this view as the
:term:`Not Found view` in your application.

When this view is the Not Found view (indicating that no view was found), and
any routes have been defined in the configuration of your application, if the
value of the ``PATH_INFO`` WSGI environment variable does not already end in
a slash, and if the value of ``PATH_INFO`` *plus* a slash matches any route's
path, do an HTTP redirect to the slash-appended PATH_INFO.  Note that this
will *lose* ``POST`` data information (turning it into a GET), so you
shouldn't rely on this to redirect POST requests.  Note also that static
routes are not considered when attempting to find a matching route.

Use the :meth:`pyramid.config.Configurator.add_view` method to configure this
view as the Not Found view::

  from pyramid.httpexceptions import HTTPNotFound
  from pyramid.view import append_slash_notfound_view
  config.add_view(append_slash_notfound_view, context=HTTPNotFound)

See also :ref:`changing_the_notfound_view`.

"""

def is_response(ob):
    """ Return ``True`` if ``ob`` implements the interface implied by
    :ref:`the_response`. ``False`` if not.

    .. warning::

       This function is deprecated as of :app:`Pyramid` 1.1.  New
       code should not use it.  Instead, new code should use the
       :func:`pyramid.request.Request.is_response` method."""
    if ( hasattr(ob, 'app_iter') and hasattr(ob, 'headerlist') and
         hasattr(ob, 'status') ):
        return True
    return False

deprecated(
    'is_response',
    'pyramid.view.is_response is deprecated as of Pyramid 1.1.  Use '
    'pyramid.request.Request.is_response instead.')
