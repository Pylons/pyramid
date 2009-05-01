from zope.interface import Attribute
from zope.interface import Interface

from zope.deferredimport import deprecated

from zope.component.interfaces import IObjectEvent

deprecated(
    '(repoze.bfg.interfaces.ITemplate should now be imported '
    'as repoze.bfg.interfaces.ITemplateRenderer)',
    ITemplate = 'repoze.bfg.interfaces:INodeTemplateRenderer',
    )

deprecated(
    '(repoze.bfg.interfaces.INodeTemplate should now be imported '
     'as repoze.bfg.interfaces.INodeTemplateRenderer)',
    INodeTemplate = 'repoze.bfg.interfaces:INodeTemplateRenderer',
    )

deprecated(
    '(repoze.bfg.interfaces.ITemplateFactory should now be imported '
    'as repoze.bfg.interfaces.ITemplateRendererFactory)',
    ITemplateFactory = 'repoze.bfg.interfaces:ITemplateRendererFactory',
    )

deprecated(
    '(repoze.bfg.interfaces.IRootPolicy should now be imported '
    'as repoze.bfg.interfaces.IRootFactory)',
    IRootPolicy = "repoze.bfg.interfaces:IRootFactory",
    )

class IRequestFactory(Interface):
    """ A utility which generates a request object """
    def __call__():
        """ Return a request factory (a callable that accepts an
        environ and returns an object implementing IRequest,
        e.g. ``webob.Request``)"""

class IRequest(Interface):
    """ Request type interface attached to all request objects """

class IPOSTRequest(IRequest):
    """ Request type interface attached to POST requests"""

class IGETRequest(IRequest):
    """ Request type interface attached to GET requests"""

class IPUTRequest(IRequest):
    """ Request type interface attached to PUT requests"""

class IDELETERequest(IRequest):
    """ Request type interface attached to DELETE requests"""

class IHEADRequest(IRequest):
    """ Request type interface attached to HEAD requests"""
    
class IResponseFactory(Interface):
    """ A utility which generates a response factory """
    def __call__():
        """ Return a response factory (e.g. a callable that returns an
        object implementing IResponse, e.g. ``webob.Response``; it
        should accept all the arguments that the webob.Response class
        accepts)"""

class IResponse(Interface):
    status = Attribute('WSGI status code of response')
    headerlist = Attribute('List of response headers')
    app_iter = Attribute('Iterable representing the response body')

class IView(Interface):
    def __call__(context, request):
        """ Must return an object that implements IResponse """

class IRootFactory(Interface):
    def __call__(environ):
        """ Return a root object """

class ITraverser(Interface):
    def __call__(environ):
        """ Return a tuple in the form ``(context, view_name, subpath,
        traversed, virtual_root, virtual_root_path)`` , typically the
        result of an object graph traversal.  ``context`` will be a
        model object, ``view_name`` will be the view name used (a
        Unicode name), ``subpath`` will be a sequence of Unicode names
        that followed the view name but were not traversed,
        ``traversed`` will be a sequence of Unicode names that were
        traversed (including the virtual root path, if any) or
        ``None`` if no traversal was performed, ``virtual_root`` will
        be a model object representing the virtual root (or the
        physical root if traversal was not performed), and
        ``virtual_root_path`` will be a sequence representing the
        virtual root path (a sequence of Unicode names) or None if
        traversal was not performed."""

class ITraverserFactory(Interface):
    def __call__(context):
        """ Return an object that implements ITraverser """

class ITemplateRenderer(Interface):
    def implementation():
        """ Return the object that the underlying templating system
        uses to render the template; it is typically a callable that
        accepts arbitrary keyword arguments and returns a string or
        unicode object """

    def __call__(**kw):
        """ Call a the template implementation with the keywords
        passed in as arguments and return the result (a string or
        unicode object) """

class ITemplateRendererFactory(Interface):
    def __call__(path, auto_reload=False):
        """ Return an object that implements ``ITemplateRenderer``  """

class INodeTemplateRenderer(Interface):
    def __call__(node, **kw):
        """ Return a string result given a node and a template path """

class ISecurityPolicy(Interface):
    """ A utility that provides a mechanism to check authorization
       using authentication data """
    def permits(context, request, permission):
        """ Returns True if the combination of the authorization
        information in the context and the authentication data in
        the request allow the action implied by the permission """

    def authenticated_userid(request):
        """ Return the userid of the currently authenticated user or
        None if there is no currently authenticated user """

    def effective_principals(request):
        """ Return the list of 'effective' principals for the request.
        This must include the userid of the currently authenticated
        user if a user is currently authenticated."""

    def principals_allowed_by_permission(context, permission):
        """ Return a sequence of principal identifiers allowed by the
        ``permission`` in the model implied by ``context``.  This
        method may not be supported by a given security policy
        implementation, in which case, it should raise a
        ``NotImplementedError`` exception."""

class IViewPermission(Interface):
    def __call__(security_policy):
        """ Return True if the permission allows, return False if it denies. """

class IViewPermissionFactory(Interface):
    def __call__(context, request):
        """ Return an IViewPermission """

class IRouter(Interface):
    """WSGI application which routes requests to 'view' code based on
    a view registry."""

    registry = Attribute(
        """Component architecture registry local to this application.""")
    
class IRoutesContext(Interface):
    """ A context (model instance) that is created as a result of URL
    dispatching"""

class INewRequest(Interface):
    """ An event type that is emitted whenever repoze.bfg begins to
    process a new request """
    request = Attribute('The request object')
    
class INewResponse(Interface):
    """ An event type that is emitted whenever any repoze.bfg view
    returns a response."""
    response = Attribute('The response object')

class ISettings(Interface):
    """ Runtime settings for repoze.bfg """
    reload_templates = Attribute('Reload templates when they change')
    
class IWSGIApplicationCreatedEvent(IObjectEvent):
    """ Event issued after the application has been created and
    configured."""
    
    app = Attribute(u"Published application")

# this interface, even if it becomes unused within BFG, is imported by
# other packages (such as repoze.bfg.traversalwrapper)
class ILocation(Interface):
    """Objects that have a structural location"""

    __parent__ = Attribute("The parent in the location hierarchy")

    __name__ = Attribute("The name within the parent")

class ILogger(Interface):
    """ Interface representing a PEP 282 logger """

class IRoutesMapper(Interface):
    """ Interface representing a Routes ``Mapper`` object """
    
class IContextNotFound(Interface):
    """ Interface implemented by contexts generated by code which
    cannot find a context during root finding or traversal """
    
class INotFoundAppFactory(Interface):
    """ A utility which returns a NotFound WSGI application factory """
    def __call__():
        """ Return a callable which returns a notfound WSGI
        application.  When the WSGI application is invoked,
        a``message`` key in the WSGI environ provides information
        pertaining to the reason for the notfound."""

class IUnauthorizedAppFactory(Interface):
    """ A utility which returns an Unauthorized WSGI application
    factory"""
    def __call__():
        """ Return a callable which returns an unauthorized WSGI
        application.  When the WSGI application is invoked, a
        ``message`` key in the WSGI environ provides information
        pertaining to the reason for the unauthorized."""

class IContextURL(Interface):
    """ An adapter which deals with URLs related to a context.
    """
    def virtual_root():
        """ Return the virtual root related to a request and the
        current context"""

    def __call__():
        """ Return a URL that points to the context """

# VH_ROOT_KEY is an interface; its imported from other packages (e.g.
# traversalwrapper)
VH_ROOT_KEY = 'HTTP_X_VHM_ROOT' 
