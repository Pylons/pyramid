from zope.interface import implements
from zope.interface import providedBy

from pyramid.interfaces import IDebugLogger
from pyramid.interfaces import IExceptionViewClassifier
from pyramid.interfaces import IRequest
from pyramid.interfaces import IRootFactory
from pyramid.interfaces import IRouteRequest
from pyramid.interfaces import IRouter
from pyramid.interfaces import IRequestFactory
from pyramid.interfaces import IRoutesMapper
from pyramid.interfaces import ITraverser
from pyramid.interfaces import IView
from pyramid.interfaces import IViewClassifier
from pyramid.interfaces import IRequestHandlerFactory
from pyramid.interfaces import IRequestHandlerFactories

from pyramid.events import ContextFound
from pyramid.events import NewRequest
from pyramid.events import NewResponse
from pyramid.httpexceptions import HTTPNotFound
from pyramid.request import Request
from pyramid.threadlocal import manager
from pyramid.traversal import DefaultRootFactory
from pyramid.traversal import ResourceTreeTraverser

class Router(object):
    implements(IRouter)

    debug_notfound = False
    debug_routematch = False

    threadlocal_manager = manager

    def __init__(self, registry):
        q = registry.queryUtility
        self.logger = q(IDebugLogger)
        self.root_factory = q(IRootFactory, default=DefaultRootFactory)
        self.routes_mapper = q(IRoutesMapper)
        self.request_factory = q(IRequestFactory, default=Request)
        handler_factory_names = q(IRequestHandlerFactories)
        handler = self.handle_request
        if handler_factory_names:
            for name in handler_factory_names:
                handler_factory = registry.getUtility(IRequestHandlerFactory,
                                                      name=name)
                handler = handler_factory(handler, registry)
            self.handle_request = handler
        self.root_policy = self.root_factory # b/w compat
        self.registry = registry
        settings = registry.settings

        if settings is not None:
            self.debug_notfound = settings['debug_notfound']
            self.debug_routematch = settings['debug_routematch']

    def handle_request(self, request):
        attrs = request.__dict__
        registry = attrs['registry']
        request_iface = IRequest
        context = None
        routes_mapper = self.routes_mapper
        debug_routematch = self.debug_routematch
        adapters = registry.adapters
        has_listeners = registry.has_listeners
        notify = registry.notify
        logger = self.logger
        try: # matches except Exception (exception view execution)
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
                                route.predicates)
                            )
                        logger and logger.debug(msg)

                    request_iface = registry.queryUtility(
                        IRouteRequest,
                        name=route.name,
                        default=IRequest)
                    
                    root_factory = route.factory or \
                                   self.root_factory

            root = root_factory(request)
            attrs['root'] = root

            # find a context
            traverser = adapters.queryAdapter(root, ITraverser)
            if traverser is None:
                traverser = ResourceTreeTraverser(root)
            tdict = traverser(request)

            context, view_name, subpath, traversed, vroot, \
                vroot_path = (
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
                            request.url, request.path_info, context,
                            view_name,
                            subpath, traversed, root, vroot,
                            vroot_path)
                        )
                    logger and logger.debug(msg)
                else:
                    msg = request.path_info
                raise HTTPNotFound(msg)
            else:
                # if there were any view wrappers for the current
                # request, use them to wrap the view

                response = view_callable(context, request)

        # handle exceptions raised during root finding and view-exec
        except Exception, why:
            # clear old generated request.response, if any; it may
            # have been mutated by the view, and its state is not
            # sane (e.g. caching headers)
            if 'response' in attrs:
                del attrs['response']

            attrs['exception'] = why

            for_ = (IExceptionViewClassifier,
                    request_iface.combined,
                    providedBy(why))
            view_callable = adapters.lookup(for_, IView,
                                            default=None)

            if view_callable is None:
                raise

            response = view_callable(why, request)

        has_listeners and notify(NewResponse(request, response))

        if request.response_callbacks:
            request._process_response_callbacks(response)

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
        manager = self.threadlocal_manager
        request = None
        threadlocals = {'registry':registry, 'request':request}
        manager.push(threadlocals)

        try: # matches finally: manager.pop()

            try: # matches finally:  ... call request finished callbacks ...
                
                # create the request
                request = self.request_factory(environ)
                threadlocals['request'] = request
                request.registry = registry
                response = self.handle_request(request)

            finally:
                if request is not None and request.finished_callbacks:
                    request._process_finished_callbacks()

            return response(request.environ, start_response)

        finally:
            manager.pop()

