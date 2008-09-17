from zope.interface import implements
from zope.interface import classProvides
from zope.interface import alsoProvides

from routes import Mapper
from routes import request_config

from repoze.bfg.interfaces import IRoutesContext
from repoze.bfg.interfaces import ITraverserFactory
from repoze.bfg.interfaces import ITraverser

_marker = ()

class RoutesContext(object):
    implements(IRoutesContext)
    def __init__(self, **kw):
        self.__dict__.update(kw)

class RoutesMapper(object):
    """ The ``RoutesMapper`` is a wrapper for the ``get_root``
    callable passed in to the repoze.bfg ``Router`` at initialization
    time.  When it is instantiated, it wraps the get_root of an
    application in such a way that the `Routes
    <http://routes.groovie.org/index.html>`_ engine has the 'first
    crack' at resolving the current request URL to a repoze.bfg view.
    Any view that claims it is 'for' the interface
    ``repoze.bfg.interfaces.IRoutesContext`` will be called if its
    *name* matches the Routes 'controller' name for the match.  It
    will be passed a context object that has attributes that match the
    Routes match arguments dictionary keys.  If no Routes route
    matches the current request, the 'fallback' get_root is called."""
    def __init__(self, get_root):
        self.get_root = get_root
        self.mapper = Mapper(controller_scan=None, directory=None,
                             explicit=True, always_scan=False)
        self.mapper.explicit = True
        self._regs_created = False

    def __call__(self, environ):
        if not self._regs_created:
            self.mapper.create_regs([])
            self._regs_created = True
        path = environ.get('PATH_INFO', '/')
        self.mapper.environ = environ
        args = self.mapper.match(path)
        if args:
            context_factory = args.get('context_factory', _marker)
            if context_factory is _marker:
                context_factory = RoutesContext
            else:
                args = args.copy()
                del args['context_factory']
            config = request_config()
            config.mapper = self.mapper
            config.mapper_dict = args
            config.host = environ.get('HTTP_HOST', environ['SERVER_NAME'])
            config.protocol = environ['wsgi.url_scheme']
            config.redirect = None
            context = context_factory(**args)
            alsoProvides(context, IRoutesContext)
            return context

        # fall back to original get_root
        return self.get_root(environ)

    def connect(self, *arg, **kw):
        """ Add a route to the Routes mapper associated with this
        request. This method accepts the same arguments as a Routes
        *Mapper* object.  One difference exists: if the
        ``context_factory`` is passed in with a value as a keyword
        argument, this callable will be called when a model object
        representing the ``context`` for the request needs to be
        constructed.  It will be called with the (all-keyword)
        arguments supplied by the Routes mapper's ``match`` method for
        this route, and should return an instance of a class.  If
        ``context_factory`` is not supplied in this way for a route, a
        default context factory (the ``RoutesContext`` class) will be
        used.  The interface ``repoze.bfg.interfaces.IRoutesContext``
        will always be tacked on to the context instance in addition
        to whatever interfaces the context instance already supplies."""
        self.mapper.connect(*arg, **kw)

class RoutesModelTraverser(object):
    classProvides(ITraverserFactory)
    implements(ITraverser)
    def __init__(self, context):
        self.context = context

    def __call__(self, environ):
        return self.context, self.context.controller, ''
    
    
        
        

