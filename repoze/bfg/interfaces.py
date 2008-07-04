from zope.interface import Interface

class IWSGIApplication(Interface):
    def __call__(environ, start_response):
        """ Represent a WSGI (PEP 333) application """

class ITraversalPolicy(Interface):
    def __call__(environ, root):
        """ Return a tuple in the form (context, name, subpath) """
        
class ITraverser(Interface):
    def __init__(context):
        """ Accept a context """

    def __call__(environ, name):
        """ Return a subcontext or based on name """
        
