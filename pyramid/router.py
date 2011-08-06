import sys

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
from pyramid.interfaces import IRequestHandlerManager

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
        handler_manager = q(IRequestHandlerManager)
        if handler_manager is None:
            self.handle_request = exc_view_handler_factory(self.handle_request,
                                                           registry)
        else:
            self.handle_request = handler_manager(self.handle_request, registry)
            
        self.root_policy = self.root_factory # b/w compat
        self.registry = registry
        settings = registry.settings

        if settings is not None:
            self.debug_notfound = settings['debug_notfound']
            self.debug_routematch = settings['debug_routematch']

    def handle_request(self, request):
        attrs = request.__dict__
        registry = attrs['registry']

        try: # matches finally: if request is not None
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
                                route.predicates)
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

            has_listeners and notify(NewResponse(request, response))

            if request.response_callbacks:
                request._process_response_callbacks(response)

            return request, response

        finally:
            if request is not None and request.finished_callbacks:
                request._process_finished_callbacks()

    def __call__(self, environ, start_response):
        """
        Accept ``environ`` and ``start_response``; create a
        :term:`request` and route the request to a :app:`Pyramid`
        view based on introspection of :term:`view configuration`
        within the application registry; call ``start_response`` and
        return an iterable.
        """
        registry = self.registry
        request = self.request_factory(environ)
        threadlocals = {'registry':registry, 'request':request}
        manager = self.threadlocal_manager
        manager.push(threadlocals)
        try:
            request.registry = registry
            request, response = self.handle_request(request)
            return response(request.environ, start_response)
        finally:
            manager.pop()

def exc_view_handler_factory(handler, registry):
    has_listeners = registry.has_listeners
    adapters = registry.adapters
    notify = registry.notify

    def exception_view_handler(request):
        attrs = request.__dict__
        try:
            request, response = handler(request)
        except Exception, exc:
            # WARNING: do not assign the result of sys.exc_info() to a
            # local var here, doing so will cause a leak
            attrs['exc_info'] = sys.exc_info()
            attrs['exception'] = exc
            # clear old generated request.response, if any; it may
            # have been mutated by the view, and its state is not
            # sane (e.g. caching headers)
            if 'response' in attrs:
                del attrs['response']
            request_iface = attrs['request_iface']
            provides = providedBy(exc)
            for_ = (IExceptionViewClassifier, request_iface.combined, provides)
            view_callable = adapters.lookup(for_, IView, default=None)
            if view_callable is None:
                raise
            response = view_callable(exc, request)
            has_listeners and notify(NewResponse(request, response))
        finally:
            attrs['exc_info'] = None
            attrs['exception'] = None
        return request, response

    return exception_view_handler

