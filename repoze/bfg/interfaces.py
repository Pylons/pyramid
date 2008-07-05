from zope.interface import Interface

class IWSGIApplicationFactory(Interface):
    def __call__(context):
        """ Return a WSGI (PEP333) application """

class IRootPolicy(Interface):
    def __call__(environ):
        """ Return a root object """

class ITraversalPolicy(Interface):
    def __call__(environ, root):
        """ Return a tuple in the form (context, name, subpath) """
        
class ITraverser(Interface):
    def __init__(context):
        """ Accept a context """

    def __call__(environ, name):
        """ Return a subcontext or based on name """
        
class IWebObRequest(Interface):
    """ Marker interface for a webob.Request object """
    
