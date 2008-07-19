from zope.interface import Interface
from zope.interface import Attribute

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
    def __call__(path):
        """ Return a tuple in the form (context, name, subpath), typically
        the result of an object graph traversal """

class ITraverserFactory(Interface):
    def __call__(context, request):
        """ Return an object that implements IPublishTraverser """

class ITemplateFactory(Interface):
    def __call__(path):
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

class NoAuthorizationInformation(Exception):
    pass

class IViewPermission(Interface):
    def __call__(security_policy):
        """ Return True if the permission allows, return False if it denies. """

class IViewPermissionFactory(Interface):
    def __call__(context, request):
        """ Return an IViewPermission """

