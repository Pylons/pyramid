from zope.interface import implementer, providedBy

from pyramid.interfaces import (
    IDebugLogger,
    IExecutionPolicy,
    IRequest,
    IRequestExtensions,
    IRootFactory,
    IRouteRequest,
    IRouter,
    IRequestFactory,
    IRoutesMapper,
    ITraverser,
    ITweens,
)

from pyramid.events import (
    ContextFound,
    NewRequest,
    NewResponse,
    BeforeTraversal,
)

from pyramid.httpexceptions import HTTPNotFound
from pyramid.request import Request
from pyramid.view import _call_view
from pyramid.request import apply_request_extensions
from pyramid.threadlocal import RequestContext

from pyramid.traversal import DefaultRootFactory, ResourceTreeTraverser


@implementer(IRouter)
class Router(object):

    debug_notfound = False
    debug_routematch = False

    def __init__(self, registry):
        q = registry.queryUtility
        self.logger = q(IDebugLogger)
        self.root_factory = q(IRootFactory, default=DefaultRootFactory)
        self.routes_mapper = q(IRoutesMapper)
        self.request_factory = q(IRequestFactory, default=Request)
        self.request_extensions = q(IRequestExtensions)
        self.execution_policy = q(
            IExecutionPolicy, default=default_execution_policy
        )
        self.orig_handle_request = self.handle_request
        tweens = q(ITweens)
        if tweens is not None:
            self.handle_request = tweens(self.handle_request, registry)
        self.root_policy = self.root_factory  # b/w compat
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
                    msg = 'no route matched for url %s' % request.url
                    logger and logger.debug(msg)
            else:
                attrs['matchdict'] = match
                attrs['matched_route'] = route

                if debug_routematch:
                    msg = (
                        'route matched for url %s; '
                        'route_name: %r, '
                        'path_info: %r, '
                        'pattern: %r, '
                        'matchdict: %r, '
                        'predicates: %r'
                        % (
                            request.url,
                            route.name,
                            request.path_info,
                            route.pattern,
                            match,
                            ', '.join([p.text() for p in route.predicates]),
                        )
                    )
                    logger and logger.debug(msg)

                request.request_iface = registry.queryUtility(
                    IRouteRequest, name=route.name, default=IRequest
                )

                root_factory = route.factory or self.root_factory

        # Notify anyone listening that we are about to start traversal
        #
        # Notify before creating root_factory in case we want to do something
        # special on a route we may have matched. See
        # https://github.com/Pylons/pyramid/pull/1876 for ideas of what is
        # possible.
        has_listeners and notify(BeforeTraversal(request))

        # Create the root factory
        root = root_factory(request)
        attrs['root'] = root

        # We are about to traverse and find a context
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
            tdict['virtual_root_path'],
        )

        attrs.update(tdict)

        # Notify anyone listening that we have a context and traversal is
        # complete
        has_listeners and notify(ContextFound(request))

        # find a view callable
        context_iface = providedBy(context)
        response = _call_view(
            registry, request, context, context_iface, view_name
        )

        if response is None:
            if self.debug_notfound:
                msg = (
                    'debug_notfound of url %s; path_info: %r, '
                    'context: %r, view_name: %r, subpath: %r, '
                    'traversed: %r, root: %r, vroot: %r, '
                    'vroot_path: %r'
                    % (
                        request.url,
                        request.path_info,
                        context,
                        view_name,
                        subpath,
                        traversed,
                        root,
                        vroot,
                        vroot_path,
                    )
                )
                logger and logger.debug(msg)
            else:
                msg = request.path_info
            raise HTTPNotFound(msg)

        return response

    def invoke_subrequest(self, request, use_tweens=False):
        """Obtain a response object from the Pyramid application based on
        information in the ``request`` object provided.  The ``request``
        object must be an object that implements the Pyramid request
        interface (such as a :class:`pyramid.request.Request` instance).  If
        ``use_tweens`` is ``True``, the request will be sent to the
        :term:`tween` in the tween stack closest to the request ingress.  If
        ``use_tweens`` is ``False``, the request will be sent to the main
        router handler, and no tweens will be invoked.

        See the API for pyramid.request for complete documentation.
        """
        request.registry = self.registry
        request.invoke_subrequest = self.invoke_subrequest
        extensions = self.request_extensions
        if extensions is not None:
            apply_request_extensions(request, extensions=extensions)
        with RequestContext(request):
            return self.invoke_request(request, _use_tweens=use_tweens)

    def request_context(self, environ):
        """
        Create a new request context from a WSGI environ.

        The request context is used to push/pop the threadlocals required
        when processing the request. It also contains an initialized
        :class:`pyramid.interfaces.IRequest` instance using the registered
        :class:`pyramid.interfaces.IRequestFactory`. The context may be
        used as a context manager to control the threadlocal lifecycle:

        .. code-block:: python

            with router.request_context(environ) as request:
                ...

        Alternatively, the context may be used without the ``with`` statement
        by manually invoking its ``begin()`` and ``end()`` methods.

        .. code-block:: python

            ctx = router.request_context(environ)
            request = ctx.begin()
            try:
                ...
            finally:
                ctx.end()

        """
        request = self.request_factory(environ)
        request.registry = self.registry
        request.invoke_subrequest = self.invoke_subrequest
        extensions = self.request_extensions
        if extensions is not None:
            apply_request_extensions(request, extensions=extensions)
        return RequestContext(request)

    def invoke_request(self, request, _use_tweens=True):
        """
        Execute a request through the request processing pipeline and
        return the generated response.

        """
        registry = self.registry
        has_listeners = registry.has_listeners
        notify = registry.notify

        if _use_tweens:
            handle_request = self.handle_request
        else:
            handle_request = self.orig_handle_request

        try:
            response = handle_request(request)

            if request.response_callbacks:
                request._process_response_callbacks(response)

            has_listeners and notify(NewResponse(request, response))

            return response

        finally:
            if request.finished_callbacks:
                request._process_finished_callbacks()

    def __call__(self, environ, start_response):
        """
        Accept ``environ`` and ``start_response``; create a
        :term:`request` and route the request to a :app:`Pyramid`
        view based on introspection of :term:`view configuration`
        within the application registry; call ``start_response`` and
        return an iterable.
        """
        response = self.execution_policy(environ, self)
        return response(environ, start_response)


def default_execution_policy(environ, router):
    with router.request_context(environ) as request:
        try:
            return router.invoke_request(request)
        except Exception:
            return request.invoke_exception_view(reraise=True)
