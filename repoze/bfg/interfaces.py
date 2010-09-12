from zope.interface import Attribute
from zope.interface import Interface

# public API interfaces

class IContextFound(Interface):
    """ An event type that is emitted after :mod:`repoze.bfg` finds a
    :term:`context` object but before it calls any view code.  See the
    documentation attached to :class:`repoze.bfg.events.ContextFound`
    for more information.

    .. note:: For backwards compatibility with versions of
       :mod:`repoze.bfg` before 1.3, this event interface can also be
       imported as :class:`repoze.bfg.interfaces.IAfterTraversal`.
    """
    request = Attribute('The request object')

IAfterTraversal = IContextFound

class INewRequest(Interface):
    """ An event type that is emitted whenever :mod:`repoze.bfg`
    begins to process a new request.  See the documentation attached
    to :class:`repoze.bfg.events.NewRequest` for more information."""
    request = Attribute('The request object')
    
class INewResponse(Interface):
    """ An event type that is emitted whenever any :mod:`repoze.bfg`
    view returns a response. See the
    documentation attached to :class:`repoze.bfg.events.NewResponse`
    for more information."""
    request = Attribute('The request object')
    response = Attribute('The response object')

class IApplicationCreated(Interface):
    """ Event issued when the
    :meth:`repoze.bfg.configuration.Configurator.make_wsgi_app` method
    is called.  See the documentation attached to
    :class:`repoze.bfg.events.ApplicationCreated` for more
    information.

    .. note:: For backwards compatibility with :mod:`repoze.bfg`
       versions before 1.3, this interface can also be imported as
       :class:`repoze.bfg.interfaces.IWSGIApplicationCreatedEvent.
    """
    app = Attribute(u"Published application")

class IFinishedRequest(Interface):
    """
    This :term:`event` is sent after all request processing is
    finished.  See the
    documentation attached to :class:`repoze.bfg.events.FinishedRequest`
    for more information.

    .. note:: This event type is new as of :mod:`repoze.bfg` 1.3.
    """
    request = Attribute('The request object')

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
    types raised by :mod:`repoze.bfg` internally
    (:class:`repoze.bfg.exceptions.NotFound` and
    :class:`repoze.bfg.exceptions.Forbidden`)."""

# internal interfaces

class IRequest(Interface):
    """ Request type interface attached to all request objects """

IRequest.combined = IRequest # for exception view lookups 

class IRouteRequest(Interface):
    """ *internal only* interface used as in a utility lookup to find
    route-specific interfaces.  Not an API."""

class IAuthenticationPolicy(Interface):
    """ An object representing a BFG authentication policy. """
    def authenticated_userid(request):
        """ Return the authenticated userid or ``None`` if no
        authenticated userid can be found. """

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
    """ An object representing a BFG authorization policy. """
    def permits(context, principals, permission):
        """ Return True if any of the principals is allowed the
        permission in the current context, else return False """
        
    def principals_allowed_by_permission(context, permission):
        """ Return a set of principal identifiers allowed by the permission """

class IStaticURLInfo(Interface):
    """ A policy for generating URLs to static resources """
    def add(name, spec, **extra):
        """ Add a new static info registration """

    def generate(path, request, **kw):
        """ Generate a URL for the given path """

class IResponseFactory(Interface):
    """ A utility which generates a response factory """
    def __call__():
        """ Return a response factory (e.g. a callable that returns an
        object implementing IResponse, e.g. ``webob.Response``; it
        should accept all the arguments that the webob.Response class
        accepts)"""

class IRequestFactory(Interface):
    """ A utility which generates a request """
    def __call__(environ):
        """ Return an object implementing IRequest, e.g. an instance
        of ``repoze.bfg.request.Request``"""

    def blank(path):
        """ Return an empty request object (see
        ``webob.Request.blank``)"""

class IViewClassifier(Interface):
    """ *Internal only* marker interface for views."""

class IExceptionViewClassifier(Interface):
    """ *Internal only* marker interface for exception views."""

class IView(Interface):
    def __call__(context, request):
        """ Must return an object that implements IResponse.  May
        optionally raise ``repoze.bfg.exceptions.Forbidden`` if an
        authorization failure is detected during view execution or
        ``repoze.bfg.exceptions.NotFound`` if the not found page is
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

class ITemplateRenderer(IRenderer):
    def implementation():
        """ Return the object that the underlying templating system
        uses to render the template; it is typically a callable that
        accepts arbitrary keyword arguments and returns a string or
        unicode object """

class IViewPermission(Interface):
    def __call__(context, request):
        """ Return True if the permission allows, return False if it denies. """

class IRouter(Interface):
    """WSGI application which routes requests to 'view' code based on
    a view registry."""
    registry = Attribute(
        """Component architecture registry local to this application.""")
    
class ISettings(Interface):
    """ Runtime settings utility for repoze.bfg; represents the
    deployment settings for the application.  Implements a mapping
    interface."""
    
# this interface, even if it becomes unused within BFG, is imported by
# other packages (such as repoze.bfg.traversalwrapper)
class ILocation(Interface):
    """Objects that have a structural location"""
    __parent__ = Attribute("The parent in the location hierarchy")
    __name__ = Attribute("The name within the parent")

class IDebugLogger(Interface):
    """ Interface representing a PEP 282 logger """

ILogger = IDebugLogger # b/c

class IRoute(Interface):
    """ Interface representing the type of object returned from
    ``IRoutesMapper.get_route``"""
    name = Attribute('The route name')
    pattern = Attribute('The route pattern')
    factory = Attribute(
        'The :term:`root factory` used by the :mod:`repoze.bfg` router '
        'when this route matches (or ``None``)')
    predicates = Attribute(
        'A sequence of :term:`route predicate` objects used to '
        'determine if a request matches this route or not or not after '
        'basic pattern matching has been completed.')
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
    
