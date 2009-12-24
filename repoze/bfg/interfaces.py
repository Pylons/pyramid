from zope.interface import Attribute
from zope.interface import Interface

# public API interfaces

class IAfterTraversal(Interface):
    """ An event type that is emitted after :mod:`repoze.bfg`
    completes traversal but before it calls any view code."""
    request = Attribute('The request object')

class INewRequest(Interface):
    """ An event type that is emitted whenever :mod:`repoze.bfg`
    begins to process a new request"""
    request = Attribute('The request object')
    
class INewResponse(Interface):
    """ An event type that is emitted whenever any :mod:`repoze.bfg`
    view returns a response."""
    response = Attribute('The response object')

class IWSGIApplicationCreatedEvent(Interface):
    """ Event issued when the
    :meth:`repoze.bfg.configuration.Configurator.make_wsgi_app` method
    is called."""
    app = Attribute(u"Published application")

# internal interfaces

class IRequest(Interface):
    """ Request type interface attached to all request objects """

class IRouteRequest(Interface):
    """ *internal only* interface used as in a utility lookup to find
    route-specific interfaces.  Not an API."""

class IResponse(Interface):
    status = Attribute('WSGI status code of response')
    headerlist = Attribute('List of response headers')
    app_iter = Attribute('Iterable representing the response body')

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


class IResponseFactory(Interface):
    """ A utility which generates a response factory """
    def __call__():
        """ Return a response factory (e.g. a callable that returns an
        object implementing IResponse, e.g. ``webob.Response``; it
        should accept all the arguments that the webob.Response class
        accepts)"""

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
    def add(view, predicates, score):
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

class IRoutesMapper(Interface):
    """ Interface representing a Routes ``Mapper`` object """
    def get_routes():
        """ Return a sequence of Route objects registered in the mapper."""

    def connect(path, name, factory=None, predicates=()):
        """ Add a new route. """

    def generate(name, kw):
        """ Generate a URL using the route named ``name`` with the
        keywords implied by kw"""

    def __call__(request):
        """ Return a matchdict for the request; the ``route`` key will
        either be a Route object or ``None`` if no route matched."""

class IForbiddenView(Interface):
    """ A utility which returns an IResponse as the result of the
    denial of a view invocation by a security policy."""
    def __call__(context, request):
        """ Return an object implementing IResponse (an object with
        the status, headerlist, and app_iter attributes) as a result
        of a view invocation denial by a security policy.
        
        Note that the ``message`` key in the WSGI environ
        (request.environ) provides information pertaining to the
        reason for the view invocation denial.  The ``context`` passed
        to the forbidden app factory will be the context found by the
        repoze.bfg router during traversal or url dispatch.  The
        ``request`` will be the request object which caused the deny."""

class INotFoundView(Interface):
    """ A utility which returns a NotFound response (an IResponse)
    when a view cannot be located for a particular URL"""
    def __call__(context, request):
        """ Return a NotFound response.  When the view is rendered,
        a``message`` key in the WSGI environ provides information
        pertaining to the reason for the notfound error."""

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
