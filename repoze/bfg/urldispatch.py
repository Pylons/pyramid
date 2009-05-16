import re

from zope.interface import implements
from zope.interface import alsoProvides

from zope.interface import classProvides

from routes import Mapper
from routes import request_config
from routes import url_for

from repoze.bfg.interfaces import IContextNotFound
from repoze.bfg.interfaces import IContextURL
from repoze.bfg.interfaces import IRoutesContext
from repoze.bfg.interfaces import ITraverser
from repoze.bfg.interfaces import ITraverserFactory

from zope.deprecation import deprecated 

_marker = ()

class DefaultRoutesContext(object):
    implements(IRoutesContext)
    def __init__(self, **kw):
        self.__dict__.update(kw)

RoutesContext = DefaultRoutesContext
deprecated('RoutesContext',
           "('from repoze.bfg.urldispatch import RoutesContext' is now "
           "deprecated; instead use 'from repoze.bfg.urldispatch import "
           "DefaultRoutesContext')",
           )

class RoutesContextNotFound(object):
    implements(IContextNotFound)
    def __init__(self, msg):
        self.msg = msg

_notfound = RoutesContextNotFound(
    'Routes context cannot be found and no fallback "get_root"')

class RoutesRootFactory(Mapper):
    """ The ``RoutesRootFactory`` is a wrapper for the root factory
    callable passed in to the repoze.bfg ``Router`` at initialization
    time.  When it is instantiated, it wraps the root factory of an
    application in such a way that the `Routes
    <http://routes.groovie.org/index.html>`_ engine has the 'first
    crack' at resolving the current request URL to a repoze.bfg view.
    Any view that claims it is 'for' the interface
    ``repoze.bfg.interfaces.IRoutesContext`` will be called if its
    name matches the Routes route ``name`` name for the match.  It
    will be passed a context object that has attributes that are
    present as Routes match arguments dictionary keys.  If no Routes
    route matches the current request, the 'fallback' get_root is
    called."""
    def __init__(self, get_root=None, **kw):
        self.get_root = get_root
        kw['controller_scan'] = None
        kw['always_scan'] = False
        kw['directory'] = None
        kw['explicit'] = True
        Mapper.__init__(self, **kw)
        self._regs_created = False

    def has_routes(self):
        return bool(self.matchlist)

    def connect(self, *arg, **kw):
        # we need to deal with our custom attributes specially :-(
        factory = None
        if '_factory' in kw:
            factory = kw.pop('_factory')
        result = Mapper.connect(self, *arg, **kw)
        self.matchlist[-1]._factory = factory
        return result

    def __call__(self, environ):
        if not self._regs_created:
            self.create_regs([])
            self._regs_created = True
        path = environ.get('PATH_INFO', '/')
        self.environ = environ # sets the thread local
        match = self.routematch(path)
        if match:
            args, route = match
        else:
            args = None
        if isinstance(args, dict): # might be an empty dict
            args = args.copy()
            routepath = route.routepath
            config = request_config()
            config.mapper = self
            config.mapper_dict = args
            config.host = environ.get('HTTP_HOST', environ['SERVER_NAME'])
            config.protocol = environ['wsgi.url_scheme']
            config.redirect = None
            kw = {}
            for k, v in args.items():
                # Routes "helpfully" converts default parameter names
                # into Unicode; these can't be used as attr names
                if k.__class__ is unicode:
                    k = k.encode('utf-8')
                kw[k] = v
            factory = route._factory
            if factory is None:
                factory = DefaultRoutesContext
                context = factory(**kw)
            else:
                context = factory(**kw)
                alsoProvides(context, IRoutesContext)
            environ['wsgiorg.routing_args'] = ((), kw)
            environ['bfg.route'] = route
            return context

        if self.get_root is None:
            return _notfound

        return self.get_root(environ)

class RoutesModelTraverser(object):
    classProvides(ITraverserFactory)
    implements(ITraverser)
    def __init__(self, context):
        self.context = context

    def __call__(self, environ):
        route = environ['bfg.route']
        match = environ['wsgiorg.routing_args'][1]

        subpath = match.get('subpath', [])
        if subpath:
            subpath = filter(None, subpath.split('/'))

        if 'path_info' in match:
            # this is stolen from routes.middleware; if the route map
            # has a *path_info capture, use it to influence the path
            # info and script_name of the generated environment
            oldpath = environ['PATH_INFO']
            newpath = match['path_info'] or ''
            environ['PATH_INFO'] = newpath
            if not environ['PATH_INFO'].startswith('/'):
                environ['PATH_INFO'] = '/' + environ['PATH_INFO']
            pattern = r'^(.*?)/' + re.escape(newpath) + '$'
            environ['SCRIPT_NAME'] += re.sub(pattern, r'\1', oldpath)
            if environ['SCRIPT_NAME'].endswith('/'):
                environ['SCRIPT_NAME'] = environ['SCRIPT_NAME'][:-1]

        return self.context, route.name, subpath, None, self.context, None

class RoutesContextURL(object):
    """ The IContextURL adapter used to generate URLs for a context
    object obtained via Routes URL dispatch.  This implementation
    juses the ``url_for`` Routes API to generate a URL based on
    ``environ['wsgiorg.routing_args']``.  Routes context objects,
    unlike traversal-based context objects, cannot have a virtual root
    that differs from its physical root; furthermore, the physical
    root of a Routes context is always itself, so the ``virtual_root``
    function returns the context of this adapter unconditionally."""
    implements(IContextURL)
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def virtual_root(self):
        return self.context 

    def __call__(self):
        return url_for(**self.request.environ['wsgiorg.routing_args'][1])
