from zope.interface import implements
from zope.interface import providedBy

from repoze.bfg.interfaces import IDebugLogger
from repoze.bfg.interfaces import IExceptionViewClassifier
from repoze.bfg.interfaces import IRequest
from repoze.bfg.interfaces import IRootFactory
from repoze.bfg.interfaces import IRouteRequest
from repoze.bfg.interfaces import IRouter
from repoze.bfg.interfaces import IRoutesMapper
from repoze.bfg.interfaces import ISettings
from repoze.bfg.interfaces import ITraverser
from repoze.bfg.interfaces import IView
from repoze.bfg.interfaces import IViewClassifier

from repoze.bfg.configuration import make_app # b/c import
from repoze.bfg.events import AfterTraversal
from repoze.bfg.events import NewRequest
from repoze.bfg.events import NewResponse
from repoze.bfg.exceptions import NotFound
from repoze.bfg.request import Request
from repoze.bfg.threadlocal import manager
from repoze.bfg.traversal import DefaultRootFactory
from repoze.bfg.traversal import ModelGraphTraverser

make_app # prevent pyflakes from complaining

class Router(object):
    implements(IRouter)

    debug_notfound = False
    threadlocal_manager = manager

    def __init__(self, registry):
        q = registry.queryUtility
        self.logger = q(IDebugLogger)
        self.root_factory = q(IRootFactory, default=DefaultRootFactory)
        self.routes_mapper = q(IRoutesMapper)
        self.root_policy = self.root_factory # b/w compat
        self.registry = registry
        settings = registry.queryUtility(ISettings)
        if settings is not None:
            self.debug_notfound = settings['debug_notfound']

    def __call__(self, environ, start_response):
        """
        Accept ``environ`` and ``start_response``; create a
        :term:`request` and route the request to a :mod:`repoze.bfg`
        view based on introspection of :term:`view configuration`
        within the application registry; call ``start_response`` and
        return an iterable.
        """
        registry = self.registry
        adapters = registry.adapters
        has_listeners = registry.has_listeners
        logger = self.logger
        manager = self.threadlocal_manager
        threadlocals = {'registry':registry, 'request':None}
        manager.push(threadlocals)

        try:
            # create the request
            request = Request(environ)
            context = None
            threadlocals['request'] = request
            attrs = request.__dict__
            attrs['registry'] = registry
            has_listeners and registry.notify(NewRequest(request))

            request_iface = IRequest

            try:
                # find the root
                root_factory = self.root_factory
                if self.routes_mapper is not None:
                    info = self.routes_mapper(request)
                    match, route = info['match'], info['route']
                    if route is not None:
                        environ['wsgiorg.routing_args'] = ((), match)
                        environ['bfg.routes.route'] = route
                        environ['bfg.routes.matchdict'] = match
                        attrs['matchdict'] = match
                        request_iface = registry.queryUtility(
                            IRouteRequest,
                            name=route.name,
                            default=IRequest)
                        root_factory = route.factory or self.root_factory

                root = root_factory(request)
                attrs['root'] = root

                # find a view callable
                traverser = adapters.queryAdapter(root, ITraverser)
                if traverser is None:
                    traverser = ModelGraphTraverser(root)
                tdict = traverser(request)
                context, view_name, subpath, traversed, vroot, vroot_path = (
                    tdict['context'], tdict['view_name'], tdict['subpath'],
                    tdict['traversed'], tdict['virtual_root'],
                    tdict['virtual_root_path'])
                attrs.update(tdict)
                has_listeners and registry.notify(AfterTraversal(request))
                context_iface = providedBy(context)
                view_callable = adapters.lookup(
                    (IViewClassifier, request_iface, context_iface),
                    IView, name=view_name, default=None)

                # invoke the view callable
                if view_callable is None:
                    if self.debug_notfound:
                        msg = (
                            'debug_notfound of url %s; path_info: %r, '
                            'context: %r, view_name: %r, subpath: %r, '
                            'traversed: %r, root: %r, vroot: %r, '
                            'vroot_path: %r' % (
                            request.url, request.path_info, context, view_name,
                            subpath, traversed, root, vroot, vroot_path)
                            )
                        logger and logger.debug(msg)
                    else:
                        msg = request.path_info
                    environ['repoze.bfg.message'] = msg
                    raise NotFound(msg)
                else:
                    response = view_callable(context, request)

            # handle exceptions raised during root finding and view lookup
            except Exception, why:
                for_ = (IExceptionViewClassifier,
                        request_iface.combined,
                        providedBy(why))
                view_callable = adapters.lookup(for_, IView, default=None)
                if view_callable is None:
                    raise

                try:
                    msg = why[0]
                except Exception:
                    msg = ''
                environ['repoze.bfg.message'] = msg

                attrs['exception'] = why
                response = view_callable(why, request)

            # process the response
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

            start_response(status, headers)
            return app_iter

        finally:
            manager.pop()

