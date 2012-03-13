from zope.interface import (
    implementer,
    providedBy,
    )

from pyramid.interfaces import (
    IDebugLogger,
    IRequest,
    IRootFactory,
    IRouteRequest,
    IRouter,
    IRequestFactory,
    IRoutesMapper,
    ITraverser,
    IView,
    IViewClassifier,
    ITweens,
    )

from pyramid.events import (
    ContextFound,
    NewRequest,
    NewResponse,
    )

from pyramid.httpexceptions import HTTPNotFound
from pyramid.request import Request
from pyramid.threadlocal import manager

from pyramid.traversal import (
    DefaultRootFactory,
    ResourceTreeTraverser,
    )

from pyramid.tweens import excview_tween_factory

@implementer(IRouter)
class Router(object):

    debug_notfound = False
    debug_routematch = False

    threadlocal_manager = manager

    def __init__(self, registry):
        q = registry.queryUtility
        self.logger = q(IDebugLogger)
        self.root_factory = q(IRootFactory, default=DefaultRootFactory)
        self.routes_mapper = q(IRoutesMapper)
        self.request_factory = q(IRequestFactory, default=Request)
        tweens = q(ITweens)
        if tweens is None:
            tweens = excview_tween_factory
        self.handle_request = tweens(self.handle_request, registry)
        self.root_policy = self.root_factory # b/w compat
        self.registry = registry
        settings = registry.settings
        if settings is not None:
            self.debug_notfound = settings['debug_notfound']
            self.debug_routematch = settings['debug_routematch']

    def handle_request(self, request):
        attrs = request.__dict__
        registry = attrs['registry']

        request.request_iface = IRequest
        context = None
        routes_mapper = self.routes_mapper
        debug_routematch = self.debug_routematch
        adapters = registry.adapters
        has_listeners = registry.has_listeners
        notify = registry.notify
        logger = self.logger

        has_listeners and notify(NewRequest(request))
        # find the root object
        root_factory = self.root_factory
        if routes_mapper is not None:
            info = routes_mapper(request)
            match, route = info['match'], info['route']
            if route is None:
                if debug_routematch:
                    msg = ('no route matched for url %s' %
                           request.url)
                    logger and logger.debug(msg)
            else:
                # TODO: kill off bfg.routes.* environ keys
                # when traverser requires request arg, and
                # cant cope with environ anymore (they are
                # docs-deprecated as of BFG 1.3)
                environ = request.environ
                environ['bfg.routes.route'] = route 
                environ['bfg.routes.matchdict'] = match
                attrs['matchdict'] = match
                attrs['matched_route'] = route

                if debug_routematch:
                    msg = (
                        'route matched for url %s; '
                        'route_name: %r, '
                        'path_info: %r, '
                        'pattern: %r, '
                        'matchdict: %r, '
                        'predicates: %r' % (
                            request.url,
                            route.name,
                            request.path_info,
                            route.pattern, match,
                            ', '.join([p.__text__ for p in route.predicates]))
                        )
                    logger and logger.debug(msg)

                request.request_iface = registry.queryUtility(
                    IRouteRequest,
                    name=route.name,
                    default=IRequest)

                root_factory = route.factory or self.root_factory

        root = root_factory(request)
        attrs['root'] = root

        # find a context
        traverser = adapters.queryAdapter(root, ITraverser)
        if traverser is None:
            traverser = ResourceTreeTraverser(root)
        tdict = traverser(request)

        context, view_name, subpath, traversed, vroot, vroot_path = (
            tdict['context'],
            tdict['view_name'],
            tdict['subpath'],
            tdict['traversed'],
            tdict['virtual_root'],
            tdict['virtual_root_path']
            )

        attrs.update(tdict)
        has_listeners and notify(ContextFound(request))

        # find a view callable
        context_iface = providedBy(context)
        view_callable = adapters.lookup(
            (IViewClassifier, request.request_iface, context_iface),
            IView, name=view_name, default=None)

        # invoke the view callable
        if view_callable is None:
            if self.debug_notfound:
                msg = (
                    'debug_notfound of url %s; path_info: %r, '
                    'context: %r, view_name: %r, subpath: %r, '
                    'traversed: %r, root: %r, vroot: %r, '
                    'vroot_path: %r' % (
                        request.url, request.path_info, context,
                        view_name, subpath, traversed, root, vroot,
                        vroot_path)
                    )
                logger and logger.debug(msg)
            else:
                msg = request.path_info
            raise HTTPNotFound(msg)
        else:
            response = view_callable(context, request)

        return response

    def __call__(self, environ, start_response):
        """
        Accept ``environ`` and ``start_response``; create a
        :term:`request` and route the request to a :app:`Pyramid`
        view based on introspection of :term:`view configuration`
        within the application registry; call ``start_response`` and
        return an iterable.
        """
        registry = self.registry
        has_listeners = self.registry.has_listeners
        notify = self.registry.notify
        request = self.request_factory(environ)
        threadlocals = {'registry':registry, 'request':request}
        manager = self.threadlocal_manager
        manager.push(threadlocals)
        request.registry = registry
        try:

            try:
                response = self.handle_request(request)
                has_listeners and notify(NewResponse(request, response))

                if request.response_callbacks:
                    request._process_response_callbacks(response)

                return response(request.environ, start_response)

            finally:
                if request.finished_callbacks:
                    request._process_finished_callbacks()

        finally:
            manager.pop()

