from zope.interface import Interface
from zope.interface import Attribute

class IResponse(Interface):
    status = Attribute('WSGI status code of response')
    headerlist = Attribute('List of response headers')
    app_iter = Attribute('Iterable representing the response body')

class IView(Interface):
    def __call__(*arg, **kw):
        """ Must return an object that implements IResponse; args are
        mapped into an IView's __call__ by mapply-like code """
        
class IViewFactory(Interface):
    def __call__(context, request):
        """ Return an object that implements IView """

class IRootPolicy(Interface):
    def __call__(environ):
        """ Return a root object """

class IPublishTraverser(Interface):
    def __call__(path):
        """ Return a tuple in the form (context, name, subpath), typically
        the result of an object graph traversal """

class IPublishTraverserFactory(Interface):
    def __call__(context, request):
        """ Return an object that implements IPublishTraverser """

class IWSGIApplication(Interface):
    def __call__(environ, start_response):
        """ A PEP 333 application """

class IWSGIApplicationFactory(Interface):
    def __call__(view, request):
        """ Return an object that implements IWSGIApplication """

class IRequest(Interface):
    """ Marker interface for a request object """
    
class ILocation(Interface):
    """Objects that have a structural location"""
    __parent__ = Attribute("The parent in the location hierarchy")
    __name__ = Attribute("The name of the object")
