import sys
from webob import Request as WebObRequest

from zope.component.event import dispatch

from zope.interface import implements

from repoze.bfg.events import NewRequest
from repoze.bfg.events import NewResponse
from repoze.bfg.events import WSGIApplicationCreatedEvent

from repoze.bfg.interfaces import ILogger
from repoze.bfg.interfaces import INotFoundAppFactory
from repoze.bfg.interfaces import IRequestFactory
from repoze.bfg.interfaces import IRootFactory
from repoze.bfg.interfaces import IRouter
from repoze.bfg.interfaces import IRoutesMapper
from repoze.bfg.interfaces import ISecurityPolicy
from repoze.bfg.interfaces import ISettings
from repoze.bfg.interfaces import IForbiddenResponseFactory
from repoze.bfg.interfaces import IUnauthorizedAppFactory
from repoze.bfg.interfaces import IView
from repoze.bfg.interfaces import IViewPermission

from repoze.bfg.log import make_stream_logger

from repoze.bfg.registry import Registry
from repoze.bfg.registry import registry_manager
from repoze.bfg.registry import populateRegistry

from repoze.bfg.request import HTTP_METHOD_FACTORIES
from repoze.bfg.request import Request

from repoze.bfg.settings import Settings

from repoze.bfg.urldispatch import RoutesRootFactory

from repoze.bfg.traversal import _traverse
from repoze.bfg.view import _view_execution_permitted
from repoze.bfg.wsgi import Unauthorized
from repoze.bfg.wsgi import NotFound

_marker = object()

class Router(object):
    """ The main repoze.bfg WSGI application. """
    implements(IRouter)

    debug_authorization = False
    debug_notfound = False

    def __init__(self, registry):
        self.registry = registry
        self.logger = registry.queryUtility(ILogger, 'repoze.bfg.debug')

        self.request_factory = registry.queryUtility(IRequestFactory)
        security_policy = registry.queryUtility(ISecurityPolicy)

        unauthorized_app_factory = registry.queryUtility(
            IUnauthorizedAppFactory)

        forbidden = None

        if unauthorized_app_factory is not None:
            warning = (
                'Instead of registering a utility against the '
                'repoze.bfg.interfaces.IUnauthorizedAppFactory interface '
                'to return a custom forbidden response, you should now '
                'register a "repoze.interfaces.IForbiddenResponseFactory".  '
                'The IUnauthorizedAppFactory interface was deprecated in '
                'repoze.bfg 0.8.2 and will be removed in a subsequent version '
                'of repoze.bfg.  See the "Hooks" chapter of the repoze.bfg '
                'documentation for more information about '
                'IForbiddenResponseFactory.')
            self.logger and self.logger.warn(warning)
            def forbidden(context, request):
                app = unauthorized_app_factory()
                response = request.get_response(app)
                return response

        self.forbidden_resp_factory = registry.queryUtility(
            IForbiddenResponseFactory,
            default=forbidden)

        if security_policy is not None:
            if hasattr(security_policy, 'forbidden'):
                security_policy_forbidden = security_policy.forbidden
            else:
                security_policy_forbidden = Unauthorized
                warning = ('You are running with a security policy (%s) which '
                           'does not have a "forbidden" method; in BFG 0.8.2+ '
                           'the ISecurityPolicy interface in the '
                           'repoze.bfg.interfaces module defines this method '
                           'as required; your application will not work under '
                           'a future release of BFG if you continue using a '
                           'security policy without a "forbidden" method.' %
                           security_policy)
                self.logger and self.logger.warn(warning)
            # allow a specifically-registered IForbiddenResponseFactory to
            # override the security policy's forbidden
            self.forbidden_resp_factory = (self.forbidden_resp_factory or
                                           security_policy_forbidden)

        self.security_policy = security_policy
        self.notfound_app_factory = registry.queryUtility(INotFoundAppFactory,
                                                          default=NotFound)
        settings = registry.queryUtility(ISettings)
        if settings is not None:
            self.debug_authorization = settings.debug_authorization
            self.debug_notfound = settings.debug_notfound
            
        self.root_factory = registry.getUtility(IRootFactory)
        self.root_policy = self.root_factory # b/w compat
        self.traverser_warned = {}

    def __call__(self, environ, start_response):
        """
        Accept ``environ`` and ``start_response``; route requests to
        ``repoze.bfg`` views based on registrations within the
        application registry; call ``start_response`` and return an
        iterable.
        """
        registry = self.registry
        registry_manager.push(registry)

        try:
            if self.request_factory is None:
                method = environ['REQUEST_METHOD']
                try:
                    # for speed we disuse HTTP_METHOD_FACTORIES.get
                    request_factory = HTTP_METHOD_FACTORIES[method]
                except KeyError:
                    request_factory = Request
            else:
                request_factory = self.request_factory

            request = request_factory(environ)
            
            registry.has_listeners and registry.notify(NewRequest(request))
            root = self.root_factory(environ)
            tdict = _traverse(root, environ)
            if '_deprecation_warning' in tdict:
                warning = tdict.pop('_deprecation_warning')
                if not warning in self.traverser_warned:
                    self.logger and self.logger.warn(warning)
            context, view_name, subpath, traversed, vroot, vroot_path = (
                tdict['context'], tdict['view_name'], tdict['subpath'],
                tdict['traversed'], tdict['virtual_root'],
                tdict['virtual_root_path'])

            if isinstance(request, WebObRequest):
                # webob.Request's __setattr__ (as of 0.9.5 and lower)
                # is a bottleneck; if we're sure we're using a
                # webob.Request, go around its back and set stuff into
                # the environ directly
                attrs = environ.setdefault('webob.adhoc_attrs', {})
                attrs.update(tdict)
            else:
                request.root = root
                request.context = context
                request.view_name = view_name
                request.subpath = subpath
                request.traversed = traversed
                request.virtual_root = vroot
                request.virtual_root_path = vroot_path

            security_policy = self.security_policy

            permission = None

            if security_policy is not None:
                permission = registry.queryMultiAdapter((context, request),
                                                        IViewPermission,
                                                        name=view_name)

            debug_authorization = self.debug_authorization

            permitted = _view_execution_permitted(context, request, view_name,
                                                  security_policy, permission,
                                                  debug_authorization)

            logger = self.logger

            if debug_authorization:
                logger and logger.debug(
                    'debug_authorization of url %s (view name %r against '
                    'context %r): %s' % (
                    request.url, view_name, context, permitted)
                    )

            if not permitted:
                if debug_authorization:
                    msg = str(permitted)
                else:
                    msg = 'Unauthorized: failed security policy check'

                environ['repoze.bfg.message'] = msg

                response = self.forbidden_resp_factory(context, request)
                start_response(response.status, response.headerlist)
                return response.app_iter

            response = registry.queryMultiAdapter(
                (context, request), IView, name=view_name)

            if response is None:
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
                    msg = request.url
                environ['repoze.bfg.message'] = msg
                notfound_app = self.notfound_app_factory()
                return notfound_app(environ, start_response)

            registry.has_listeners and registry.notify(NewResponse(response))

            try:
                start_response(response.status, response.headerlist)
                return response.app_iter
            except AttributeError:
                raise ValueError(
                    'Non-response object returned from view: %r' % response)

        finally:
            registry_manager.pop()

def make_app(root_factory, package=None, filename='configure.zcml',
             options=None):
    """ Return a Router object, representing a ``repoze.bfg`` WSGI
    application.  ``root_factory`` must be a callable that accepts a
    WSGI environment and returns a root object.  ``package`` is a
    Python module representing the application's package, ``filename``
    is the filesystem path to a ZCML file (optionally relative to the
    package path) that should be parsed to create the application
    registry.  ``options``, if used, should be a dictionary containing
    runtime options (e.g. the key/value pairs in an app section of a
    PasteDeploy file), with each key representing the option and the
    key's value representing the specific option value,
    e.g. ``{'reload_templates':True}``"""
    if options is None:
        options = {}
    regname = filename
    if package:
        regname = package.__name__
    registry = Registry(regname)
    debug_logger = make_stream_logger('repoze.bfg.debug', sys.stderr)
    registry.registerUtility(debug_logger, ILogger, 'repoze.bfg.debug')
    settings = Settings(options)
    registry.registerUtility(settings, ISettings)
    mapper = RoutesRootFactory(root_factory)
    registry.registerUtility(mapper, IRoutesMapper)
    populateRegistry(registry, filename, package)
    if mapper.has_routes():
        # if the user had any <route/> statements in his configuration,
        # use the RoutesRootFactory as the root factory
        root_factory = mapper
    else:
        # otherwise, use only the supplied root_factory (unless it's None)
        if root_factory is None:
            raise ValueError(
                'root_factory (aka get_root) was None and no routes connected')

    registry.registerUtility(root_factory, IRootFactory)
    app = Router(registry)

    # We push the registry on to the stack here in case any ZCA API is
    # used in listeners subscribed to the WSGIApplicationCreatedEvent
    # we send.
    registry_manager.push(registry)
    try:
        # use dispatch here instead of registry.notify to make unit
        # tests possible
        dispatch(WSGIApplicationCreatedEvent(app))
    finally:
        registry_manager.pop()

    return app

