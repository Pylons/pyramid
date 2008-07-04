from zope.interface import Interface

class IWSGIApplication(Interface):
    def __call__(environ, start_response):
        """ Represent a WSGI (PEP 333) application """

class IPolicy(Interface):
    def __call__(environ):
        """ Return a tuple in the form (context, name, subpath) """
        
