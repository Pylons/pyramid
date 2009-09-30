import os
import sys

from zope.interface import implements
from zope.interface import providedBy

from zope.component.event import dispatch

from repoze.bfg.interfaces import IAuthenticationPolicy
from repoze.bfg.interfaces import IAuthorizationPolicy
from repoze.bfg.interfaces import IDefaultRootFactory
from repoze.bfg.interfaces import IForbiddenView
from repoze.bfg.interfaces import ILogger
from repoze.bfg.interfaces import INotFoundView
from repoze.bfg.interfaces import IRootFactory
from repoze.bfg.interfaces import IRouter
from repoze.bfg.interfaces import IRoutesMapper
from repoze.bfg.interfaces import ISettings
from repoze.bfg.interfaces import ITraverserFactory
from repoze.bfg.interfaces import IView

from repoze.bfg.authorization import ACLAuthorizationPolicy
from repoze.bfg.events import NewRequest
from repoze.bfg.events import NewResponse
from repoze.bfg.events import WSGIApplicationCreatedEvent
from repoze.bfg.exceptions import Forbidden
from repoze.bfg.exceptions import NotFound
from repoze.bfg.log import make_stream_logger
from repoze.bfg.registry import Registry
from repoze.bfg.registry import populateRegistry
from repoze.bfg.request import request_factory
from repoze.bfg.settings import Settings
from repoze.bfg.settings import get_options
from repoze.bfg.threadlocal import manager
from repoze.bfg.traversal import ModelGraphTraverser
from repoze.bfg.traversal import _traverse
from repoze.bfg.urldispatch import RoutesRootFactory
from repoze.bfg.view import default_forbidden_view
from repoze.bfg.view import default_notfound_view

_marker = object()

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
        self.root_policy = self.root_factory # b/w compat
        self.registry = registry
        settings = registry.queryUtility(ISettings)
        if settings is not None:
            self.debug_notfound = settings['debug_notfound']
        self.traverser_warned = {}

    def __call__(self, environ, start_response):
        """
        Accept ``environ`` and ``start_response``; route requests to
        ``repoze.bfg`` views based on registrations within the
        application registry; call ``start_response`` and return an
        iterable.
        """
        registry = self.registry
        logger = self.logger
        manager = self.threadlocal_manager
        threadlocals = {'registry':registry, 'request':None}
        manager.push(threadlocals)
 
        try:
            root = self.root_factory(environ)
            request = request_factory(environ)
            threadlocals['request'] = request
            registry.has_listeners and registry.notify(NewRequest(request))
            traverser = registry.queryAdapter(root, ITraverserFactory)
            if traverser is None:
                traverser = ModelGraphTraverser(root)
            tdict = _traverse(root, environ, traverser=traverser)
            context, view_name, subpath, traversed, vroot, vroot_path = (
                tdict['context'], tdict['view_name'], tdict['subpath'],
                tdict['traversed'], tdict['virtual_root'],
                tdict['virtual_root_path'])

            # webob.Request's __setattr__ (as of 0.9.5 and lower) is a
            # bottleneck; since we're sure we're using a
            # webob.Request, we can go around its back and set stuff
            # into the environ directly
            if 'webob.adhoc_attrs' in environ:
                attrs = environ.setdefault('webob.adhoc_attrs', {})
                attrs.update(tdict)
            else:
                environ['webob.adhoc_attrs'] = tdict

            provides = map(providedBy, (context, request))
            view_callable = registry.adapters.lookup(
                provides, IView, name=view_name, default=None)

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
                    environ = getattr(request, 'environ', {})
                    environ['repoze.bfg.message'] = msg
                    response = self.forbidden_view(context, request)
                except NotFound, why:
                    msg = why[0]
                    environ = getattr(request, 'environ', {})
                    environ['repoze.bfg.message'] = msg
                    response = self.notfound_view(context, request)

            registry.has_listeners and registry.notify(NewResponse(response))

            try:
                start_response(response.status, response.headerlist)
                return response.app_iter
            except AttributeError:
                raise ValueError(
                    'Non-response object returned from view named %s '
                    '(and no renderer): %r' % (view_name, response))

        finally:
            manager.pop()

def make_app(root_factory, package=None, filename='configure.zcml',
             authentication_policy=None, authorization_policy=None,
             options=None, registry=None, debug_logger=None,
             manager=manager, os=os):
    # registry, debug_logger, manager and os *only* for unittests
    """ Return a Router object, representing a fully configured
    ``repoze.bfg`` WSGI application.

    ``root_factory`` must be a callable that accepts a WSGI
    environment and returns a traversal root object.  The traversal
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

    ``options``, if used, should be a dictionary containing runtime
    options (e.g. the key/value pairs in an app section of a
    PasteDeploy file), with each key representing the option and the
    key's value representing the specific option value,
    e.g. ``{'reload_templates':True}``"""
    if options is None:
        options = {}

    if not 'configure_zcml' in options:
        options['configure_zcml'] = filename

    settings = Settings(get_options(options))
    filename = settings['configure_zcml']

    # not os.path.isabs below for windows systems
    if (':' in filename) and (not os.path.isabs(filename)):
        package, filename = filename.split(':', 1)
        __import__(package)
        package = sys.modules[package]

    if registry is None:
        regname = filename
        if package:
            regname = package.__name__
        registry = Registry(regname)

    registry.registerUtility(settings, ISettings)

    if debug_logger is None:
        debug_logger = make_stream_logger('repoze.bfg.debug', sys.stderr)
    registry.registerUtility(debug_logger, ILogger, 'repoze.bfg.debug')

    if root_factory is None:
        root_factory = DefaultRootFactory

    # register the *default* root factory so apps can find it later
    registry.registerUtility(root_factory, IDefaultRootFactory)

    mapper = RoutesRootFactory(root_factory)
    registry.registerUtility(mapper, IRoutesMapper)

    if authentication_policy:
        debug_logger.warn(
            'The "authentication_policy" and "authorization_policy" '
            'arguments to repoze.bfg.router.make_app have been deprecated '
            'in repoze.bfg version 1.0.  Instead of using these arguments to '
            'configure an authorization/authentication policy pair, use '
            'a pair of ZCML directives (such as "authtktauthenticationpolicy" '
            'and "aclauthorizationpolicy" documented within the Security '
            'chapter in the BFG documentation.  If you need to use a custom '
            'authentication or authorization policy, you should make a ZCML '
            'directive for it and use that directive within your '
            'application\'s ZCML')
        registry.registerUtility(authentication_policy, IAuthenticationPolicy)
        if authorization_policy is None:
            authorization_policy = ACLAuthorizationPolicy()
        registry.registerUtility(authorization_policy, IAuthorizationPolicy)

    populateRegistry(registry, filename, package)

    if mapper.has_routes():
        # if the user had any <route/> statements in his configuration,
        # use the RoutesRootFactory as the IRootFactory; otherwise use the
        # default root factory (optimization; we don't want to go through
        # the Routes logic if we know there are no routes to match)
        root_factory = mapper

    registry.registerUtility(root_factory, IRootFactory)

    app = Router(registry)

    # We push the registry on to the stack here in case any ZCA API is
    # used in listeners subscribed to the WSGIApplicationCreatedEvent
    # we send.
    manager.push({'registry':registry, 'request':None})
    try:
        # use dispatch here instead of registry.notify to make unit
        # tests possible
        dispatch(WSGIApplicationCreatedEvent(app))
    finally:
        manager.pop()

    return app

class DefaultRootFactory:
    __parent__ = None
    __name__ = None
    def __init__(self, environ):
        if 'bfg.routes.matchdict' in environ:
            # provide backwards compatibility for applications which
            # used routes (at least apps without any custom "context
            # factory") in BFG 0.9.X and before
            self.__dict__.update(environ['bfg.routes.matchdict'])

