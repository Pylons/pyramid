from zope.interface import Interface
from zope.interface import Attribute

from zope.component.interfaces import IObjectEvent

class IRequest(Interface):
    """ Marker interface for a request object """
    
class IResponse(Interface):
    status = Attribute('WSGI status code of response')
    headerlist = Attribute('List of response headers')
    app_iter = Attribute('Iterable representing the response body')

class IView(Interface):
    def __call__(context, request):
        """ Must return an object that implements IResponse """

class IRootPolicy(Interface):
    def __call__(environ):
        """ Return a root object """

class ITraverser(Interface):
    def __call__(environ):
        """ Return a tuple in the form (context, name, subpath), typically
        the result of an object graph traversal """

class ITraverserFactory(Interface):
    def __call__(context):
        """ Return an object that implements IPublishTraverser """

class ITemplateFactory(Interface):
    def __call__(path, auto_reload=False):
        """ Return an an ITemplate given a filesystem path """

class ITemplate(Interface):
    def __call__(**kw):
        """ Return a string result given a template path """

class INodeTemplate(Interface):
    def __call__(node, **kw):
        """ Return a string result given a template path """
        
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

    registry = interface.Attribute(
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

