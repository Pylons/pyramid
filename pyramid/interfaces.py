from zope.interface import Attribute
from zope.interface import Interface

# public API interfaces

class IContextFound(Interface):
    """ An event type that is emitted after :app:`Pyramid` finds a
    :term:`context` object but before it calls any view code.  See the
    documentation attached to :class:`pyramid.events.ContextFound`
    for more information.

    .. note:: For backwards compatibility with versions of
       :app:`Pyramid` before 1.0, this event interface can also be
       imported as :class:`pyramid.interfaces.IAfterTraversal`.
    """
    request = Attribute('The request object')

IAfterTraversal = IContextFound

class INewRequest(Interface):
    """ An event type that is emitted whenever :app:`Pyramid`
    begins to process a new request.  See the documentation attached
    to :class:`pyramid.events.NewRequest` for more information."""
    request = Attribute('The request object')
    
class INewResponse(Interface):
    """ An event type that is emitted whenever any :app:`Pyramid`
    view returns a response. See the
    documentation attached to :class:`pyramid.events.NewResponse`
    for more information."""
    request = Attribute('The request object')
    response = Attribute('The response object')

class IApplicationCreated(Interface):
    """ Event issued when the
    :meth:`pyramid.config.Configurator.make_wsgi_app` method
    is called.  See the documentation attached to
    :class:`pyramid.events.ApplicationCreated` for more
    information.

    .. note:: For backwards compatibility with :app:`Pyramid`
       versions before 1.0, this interface can also be imported as
       :class:`pyramid.interfaces.IWSGIApplicationCreatedEvent`.
    """
    app = Attribute(u"Created application")

IWSGIApplicationCreatedEvent = IApplicationCreated # b /c

class IResponse(Interface): # not an API
    status = Attribute('WSGI status code of response')
    headerlist = Attribute('List of response headers')
    app_iter = Attribute('Iterable representing the response body')

class IException(Interface): # not an API
    """ An interface representing a generic exception """

class IExceptionResponse(IException, IResponse):
    """ An interface representing a WSGI response which is also an
    exception object.  Register an exception view using this interface
    as a ``context`` to apply the registered view for all exception
    types raised by :app:`Pyramid` internally
    (:class:`pyramid.exceptions.NotFound` and
    :class:`pyramid.exceptions.Forbidden`)."""

class IBeforeRender(Interface):
    """
    Subscribers to this event may introspect the and modify the set of
    :term:`renderer globals` before they are passed to a :term:`renderer`.
    This event object iself has a dictionary-like interface that can be used
    for this purpose.  For example::

      from repoze.events import subscriber
      from pyramid.interfaces import IBeforeRender

      @subscriber(IBeforeRender)
      def add_global(event):
          event['mykey'] = 'foo'

    See also :ref:`beforerender_event`.
    """
    def __setitem__(name, value):
        """ Set a name/value pair into the dictionary which is passed to a
        renderer as the renderer globals dictionary.  If the ``name`` already
        exists in the target dictionary, a :exc:`KeyError` will be raised."""

    def update(d):
        """ Update the renderer globals dictionary with another dictionary
        ``d``.  If any of the key names in the source dictionary already exist
        in the target dictionary, a :exc:`KeyError` will be raised"""

    def __contains__(k):
        """ Return ``True`` if ``k`` exists in the renderer globals
        dictionary."""

    def __getitem__(k):
        """ Return the value for key ``k`` from the renderer globals
        dictionary."""

    def get(k, default=None):
        """ Return the value for key ``k`` from the renderer globals
        dictionary, or the default if no such value exists."""

class IRenderer(Interface):
    def __call__(value, system):
        """ Call a the renderer implementation with the result of the
        view (``value``) passed in and return a result (a string or
        unicode object useful as a response body).  Values computed by
        the system are passed by the system in the ``system``
        parameter, which is a dictionary.  Keys in the dictionary
        include: ``view`` (the view callable that returned the value),
        ``renderer_name`` (the template name or simple name of the
        renderer), ``context`` (the context object passed to the
        view), and ``request`` (the request object passed to the
        view)."""

class ITemplateRenderer(IRenderer):
    def implementation():
        """ Return the object that the underlying templating system
        uses to render the template; it is typically a callable that
        accepts arbitrary keyword arguments and returns a string or
        unicode object """

class IViewMapper(Interface):
    def __call__(self, object):
        """ Provided with an arbitrary object (a function, class, or
        instance), returns a callable with the call signature ``(context,
        request)``.  The callable returned should itself return a Response
        object.  An IViewMapper is returned by
        :class:`pyramid.interfaces.IViewMapperFactory`."""

class IViewMapperFactory(Interface):
    def __call__(self, **kw):
        """
        Return an object which implements
        :class:`pyramid.interfaces.IViewMapper`.  ``kw`` will be a dictionary
        containing view-specific arguments, such as ``permission``,
        ``predicates``, ``attr``, ``renderer``, and other items.  An
        IViewMapperFactory is used by
        :meth:`pyramid.config.Configurator.add_view` to provide a plugpoint
        to extension developers who want to modify potential view callable
        invocation signatures and response values.
        """

# internal interfaces

class IRequest(Interface):
    """ Request type interface attached to all request objects """

IRequest.combined = IRequest # for exception view lookups 

class IRouteRequest(Interface):
    """ *internal only* interface used as in a utility lookup to find
    route-specific interfaces.  Not an API."""

class IAuthenticationPolicy(Interface):
    """ An object representing a Pyramid authentication policy. """
    def authenticated_userid(request):
        """ Return the authenticated userid or ``None`` if no authenticated
        userid can be found. This method of the policy should ensure that a
        record exists in whatever persistent store is used related to the
        user (the user should not have been deleted); if a record associated
        with the current id does not exist in a persistent store, it should
        return ``None``."""

    def unauthenticated_userid(request):
        """ Return the *unauthenticated* userid.  This method performs the
        same duty as ``authenticated_userid`` but is permitted to return the
        userid based only on data present in the request; it needn't (and
        shouldn't) check any persistent store to ensure that the user record
        related to the request userid exists."""

    def effective_principals(request):
        """ Return a sequence representing the effective principals
        including the userid and any groups belonged to by the current
        user, including 'system' groups such as Everyone and
        Authenticated. """

    def remember(request, principal, **kw):
        """ Return a set of headers suitable for 'remembering' the
        principal named ``principal`` when set in a response.  An
        individual authentication policy and its consumers can decide
        on the composition and meaning of **kw. """
    
    def forget(request):
        """ Return a set of headers suitable for 'forgetting' the
        current user on subsequent requests. """

class IAuthorizationPolicy(Interface):
    """ An object representing a Pyramid authorization policy. """
    def permits(context, principals, permission):
        """ Return ``True`` if any of the ``principals`` is allowed the
        ``permission`` in the current ``context``, else return ``False``
        """
        
    def principals_allowed_by_permission(context, permission):
        """ Return a set of principal identifiers allowed by the
        ``permission`` in ``context``.  This behavior is optional; if you
        choose to not implement it you should define this method as
        something which raises a ``NotImplementedError``.  This method
        will only be called when the
        ``pyramid.security.principals_allowed_by_permission`` API is
        used."""

class IStaticURLInfo(Interface):
    """ A policy for generating URLs to static assets """
    def add(name, spec, **extra):
        """ Add a new static info registration """

    def generate(path, request, **kw):
        """ Generate a URL for the given path """

class IResponseFactory(Interface):
    """ A utility which generates a response factory """
    def __call__():
        """ Return a response factory (e.g. a callable that returns an object
        implementing IResponse, e.g. :class:`pyramid.response.Response`). It
        should accept all the arguments that the Pyramid Response class
        accepts."""

class IRequestFactory(Interface):
    """ A utility which generates a request """
    def __call__(environ):
        """ Return an object implementing IRequest, e.g. an instance
        of ``pyramid.request.Request``"""

    def blank(path):
        """ Return an empty request object (see
        :meth:`pyramid.request.Request.blank`)"""

class IViewClassifier(Interface):
    """ *Internal only* marker interface for views."""

class IExceptionViewClassifier(Interface):
    """ *Internal only* marker interface for exception views."""

class IView(Interface):
    def __call__(context, request):
        """ Must return an object that implements IResponse.  May
        optionally raise ``pyramid.exceptions.Forbidden`` if an
        authorization failure is detected during view execution or
        ``pyramid.exceptions.NotFound`` if the not found page is
        meant to be returned."""

class ISecuredView(IView):
    """ *Internal only* interface.  Not an API. """
    def __call_permissive__(context, request):
        """ Guaranteed-permissive version of __call__ """

    def __permitted__(context, request):
        """ Return True if view execution will be permitted using the
        context and request, False otherwise"""

class IMultiView(ISecuredView):
    """ *internal only*.  A multiview is a secured view that is a
    collection of other views.  Each of the views is associated with
    zero or more predicates.  Not an API."""
    def add(view, predicates, order, accept=None, phash=None):
        """ Add a view to the multiview. """

class IRootFactory(Interface):
    def __call__(request):
        """ Return a root object based on the request """

class IDefaultRootFactory(Interface):
    def __call__(request):
        """ Return the *default* root object for an application """

class ITraverser(Interface):
    def __call__(request):
        """ Return a dictionary with (at least) the keys ``root``,
        ``context``, ``view_name``, ``subpath``, ``traversed``,
        ``virtual_root``, and ``virtual_root_path``.  These values are
        typically the result of an object graph traversal.  ``root``
        is the physical root object, ``context`` will be a model
        object, ``view_name`` will be the view name used (a Unicode
        name), ``subpath`` will be a sequence of Unicode names that
        followed the view name but were not traversed, ``traversed``
        will be a sequence of Unicode names that were traversed
        (including the virtual root path, if any) ``virtual_root``
        will be a model object representing the virtual root (or the
        physical root if traversal was not performed), and
        ``virtual_root_path`` will be a sequence representing the
        virtual root path (a sequence of Unicode names) or None if
        traversal was not performed.

        Extra keys for special purpose functionality can be added as
        necessary.

        All values returned in the dictionary will be made available
        as attributes of the ``request`` object.
        """

ITraverserFactory = ITraverser # b / c for 1.0 code

class IRendererFactory(Interface):
    def __call__(name):
        """ Return an object that implements ``IRenderer``  """

class IRendererGlobalsFactory(Interface):
    def __call__(system_values):
        """ Return a dictionary of global renderer values (aka
        top-level template names).  The ``system_values`` value passed
        in will be a dictionary that includes at least a ``request``
        key, indicating the current request, and the value
        ``renderer_name``, which will be the name of the renderer in
        use."""

class IViewPermission(Interface):
    def __call__(context, request):
        """ Return True if the permission allows, return False if it denies. """

class IRouter(Interface):
    """WSGI application which routes requests to 'view' code based on
    a view registry."""
    registry = Attribute(
        """Component architecture registry local to this application.""")
    
class ISettings(Interface):
    """ Runtime settings utility for pyramid; represents the
    deployment settings for the application.  Implements a mapping
    interface."""
    
# this interface, even if it becomes unused within Pyramid, is
# imported by other packages (such as traversalwrapper)
class ILocation(Interface):
    """Objects that have a structural location"""
    __parent__ = Attribute("The parent in the location hierarchy")
    __name__ = Attribute("The name within the parent")

class IDebugLogger(Interface):
    """ Interface representing a PEP 282 logger """

ILogger = IDebugLogger # b/c

class IRoutePregenerator(Interface):
    def __call__(request, elements, kw):
        """ A pregenerator is a function associated by a developer
        with a :term:`route`. The pregenerator for a route is called
        by :func:`pyramid.url.route_url` in order to adjust the set
        of arguments passed to it by the user for special purposes,
        such as Pylons 'subdomain' support.  It will influence the URL
        returned by ``route_url``.

        A pregenerator should return a two-tuple of ``(elements, kw)``
        after examining the originals passed to this function, which
        are the arguments ``(request, elements, kw)``.  The simplest
        pregenerator is::

            def pregenerator(request, elements, kw):
                return elements, kw

        You can employ a pregenerator by passing a ``pregenerator``
        argument to the
        :meth:`pyramid.config.Configurator.add_route`
        function.

        """

class IRoute(Interface):
    """ Interface representing the type of object returned from
    ``IRoutesMapper.get_route``"""
    name = Attribute('The route name')
    pattern = Attribute('The route pattern')
    factory = Attribute(
        'The :term:`root factory` used by the :app:`Pyramid` router '
        'when this route matches (or ``None``)')
    predicates = Attribute(
        'A sequence of :term:`route predicate` objects used to '
        'determine if a request matches this route or not or not after '
        'basic pattern matching has been completed.')
    pregenerator = Attribute('This attribute should either be ``None`` or '
                             'a callable object implementing the '
                             '``IRoutePregenerator`` interface')
    def match(path):
        """
        If the ``path`` passed to this function can be matched by the
        ``pattern`` of this route, return a dictionary (the
        'matchdict'), which will contain keys representing the dynamic
        segment markers in the pattern mapped to values extracted from
        the provided ``path``.

        If the ``path`` passed to this function cannot be matched by
        the ``pattern`` of this route, return ``None``.
        """
    def generate(kw):
        """
        Generate a URL based on filling in the dynamic segment markers
        in the pattern using the ``kw`` dictionary provided.
        """

class IRoutesMapper(Interface):
    """ Interface representing a Routes ``Mapper`` object """
    def get_routes():
        """ Return a sequence of Route objects registered in the mapper."""

    def has_routes():
        """ Returns ``True`` if any route has been registered. """

    def get_route(name):
        """ Returns an ``IRoute`` object if a route with the name ``name``
        was registered, otherwise return ``None``."""

    def connect(name, pattern, factory=None, predicates=()):
        """ Add a new route. """

    def generate(name, kw):
        """ Generate a URL using the route named ``name`` with the
        keywords implied by kw"""

    def __call__(request):
        """ Return a dictionary containing matching information for
        the request; the ``route`` key of this dictionary will either
        be a Route object or ``None`` if no route matched; the
        ``match`` key will be the matchdict or ``None`` if no route
        matched."""

class IContextURL(Interface):
    """ An adapter which deals with URLs related to a context.
    """
    def virtual_root():
        """ Return the virtual root related to a request and the
        current context"""

    def __call__():
        """ Return a URL that points to the context """

class IPackageOverrides(Interface):
    """ Utility for pkg_resources overrides """

# VH_ROOT_KEY is an interface; its imported from other packages (e.g.
# traversalwrapper)
VH_ROOT_KEY = 'HTTP_X_VHM_ROOT'

class IChameleonLookup(Interface):
    translate = Attribute('IChameleonTranslate object')
    debug = Attribute('The ``debug_templates`` setting for this application')
    auto_reload = Attribute('The ``reload_templates`` setting for this app')
    def __call__(self, info):
        """ Return an ITemplateRenderer based on IRendererInfo ``info`` """

class IChameleonTranslate(Interface):
    """ Internal interface representing a chameleon translate function """
    def __call__(msgid, domain=None, mapping=None, context=None,
                 target_language=None, default=None):
        """ Translate a mess of arguments to a Unicode object """

class ILocalizer(Interface):
    """ Localizer for a specific language """
        
class ILocaleNegotiator(Interface):
    def __call__(request):
        """ Return a locale name """

class ITranslationDirectories(Interface):
    """ A list object representing all known translation directories
    for an application"""

class IDefaultPermission(Interface):
    """ A string object representing the default permission to be used
    for all view configurations which do not explicitly declare their
    own."""

class ISessionFactory(Interface):
    """ An interface representing a factory which accepts a request object and
    returns an ISession object """
    def __call__(request):
        """ Return an ISession object """

class ISession(Interface):
    """ An interface representing a session (a web session object,
    usually accessed via ``request.session``.

    Keys and values of a session must be pickleable.
    """

    # attributes

    created = Attribute('Integer representing Epoch time when created.')
    new = Attribute('Boolean attribute.  If ``True``, the session is new.')

    # special methods

    def invalidate():
        """ Invalidate the session.  The action caused by
        ``invalidate`` is implementation-dependent, but it should have
        the effect of completely dissociating any data stored in the
        session with the current request.  It might set response
        values (such as one which clears a cookie), or it might not."""

    def changed():
        """ Mark the session as changed. A user of a session should
        call this method after he or she mutates a mutable object that
        is *a value of the session* (it should not be required after
        mutating the session itself).  For example, if the user has
        stored a dictionary in the session under the key ``foo``, and
        he or she does ``session['foo'] = {}``, ``changed()`` needn't
        be called.  However, if subsequently he or she does
        ``session['foo']['a'] = 1``, ``changed()`` must be called for
        the sessioning machinery to notice the mutation of the
        internal dictionary."""

    def flash(msg, queue='', allow_duplicate=True):
        """ Push a flash message onto the end of the flash queue represented
        by ``queue``.  An alternate flash message queue can used by passing
        an optional ``queue``, which must be a string.  If
        ``allow_duplicate`` is false, if the ``msg`` already exists in the
        queue, it will not be readded."""

    def pop_flash(queue=''):
        """ Pop a queue from the flash storage.  The queue is removed from
        flash storage after this message is called.  The queue is returned;
        it is a list of flash messages added by
        :meth:`pyramid.interfaces.ISesssion.flash`"""

    def peek_flash(queue=''):
        """ Peek at a queue in the flash storage.  The queue remains in
        flash storage after this message is called.  The queue is returned;
        it is a list of flash messages added by
        :meth:`pyramid.interfaces.ISesssion.flash`
        """

    def new_csrf_token():
        """ Create and set into the session a new, random cross-site request
        forgery protection token.  Return the token.  It will be a string."""

    def get_csrf_token():
        """ Return a random cross-site request forgery protection token.  It
        will be a string.  If a token was previously added to the session via
        ``new_csrf_token``, that token will be returned.  If no CSRF token
        was previously set into the session, ``new_csrf_token`` will be
        called, which will create and set a token, and this token will be
        returned.
        """

    # mapping methods
    
    def __getitem__(key):
        """Get a value for a key

        A ``KeyError`` is raised if there is no value for the key.
        """

    def get(key, default=None):
        """Get a value for a key

        The default is returned if there is no value for the key.
        """

    def __delitem__(key):
        """Delete a value from the mapping using the key.

        A ``KeyError`` is raised if there is no value for the key.
        """

    def __setitem__(key, value):
        """Set a new item in the mapping."""

    def keys():
        """Return the keys of the mapping object.
        """

    def values():
        """Return the values of the mapping object.
        """

    def items():
        """Return the items of the mapping object.
        """

    def iterkeys():
        "iterate over keys; equivalent to __iter__"

    def itervalues():
        "iterate over values"

    def iteritems():
        "iterate over items"

    def clear():
        "delete all items"
    
    def update(d):
        " Update D from E: for k in E.keys(): D[k] = E[k]"
    
    def setdefault(key, default=None):
        " D.setdefault(k[,d]) -> D.get(k,d), also set D[k]=d if k not in D "
    
    def pop(k, *args):
        """remove specified key and return the corresponding value
        ``*args`` may contain a single default value, or may not be supplied.
        If key is not found, default is returned if given, otherwise 
        ``KeyError`` is raised"""
    
    def popitem():
        """remove and return some (key, value) pair as a
        2-tuple; but raise ``KeyError`` if mapping is empty"""

    def __len__():
        """Return the number of items in the session.
        """

    def __iter__():
        """Return an iterator for the keys of the mapping object.
        """

    def __contains__(key):
        """Return true if a key exists in the mapping."""

NO_PERMISSION_REQUIRED = '__no_permission_required__'

class IRendererInfo(Interface):
    """ An object implementing this interface is passed to every
    :term:`renderer factory` constructor as its only argument (conventionally
    named ``info``)"""
    name = Attribute('The value passed by the user as the renderer name')
    package = Attribute('The "current package" when the renderer '
                        'configuration statement was found')
    type = Attribute('The renderer type name')
    registry = Attribute('The "current" application registry when the '
                         'renderer was created')
    settings = Attribute('The deployment settings dictionary related '
                         'to the current application')
    

