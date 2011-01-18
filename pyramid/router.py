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

from pyramid.events import ContextFound
from pyramid.events import NewRequest
from pyramid.events import NewResponse
from pyramid.exceptions import NotFound
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
        self.root_policy = self.root_factory # b/w compat
        self.registry = registry
        settings = registry.settings

        if settings is not None:
            self.debug_notfound = settings['debug_notfound']
            self.debug_routematch = settings['debug_routematch']

    def __call__(self, environ, start_response):
        """
        Accept ``environ`` and ``start_response``; create a
        :term:`request` and route the request to a :app:`Pyramid`
        view based on introspection of :term:`view configuration`
        within the application registry; call ``start_response`` and
        return an iterable.
        """
        registry = self.registry
        adapters = registry.adapters
        has_listeners = registry.has_listeners
        logger = self.logger
        manager = self.threadlocal_manager
        request = None
        threadlocals = {'registry':registry, 'request':request}
        manager.push(threadlocals)

        try: # matches finally: manager.pop()

            try: # matches finally:  ... call request finished callbacks ...
                
                # create the request
                request = self.request_factory(environ)
                context = None
                threadlocals['request'] = request
                attrs = request.__dict__
                attrs['registry'] = registry
                has_listeners and registry.notify(NewRequest(request))
                request_iface = IRequest

                try:
                    # find the root object
                    root_factory = self.root_factory
                    if self.routes_mapper is not None:
                        info = self.routes_mapper(request)
                        match, route = info['match'], info['route']
                        if route is None:
                            if self.debug_routematch:
                                msg = ('no route matched for url %s' %
                                       request.url)
                                logger and logger.debug(msg)
                        else:
                            # TODO: kill off bfg.routes.* environ keys when
                            # traverser requires request arg, and cant cope
                            # with environ anymore (they are docs-deprecated as
                            # of BFG 1.3)
                            environ['bfg.routes.route'] = route 
                            environ['bfg.routes.matchdict'] = match
                            attrs['matchdict'] = match
                            attrs['matched_route'] = route

                            if self.debug_routematch:
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
                            root_factory = route.factory or self.root_factory

                    root = root_factory(request)
                    attrs['root'] = root

                    # find a context
                    traverser = adapters.queryAdapter(root, ITraverser)
                    if traverser is None:
                        traverser = ResourceTreeTraverser(root)
                    tdict = traverser(request)
                    context, view_name, subpath, traversed, vroot, vroot_path =(
                        tdict['context'], tdict['view_name'], tdict['subpath'],
                        tdict['traversed'], tdict['virtual_root'],
                        tdict['virtual_root_path'])
                    attrs.update(tdict)
                    has_listeners and registry.notify(ContextFound(request))

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
                                    subpath, traversed, root, vroot, vroot_path)
                                )
                            logger and logger.debug(msg)
                        else:
                            msg = request.path_info
                        raise NotFound(msg)
                    else:
                        response = view_callable(context, request)

                # handle exceptions raised during root finding and view-exec
                except Exception, why:
                    attrs['exception'] = why

                    for_ = (IExceptionViewClassifier,
                            request_iface.combined,
                            providedBy(why))
                    view_callable = adapters.lookup(for_, IView, default=None)

                    if view_callable is None:
                        raise

                    try: 
                        msg = why[0]
                    except:
                        msg = ''

                    # repoze.bfg.message docs-deprecated in Pyramid 1.0
                    environ['repoze.bfg.message'] = msg

                    response = view_callable(why, request)

                # process the response

                has_listeners and registry.notify(NewResponse(request,response))

                if request.response_callbacks:
                    request._process_response_callbacks(response)

                try:
                    headers = response.headerlist
                    app_iter = response.app_iter
                    status = response.status
                except AttributeError:
                    raise ValueError(
                        'Non-response object returned from view named %s '
                        '(and no renderer): %r' % (view_name, response))

            finally:
                if request is not None and request.finished_callbacks:
                    request._process_finished_callbacks()

            start_response(status, headers)
            return app_iter
            
        finally:
            manager.pop()
