import mimetypes

# See http://bugs.python.org/issue5853 which is a recursion bug
# that seems to effect Python 2.6, Python 2.6.1, and 2.6.2 (a fix
# has been applied on the Python 2 trunk).  This workaround should
# really be in Paste if anywhere, but it's easiest to just do it
# here and get it over with to avoid needing to deal with any
# fallout.

if hasattr(mimetypes, 'init'):
    mimetypes.init()

import venusian

from zope.interface import providedBy
from zope.deprecation import deprecated

from pyramid.interfaces import IRoutesMapper
from pyramid.interfaces import IView
from pyramid.interfaces import IViewClassifier

from pyramid.httpexceptions import HTTPFound
from pyramid.renderers import RendererHelper
from pyramid.static import static_view
from pyramid.threadlocal import get_current_registry

# Nast BW compat hack: dont yet deprecate this (ever?)
class static(static_view): # only subclass for purposes of autodoc
    __doc__ = static_view.__doc__

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
    :exc:`pyramid.exceptions.Forbidden` exception will be raised.
    The exception's ``args`` attribute explains why the view access
    was disallowed.

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

    If ``secure`` is ``True``, and the view is protected by a
    permission, the permission will be checked before the view
    function is invoked.  If the permission check disallows view
    execution (based on the current :term:`authentication policy`), a
    :exc:`pyramid.exceptions.Forbidden` exception will be raised;
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
    :exc:`pyramid.exceptions.Forbidden` exception will be raised;
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

    .. note:: This isn't a true interface or subclass check.  Instead, it's a
        duck-typing check, as response objects are not obligated to be of a
        particular class or provide any particular Zope interface."""

    # response objects aren't obligated to implement a Zope interface,
    # so we do it the hard way
    if ( hasattr(ob, 'app_iter') and hasattr(ob, 'headerlist') and
         hasattr(ob, 'status') ):
        return True
    return False

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

    The following arguments are supported as arguments to
    :class:`pyramid.view.view_config`: ``context``, ``permission``, ``name``,
    ``request_type``, ``route_name``, ``request_method``, ``request_param``,
    ``containment``, ``xhr``, ``accept``, ``header``, ``path_info``,
    ``custom_predicates``, ``decorator``, and ``mapper``.

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
                 mapper=None):
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

    def __call__(self, wrapped):
        settings = self.__dict__.copy()

        def callback(context, name, ob):
            renderer = settings.get('renderer')
            if isinstance(renderer, basestring):
                renderer = RendererHelper(name=renderer,
                                          package=info.module,
                                          registry=context.config.registry)
            settings['renderer'] = renderer
            context.config.add_view(view=ob, **settings)

        info = self.venusian.attach(wrapped, callback, category='pyramid')

        if info.scope == 'class':
            # if the decorator was attached to a method in a class, or
            # otherwise executed at class scope, we need to set an
            # 'attr' into the settings if one isn't already in there
            if settings['attr'] is None:
                settings['attr'] = wrapped.__name__

        settings['_info'] = info.codeinfo
        return wrapped

bfg_view = view_config # permanent b/c

deprecated(
    'bfg_view',
    'pyramid.view.bfg_view is deprecated as of Pyramid 1.0.  Use '
    'pyramid.view.view_config instead (API-compat, simple '
    'rename).')

def default_exceptionresponse_view(context, request):
    if not isinstance(context, Exception):
        # backwards compat for an exception response view registered via
        # config.set_notfound_view or config.set_forbidden_view
        # instead of as a proper exception view
        context = request.exception or context
    return context

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

       from pyramid.exceptions import NotFound
       from pyramid.view import AppendSlashNotFoundViewFactory

       def notfound_view(context, request):
           return HTTPNotFound('It aint there, stop trying!')

       custom_append_slash = AppendSlashNotFoundViewFactory(notfound_view)
       config.add_view(custom_append_slash, context=NotFound)

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
            context = request.exception
        path = request.environ.get('PATH_INFO', '/')
        registry = request.registry
        mapper = registry.queryUtility(IRoutesMapper)
        if mapper is not None and not path.endswith('/'):
            slashpath = path + '/'
            for route in mapper.get_routes():
                if route.match(slashpath) is not None:
                    if request.environ.get('QUERY_STRING'):
                        slashpath += '?' + request.environ['QUERY_STRING']
                    return HTTPFound(location=slashpath)
        return self.notfound_view(context, request)

append_slash_notfound_view = AppendSlashNotFoundViewFactory()
append_slash_notfound_view.__doc__ = """\
For behavior like Django's ``APPEND_SLASH=True``, use this view as the
:term:`Not Found view` in your application.

When this view is the Not Found view (indicating that no view was
found), and any routes have been defined in the configuration of your
application, if the value of the ``PATH_INFO`` WSGI environment
variable does not already end in a slash, and if the value of
``PATH_INFO`` *plus* a slash matches any route's path, do an HTTP
redirect to the slash-appended PATH_INFO.  Note that this will *lose*
``POST`` data information (turning it into a GET), so you shouldn't
rely on this to redirect POST requests.

Use the :meth:`pyramid.config.Configurator.add_view` method to configure this
view as the Not Found view::

  from pyramid.exceptions import NotFound
  from pyramid.view import append_slash_notfound_view
  config.add_view(append_slash_notfound_view, context=NotFound)

See also :ref:`changing_the_notfound_view`.

"""


