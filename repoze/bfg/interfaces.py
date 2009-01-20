from zope.interface import Attribute
from zope.interface import Interface
from zope.interface import implements

from zope.deferredimport import deprecated

from zope.component.interfaces import IObjectEvent

from webob import Request as WebobRequest


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
    """ A utility which generates a request factory """
    def __call__():
        """ Return a request factory (e.g. a callable that accepts an
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
        """ Return a tuple in the form (context, name, subpath), typically
        the result of an object graph traversal """

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

class NoAuthorizationInformation(Exception):
    pass

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
    
