from zope.interface import implements
from zope.interface import providedBy
from zope.interface import alsoProvides

from repoze.bfg.interfaces import IForbiddenView
from repoze.bfg.interfaces import ILogger
from repoze.bfg.interfaces import INotFoundView
from repoze.bfg.interfaces import IRootFactory
from repoze.bfg.interfaces import IRouter
from repoze.bfg.interfaces import IRouteRequest
from repoze.bfg.interfaces import IRoutesMapper
from repoze.bfg.interfaces import ISettings
from repoze.bfg.interfaces import ITraverser
from repoze.bfg.interfaces import IView

from repoze.bfg.events import AfterTraversal
from repoze.bfg.events import NewRequest
from repoze.bfg.events import NewResponse
from repoze.bfg.exceptions import Forbidden
from repoze.bfg.exceptions import NotFound
from repoze.bfg.resource import resolve_resource_spec
from repoze.bfg.request import Request
from repoze.bfg.threadlocal import manager
from repoze.bfg.traversal import DefaultRootFactory
from repoze.bfg.traversal import ModelGraphTraverser
from repoze.bfg.view import default_forbidden_view
from repoze.bfg.view import default_notfound_view

class Router(object):
    """ The main repoze.bfg WSGI application. """
    implements(IRouter)

    debug_notfound = False
    threadlocal_manager = manager

    def __init__(self, registry):
        q = registry.queryUtility
        self.logger = q(ILogger, 'repoze.bfg.debug')
        self.notfound_view = q(INotFoundView, default=default_notfound_view)
        self.forbidden_view = q(IForbiddenView, default=default_forbidden_view)
        self.root_factory = q(IRootFactory, default=DefaultRootFactory)
        self.routes_mapper = q(IRoutesMapper)
        self.root_policy = self.root_factory # b/w compat
        self.registry = registry
        settings = registry.queryUtility(ISettings)
        if settings is not None:
            self.debug_notfound = settings['debug_notfound']

    def __call__(self, environ, start_response):
        """
        Accept ``environ`` and ``start_response``; route requests to
        ``repoze.bfg`` views based on registrations within the
        application registry; call ``start_response`` and return an
        iterable.
        """
        registry = self.registry
        has_listeners = registry.has_listeners
        logger = self.logger
        manager = self.threadlocal_manager
        threadlocals = {'registry':registry, 'request':None}
        manager.push(threadlocals)

        try:
            # setup
            request = Request(environ)
            threadlocals['request'] = request
            attrs = request.__dict__
            attrs['registry'] = registry
            has_listeners and registry.notify(NewRequest(request))

            # root resolution
            root_factory = self.root_factory
            if self.routes_mapper is not None:
                info = self.routes_mapper(request)
                match, route = info['match'], info['route']
                if route is not None:
                    environ['wsgiorg.routing_args'] = ((), match)
                    environ['bfg.routes.route'] = route
                    environ['bfg.routes.matchdict'] = match
                    request.matchdict = match
                    iface = registry.queryUtility(IRouteRequest,
                                                  name=route.name)
                    if iface is not None:
                        alsoProvides(request, iface)
                    root_factory = route.factory or self.root_factory
                
            root = root_factory(request)
            attrs['root'] = root

            # view lookup
            traverser = registry.adapters.queryAdapter(root, ITraverser)
            if traverser is None:
                traverser = ModelGraphTraverser(root)
            tdict = traverser(request)
            context, view_name, subpath, traversed, vroot, vroot_path = (
                tdict['context'], tdict['view_name'], tdict['subpath'],
                tdict['traversed'], tdict['virtual_root'],
                tdict['virtual_root_path'])
            attrs.update(tdict)
            has_listeners and registry.notify(AfterTraversal(request))
            provides = map(providedBy, (context, request))
            view_callable = registry.adapters.lookup(
                provides, IView, name=view_name, default=None)

            # view execution
            if view_callable is None:
                if self.debug_notfound:
                    msg = (
                        'debug_notfound of url %s; path_info: %r, context: %r, '
                        'view_name: %r, subpath: %r, traversed: %r, '
                        'root: %r, vroot: %r,  vroot_path: %r' % (
                        request.url, request.path_info, context, view_name,
                        subpath, traversed, root, vroot, vroot_path)
                        )
                    logger and logger.debug(msg)
                else:
                    msg = request.path_info
                environ['repoze.bfg.message'] = msg
                response = self.notfound_view(context, request)
            else:
                try:
                    response = view_callable(context, request)
                except Forbidden, why:
                    msg = why[0]
                    environ['repoze.bfg.message'] = msg
                    response = self.forbidden_view(context, request)
                except NotFound, why:
                    msg = why[0]
                    environ['repoze.bfg.message'] = msg
                    response = self.notfound_view(context, request)

            # response handling
            has_listeners and registry.notify(NewResponse(response))
            try:
                headers = response.headerlist
                app_iter = response.app_iter
                status = response.status
            except AttributeError:
                raise ValueError(
                    'Non-response object returned from view named %s '
                    '(and no renderer): %r' % (view_name, response))

            if 'global_response_headers' in attrs:
                headers = list(headers)
                headers.extend(attrs['global_response_headers'])
            
            start_response(response.status, headers)
            return response.app_iter

        finally:
            manager.pop()

# note that ``options`` is a b/w compat alias for ``settings`` and
# ``Configurator`` is a testing dep inj
def make_app(root_factory, package=None, filename='configure.zcml',
             settings=None, options=None, Configurator=None):
    """ Return a Router object, representing a fully configured
    ``repoze.bfg`` WSGI application.

    ``root_factory`` must be a callable that accepts a :term:`request`
    object and which returns a traversal root object.  The traversal
    root returned by the root factory is the *default* traversal root;
    it can be overridden on a per-view basis.  ``root_factory`` may be
    ``None``, in which case a 'default default' traversal root is
    used.

    ``package`` is a Python module representing the application's
    package.  It is optional, defaulting to ``None``.  ``package`` may
    be ``None``.  If ``package`` is ``None``, the ``filename`` passed
    or the value in the ``options`` dictionary named
    ``configure_zcml`` must be a) absolute pathname to a ZCML file
    that represents the application's configuration *or* b) a
    'specification' in the form
    ``dotted_package_name:relative/file/path.zcml``.

    ``filename`` is the filesystem path to a ZCML file (optionally
    relative to the package path) that should be parsed to create the
    application registry.  It defaults to ``configure.zcml``.  It can
    also be a 'specification' in the form
    ``dotted_package_name:relatve/file/path.zcml``. Note that if any
    value for ``configure_zcml`` is passed within the ``options``
    dictionary, the value passed as ``filename`` will be ignored,
    replaced with the ``configure_zcml`` value.

    ``settings``, if used, should be a dictionary containing runtime
    settings (e.g. the key/value pairs in an app section of a
    PasteDeploy file), with each key representing the option and the
    key's value representing the specific option value,
    e.g. ``{'reload_templates':True}``.  Note that the keyword
    parameter ``options`` is a backwards compatibility alias for the
    ``settings`` keyword parameter.
    """
    if Configurator is None:
        from repoze.bfg.configuration import Configurator # pragma: no cover
    settings = settings or options
    config = Configurator()
    package_name = package and package.__name__ or None
    package_name, filename = resolve_resource_spec(filename, package_name)
    if package_name is not None:
        spec = '%s:%s' % (package_name, filename)
    else:
        spec = filename
    config.declarative(root_factory, spec, settings=settings)
    app = config.make_wsgi_app()
    return app

