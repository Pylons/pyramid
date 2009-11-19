import os
import re
import sys
import threading
import inspect

from webob import Response

import zope.component

from zope.configuration.exceptions import ConfigurationError
from zope.configuration import xmlconfig

from zope.component import getGlobalSiteManager
from zope.component import getSiteManager
from zope.component import queryUtility

from zope.interface import Interface
from zope.interface import implementedBy
from zope.interface.interfaces import IInterface
from zope.interface import implements

from repoze.bfg.interfaces import IAuthenticationPolicy
from repoze.bfg.interfaces import IAuthorizationPolicy
from repoze.bfg.interfaces import IDefaultRootFactory
from repoze.bfg.interfaces import IForbiddenView
from repoze.bfg.interfaces import ILogger
from repoze.bfg.interfaces import IMultiView
from repoze.bfg.interfaces import INotFoundView
from repoze.bfg.interfaces import IPackageOverrides
from repoze.bfg.interfaces import IRendererFactory
from repoze.bfg.interfaces import IRequest
from repoze.bfg.interfaces import IResponseFactory
from repoze.bfg.interfaces import IRootFactory
from repoze.bfg.interfaces import IRouteRequest
from repoze.bfg.interfaces import IRoutesMapper
from repoze.bfg.interfaces import ISettings
from repoze.bfg.interfaces import ISecuredView
from repoze.bfg.interfaces import ITemplateRendererFactory
from repoze.bfg.interfaces import IView

from repoze.bfg import chameleon_zpt
from repoze.bfg import chameleon_text
from repoze.bfg import renderers
from repoze.bfg.compat import all
from repoze.bfg.events import WSGIApplicationCreatedEvent
from repoze.bfg.exceptions import Forbidden
from repoze.bfg.exceptions import NotFound
from repoze.bfg.log import make_stream_logger
from repoze.bfg.registry import Registry
from repoze.bfg.request import route_request_iface
from repoze.bfg.resource import PackageOverrides
from repoze.bfg.settings import Settings
from repoze.bfg.settings import get_settings
from repoze.bfg.static import StaticRootFactory
from repoze.bfg.threadlocal import get_current_registry
from repoze.bfg.threadlocal import manager
from repoze.bfg.traversal import find_interface
from repoze.bfg.traversal import DefaultRootFactory
from repoze.bfg.urldispatch import RoutesMapper
from repoze.bfg.view import render_view_to_response
from repoze.bfg.view import static as static_view

import martian

class Configurator(object):
    """ A wrapper around the registry that performs configuration tasks """
    def __init__(self, registry=None):
        if registry is None:
            registry = self.make_default_registry()
        self.reg = registry

    def make_default_registry(self):
        self.reg = Registry()
        self.renderer(chameleon_zpt.renderer_factory, '.pt')
        self.renderer(chameleon_text.renderer_factory, '.txt')
        self.renderer(renderers.json_renderer_factory, 'json')
        self.renderer(renderers.string_renderer_factory, 'string')
        settings = Settings({})
        self.settings(settings)
        self.root_factory(DefaultRootFactory)
        self.debug_logger(None)
        return self.reg

    def make_wsgi_app(self, manager=manager, getSiteManager=getSiteManager):
        # manager and getSiteManager in arglist for testing dep injection only
        from repoze.bfg.router import Router # avoid circdep
        app = Router(self.reg)
        # executing sethook means we're taking over getSiteManager for
        # the lifetime of this process
        getSiteManager.sethook(get_current_registry)
        # We push the registry on to the stack here in case any ZCA API is
        # used in listeners subscribed to the WSGIApplicationCreatedEvent
        # we send.
        manager.push({'registry':self.reg, 'request':None})
        try:
            self.reg.notify(WSGIApplicationCreatedEvent(app))
        finally:
            manager.pop()
        return app

    def declarative(self, root_factory, package=None,
                    filename='configure.zcml', settings=None,
                    debug_logger=None, os=os, lock=threading.Lock()):

        self.make_default_registry()

        # debug_logger, os and lock *only* for unittests
        if settings is None:
            settings = {}

        if not 'configure_zcml' in settings:
            settings['configure_zcml'] = filename

        settings = Settings(settings)
        filename = settings['configure_zcml']

        # not os.path.isabs below for windows systems
        if (':' in filename) and (not os.path.isabs(filename)):
            package, filename = filename.split(':', 1)
            __import__(package)
            package = sys.modules[package]

        self.settings(settings)
        self.debug_logger(debug_logger)
        self.root_factory(root_factory or DefaultRootFactory)
        self.load_zcml(filename, package, lock=lock)

    def load_zcml(self, filename, package=None, lock=threading.Lock()):
        # We push our ZCML-defined configuration into an app-local
        # component registry in order to allow more than one bfg app to live
        # in the same process space without one unnecessarily stomping on
        # the other's component registrations (although I suspect directives
        # that have side effects are going to fail).  The only way to do
        # that currently is to override zope.component.getGlobalSiteManager
        # for the duration of the ZCML includes.  We acquire a lock in case
        # another make_app runs in a different thread simultaneously, in a
        # vain attempt to prevent mixing of registrations.  There's not much
        # we can do about non-makeRegistry code that tries to use the global
        # site manager API directly in a different thread while we hold the
        # lock.  Those registrations will end up in our application's
        # registry.
        lock.acquire()
        manager.push({'registry':self.reg, 'request':None})
        try:
            getSiteManager.sethook(get_current_registry)
            zope.component.getGlobalSiteManager = get_current_registry
            xmlconfig.file(filename, package, execute=True)
        finally:
            zope.component.getGlobalSiteManager = getGlobalSiteManager
            lock.release()
            manager.pop()
            getSiteManager.reset()

    def view(self, view=None, name="", for_=None, permission=None, 
             request_type=None, route_name=None, request_method=None,
             request_param=None, containment=None, attr=None,
             renderer=None, wrapper=None, xhr=False, accept=None,
             header=None, path_info=None, _info=u''):

        if not view:
            if renderer:
                def view(context, request):
                    return {}
            else:
                raise ConfigurationError('"view" was not specified and '
                                         'no "renderer" specified')

        if request_type and route_name:
            raise ConfigurationError(
                'A view cannot be configured with both the request_type and '
                'route_name parameters: these two features when used together '
                'causes an internal conflict.')

        if request_type is None:
            request_type = IRequest

        if route_name is not None:
            request_type = self.reg.queryUtility(IRouteRequest,
                                                 name=route_name)
            if request_type is None:
                request_type = route_request_iface(route_name)
                self.reg.registerUtility(request_type, IRouteRequest,
                                         name=route_name)

        score, predicates = _make_predicates(
            xhr=xhr, request_method=request_method, path_info=path_info,
            request_param=request_param, header=header, accept=accept,
            containment=containment)

        derived_view = self.derive_view(view, permission, predicates, attr,
                                        renderer, wrapper, name)
        r_for_ = for_
        r_request_type = request_type
        if r_for_ is None:
            r_for_ = Interface
        if not IInterface.providedBy(r_for_):
            r_for_ = implementedBy(r_for_)
        if not IInterface.providedBy(r_request_type):
            r_request_type = implementedBy(r_request_type)
        old_view = self.reg.adapters.lookup((r_for_, r_request_type),
                                            IView, name=name)
        if old_view is None:
            if hasattr(derived_view, '__call_permissive__'):
                view_iface = ISecuredView
            else:
                view_iface = IView
            self.reg.registerAdapter(derived_view, (for_, request_type),
                                     view_iface, name, info=_info)
        else:
            # XXX we could try to be more efficient here and register
            # a non-secured view for a multiview if none of the
            # multiview's consituent views have a permission
            # associated with them, but this code is getting pretty
            # rough already
            if IMultiView.providedBy(old_view):
                multiview = old_view
            else:
                multiview = MultiView(name)
                multiview.add(old_view, sys.maxint)
            multiview.add(derived_view, score)
            for i in (IView, ISecuredView):
                # unregister any existing views
                self.reg.adapters.unregister((r_for_, r_request_type), i,
                                             name=name)
            self.reg.registerAdapter(multiview, (for_, request_type),
                                     IMultiView, name, info=_info)

    def renderer_from_name(self, path):
        name = os.path.splitext(path)[1]
        if not name:
            name = path
        factory = self.reg.queryUtility(IRendererFactory, name=name)
        if factory is None:
            raise ValueError('No renderer for renderer name %r' % name)
        return factory(path)

    def derive_view(self, original_view, permission=None, predicates=(),
                    attr=None, renderer_name=None, wrapper_viewname=None,
                    viewname=None):
        mapped_view = self._map_view(original_view, attr, renderer_name)
        owrapped_view = self._owrap_view(mapped_view, viewname,wrapper_viewname)
        secured_view = self._secure_view(owrapped_view, permission)
        debug_view = self._authdebug_view(secured_view, permission)
        derived_view = self._predicate_wrap(debug_view, predicates)
        return derived_view

    def _map_view(self, view, attr=None, renderer_name=None):
        wrapped_view = view

        renderer = None

        if renderer_name is None:
            # global default renderer
            factory = self.reg.queryUtility(IRendererFactory)
            if factory is not None:
                renderer_name = ''
                renderer = factory(renderer_name)
        else:
            renderer = self.renderer_from_name(renderer_name)

        if inspect.isclass(view):
            # If the object we've located is a class, turn it into a
            # function that operates like a Zope view (when it's invoked,
            # construct an instance using 'context' and 'request' as
            # position arguments, then immediately invoke the __call__
            # method of the instance with no arguments; __call__ should
            # return an IResponse).
            if requestonly(view, attr):
                # its __init__ accepts only a single request argument,
                # instead of both context and request
                def _bfg_class_requestonly_view(context, request):
                    inst = view(request)
                    if attr is None:
                        response = inst()
                    else:
                        response = getattr(inst, attr)()
                    if renderer is not None:
                        response = rendered_response(renderer, 
                                                     response, inst,
                                                     context, request,
                                                     renderer_name)
                    return response
                wrapped_view = _bfg_class_requestonly_view
            else:
                # its __init__ accepts both context and request
                def _bfg_class_view(context, request):
                    inst = view(context, request)
                    if attr is None:
                        response = inst()
                    else:
                        response = getattr(inst, attr)()
                    if renderer is not None:
                        response = rendered_response(renderer, 
                                                     response, inst,
                                                     context, request,
                                                     renderer_name)
                    return response
                wrapped_view = _bfg_class_view

        elif requestonly(view, attr):
            # its __call__ accepts only a single request argument,
            # instead of both context and request
            def _bfg_requestonly_view(context, request):
                if attr is None:
                    response = view(request)
                else:
                    response = getattr(view, attr)(request)

                if renderer is not None:
                    response = rendered_response(renderer,
                                                 response, view,
                                                 context, request,
                                                 renderer_name)
                return response
            wrapped_view = _bfg_requestonly_view

        elif attr:
            def _bfg_attr_view(context, request):
                response = getattr(view, attr)(context, request)
                if renderer is not None:
                    response = rendered_response(renderer, 
                                                 response, view,
                                                 context, request,
                                                 renderer_name)
                return response
            wrapped_view = _bfg_attr_view

        elif renderer is not None:
            def _rendered_view(context, request):
                response = view(context, request)
                response = rendered_response(renderer, 
                                             response, view,
                                             context, request,
                                             renderer_name)
                return response
            wrapped_view = _rendered_view

        decorate_view(wrapped_view, view)
        return wrapped_view

    def _owrap_view(self, view, viewname, wrapper_viewname):
        if not wrapper_viewname:
            return view
        def _owrapped_view(context, request):
            response = view(context, request)
            request.wrapped_response = response
            request.wrapped_body = response.body
            request.wrapped_view = view
            wrapped_response = render_view_to_response(context, request,
                                                       wrapper_viewname)
            if wrapped_response is None:
                raise ValueError(
                    'No wrapper view named %r found when executing view '
                    'named %r' % (wrapper_viewname, viewname))
            return wrapped_response
        decorate_view(_owrapped_view, view)
        return _owrapped_view

    def _predicate_wrap(self, view, predicates):
        if not predicates:
            return view
        def _wrapped(context, request):
            if all((predicate(context, request) for predicate in predicates)):
                return view(context, request)
            raise NotFound('predicate mismatch for view %s' % view)
        def checker(context, request):
            return all((predicate(context, request) for predicate in
                        predicates))
        _wrapped.__predicated__ = checker
        decorate_view(_wrapped, view)
        return _wrapped

    def _secure_view(self, view, permission):
        wrapped_view = view
        authn_policy = self.reg.queryUtility(IAuthenticationPolicy)
        authz_policy = self.reg.queryUtility(IAuthorizationPolicy)
        if authn_policy and authz_policy and (permission is not None):
            def _secured_view(context, request):
                principals = authn_policy.effective_principals(request)
                if authz_policy.permits(context, principals, permission):
                    return view(context, request)
                msg = getattr(request, 'authdebug_message',
                              'Unauthorized: %s failed permission check' % view)
                raise Forbidden(msg)
            _secured_view.__call_permissive__ = view
            def _permitted(context, request):
                principals = authn_policy.effective_principals(request)
                return authz_policy.permits(context, principals, permission)
            _secured_view.__permitted__ = _permitted
            wrapped_view = _secured_view
            decorate_view(wrapped_view, view)

        return wrapped_view

    def _authdebug_view(self, view, permission):
        wrapped_view = view
        authn_policy = self.reg.queryUtility(IAuthenticationPolicy)
        authz_policy = self.reg.queryUtility(IAuthorizationPolicy)
        settings = get_settings()
        debug_authorization = False
        if settings is not None:
            debug_authorization = settings.get('debug_authorization', False)
        if debug_authorization:
            def _authdebug_view(context, request):
                view_name = getattr(request, 'view_name', None)

                if authn_policy and authz_policy:
                    if permission is None:
                        msg = 'Allowed (no permission registered)'
                    else:
                        principals = authn_policy.effective_principals(request)
                        msg = str(authz_policy.permits(context, principals,
                                                       permission))
                else:
                    msg = 'Allowed (no authorization policy in use)'

                view_name = getattr(request, 'view_name', None)
                url = getattr(request, 'url', None)
                msg = ('debug_authorization of url %s (view name %r against '
                       'context %r): %s' % (url, view_name, context, msg))
                logger = self.reg.queryUtility(ILogger, 'repoze.bfg.debug')
                logger and logger.debug(msg)
                if request is not None:
                    request.authdebug_message = msg
                return view(context, request)

            wrapped_view = _authdebug_view
            decorate_view(wrapped_view, view)

        return wrapped_view

    def route(self, name, path, view=None, view_for=None,
              permission=None, factory=None, for_=None,
              header=None, xhr=False, accept=None, path_info=None,
              request_method=None, request_param=None, 
              view_permission=None, view_request_method=None,
              view_request_param=None,
              view_containment=None, view_attr=None,
              renderer=None, view_renderer=None, view_header=None, 
              view_accept=None, view_xhr=False,
              view_path_info=None, _info=u''):
        # the strange ordering of the request kw args above is for b/w
        # compatibility purposes.
        # these are route predicates; if they do not match, the next route
        # in the routelist will be tried
        _, predicates = _make_predicates(xhr=xhr,
                                         request_method=request_method,
                                         path_info=path_info,
                                         request_param=request_param,
                                         header=header,
                                         accept=accept)

        request_iface = self.reg.queryUtility(IRouteRequest, name=name)
        if request_iface is None:
            request_iface = route_request_iface(name)
            self.reg.registerUtility(request_iface, IRouteRequest, name=name)

        if view:
            view_for = view_for or for_
            view_permission = view_permission or permission
            view_renderer = view_renderer or renderer
            self.view(
                permission=view_permission,
                for_=view_for,
                view=view,
                name='',
                route_name=name, 
                request_method=view_request_method,
                request_param=view_request_param,
                containment=view_containment,
                attr=view_attr,
                renderer=view_renderer,
                header=view_header,
                accept=view_accept,
                xhr=view_xhr,
                path_info=view_path_info,
                _info=_info,
                )

        mapper = self.reg.queryUtility(IRoutesMapper)
        if mapper is None:
            mapper = RoutesMapper()
            self.reg.registerUtility(mapper, IRoutesMapper)
        mapper.connect(path, name, factory, predicates=predicates)

    def scan(self, package, _info=u'', martian=martian):
        # martian overrideable only for unit tests
        multi_grokker = BFGMultiGrokker()
        multi_grokker.register(BFGViewGrokker())
        module_grokker = martian.ModuleGrokker(grokker=multi_grokker)
        martian.grok_dotted_name(
            package.__name__, grokker=module_grokker,
            _info=_info, _configurator=self,
            exclude_filter=lambda name: name.startswith('.'))

    def authentication_policy(self, policy, _info=u''):
        self.reg.registerUtility(policy, IAuthenticationPolicy, info=_info)
        
    def authorization_policy(self, policy, _info=u''):
        self.reg.registerUtility(policy, IAuthorizationPolicy, info=_info)

    def renderer(self, factory, name, _info=u''):
        iface = IRendererFactory
        if name.startswith('.'):
            iface = ITemplateRendererFactory
        self.reg.registerUtility(factory, iface, name=name, info=_info)

    def resource(self, to_override, override_with, _info=u'', _override=None,):
        if to_override == override_with:
            raise ConfigurationError('You cannot override a resource with '
                                     'itself')

        package = to_override
        path = ''
        if ':' in to_override:
            package, path = to_override.split(':', 1)

        override_package = override_with
        override_prefix = ''
        if ':' in override_with:
            override_package, override_prefix = override_with.split(':', 1)

        if path and path.endswith('/'):
            if override_prefix and (not override_prefix.endswith('/')):
                raise ConfigurationError(
                    'A directory cannot be overridden with a file (put a slash '
                    'at the end of override_with if necessary)')

        if override_prefix and override_prefix.endswith('/'):
            if path and (not path.endswith('/')):
                raise ConfigurationError(
                    'A file cannot be overridden with a directory (put a slash '
                    'at the end of to_override if necessary)')

        __import__(package)
        __import__(override_package)
        package = sys.modules[package]
        override_package = sys.modules[override_package]

        if _override is not None:
            _override(package, path, override_package, override_prefix)
        else:
            self._override(package, path, override_package, override_prefix)

    def _override(self, package, path, override_package, override_prefix,
                  _info=u'', PackageOverrides=PackageOverrides):
            pkg_name = package.__name__
            override_pkg_name = override_package.__name__
            override = self.reg.queryUtility(IPackageOverrides, name=pkg_name)
            if override is None:
                override = PackageOverrides(package)
                self.reg.registerUtility(override, IPackageOverrides,
                                         name=pkg_name, info=_info)
            override.insert(path, override_pkg_name, override_prefix)


    def notfound(self, view=None, attr=None, renderer=None, wrapper=None,
                 _info=u''):
        self.view_utility(view, attr, renderer, wrapper, INotFoundView,
                          _info=_info)

    def forbidden(self, view=None, attr=None, renderer=None, wrapper=None,
                  _info=u''):
        self.view_utility(view, attr, renderer, wrapper,
                          IForbiddenView, _info=_info)

    def view_utility(self, view, attr, renderer, wrapper, iface, _info=u''):
        if not view:
            if renderer:
                def view(context, request):
                    return {}
            else:
                raise ConfigurationError('"view" attribute was not specified '
                                         'and no renderer specified')

        derived_view = self.derive_view(view, attr=attr, renderer_name=renderer,
                                        wrapper_viewname=wrapper)
        self.reg.registerUtility(derived_view, iface, '', info=_info)

    def static(self, name, path, cache_max_age=3600, _info=u''):
        view = static_view(path, cache_max_age=cache_max_age)
        self.route(name, "%s*subpath" % name, view=view,
                   view_for=StaticRootFactory, factory=StaticRootFactory(path),
                   _info=_info)

    def settings(self, settings):
        self.reg.registerUtility(settings, ISettings)

    def debug_logger(self, logger):
        if logger is None:
            logger = make_stream_logger('repoze.bfg.debug', sys.stderr)
        self.reg.registerUtility(logger, ILogger, 'repoze.bfg.debug')

    def root_factory(self, factory):
        self.reg.registerUtility(factory, IRootFactory)
        self.reg.registerUtility(factory, IDefaultRootFactory) # b/c
        
def _make_predicates(xhr=None, request_method=None, path_info=None,
                     request_param=None, header=None, accept=None,
                     containment=None):
    # Predicates are added to the predicate list in (presumed)
    # computation expense order.  All predicates associated with a
    # view must evaluate true for the view to "match" a request.
    # Elsewhere in the code, we evaluate them using a generator
    # expression.  The fastest predicate should be evaluated first,
    # then the next fastest, and so on, as if one returns false, the
    # remainder of the predicates won't need to be evaluated.

    # Each predicate is associated with a weight value.  The weight
    # symbolizes the relative potential "importance" of the predicate
    # to all other predicates.  A larger weight indicates greater
    # importance.  These weights are subtracted from an aggregate
    # 'weight' variable.  The aggregate weight is then divided by the
    # length of the predicate list to compute a "score" for this view.
    # The score represents the ordering in which a "multiview" ( a
    # collection of views that share the same context/request/name
    # triad but differ in other ways via predicates) will attempt to
    # call its set of views.  Views with lower scores will be tried
    # first.  The intent is to a) ensure that views with more
    # predicates are always evaluated before views with fewer
    # predicates and b) to ensure a stable call ordering of views that
    # share the same number of predicates.

    # Views which do not have any predicates get a score of
    # sys.maxint, meaning that they will be tried very last.

    predicates = []
    weight = sys.maxint

    if xhr:
        def xhr_predicate(context, request):
            return request.is_xhr
        weight = weight - 10
        predicates.append(xhr_predicate)

    if request_method is not None:
        def request_method_predicate(context, request):
            return request.method == request_method
        weight = weight - 20
        predicates.append(request_method_predicate)

    if path_info is not None:
        try:
            path_info_val = re.compile(path_info)
        except re.error, why:
            raise ConfigurationError(why[0])
        def path_info_predicate(context, request):
            return path_info_val.match(request.path_info) is not None
        weight = weight - 30
        predicates.append(path_info_predicate)

    if request_param is not None:
        request_param_val = None
        if '=' in request_param:
            request_param, request_param_val = request_param.split('=', 1)
        def request_param_predicate(context, request):
            if request_param_val is None:
                return request_param in request.params
            return request.params.get(request_param) == request_param_val
        weight = weight - 40
        predicates.append(request_param_predicate)

    if header is not None:
        header_name = header
        header_val = None
        if ':' in header:
            header_name, header_val = header.split(':', 1)
            try:
                header_val = re.compile(header_val)
            except re.error, why:
                raise ConfigurationError(why[0])
        def header_predicate(context, request):
            if header_val is None:
                return header_name in request.headers
            val = request.headers.get(header_name)
            return header_val.match(val) is not None
        weight = weight - 50
        predicates.append(header_predicate)

    if accept is not None:
        def accept_predicate(context, request):
            return accept in request.accept
        weight = weight - 60
        predicates.append(accept_predicate)

    if containment is not None:
        def containment_predicate(context, request):
            return find_interface(context, containment) is not None
        weight = weight - 70
        predicates.append(containment_predicate)

    # this will be == sys.maxint if no predicates
    score = weight / (len(predicates) + 1)
    return score, predicates

class BFGViewMarker(object):
    pass

class BFGMultiGrokker(martian.core.MultiInstanceOrClassGrokkerBase):
    def get_bases(self, obj):
        if hasattr(obj, '__bfg_view_settings__'):
            return [BFGViewMarker]
        return []

class BFGViewGrokker(martian.InstanceGrokker):
    martian.component(BFGViewMarker)
    def grok(self, name, obj, **kw):
        config = getattr(obj, '__bfg_view_settings__', [])
        for settings in config:
            config = kw['_configurator']
            info = kw.get('_info', u'')
            config.view(view=obj, _info=info, **settings)
        return bool(config)

class MultiView(object):
    implements(IMultiView)

    def __init__(self, name):
        self.name = name
        self.views = []

    def add(self, view, score):
        self.views.append((score, view))
        self.views.sort()

    def match(self, context, request):
        for score, view in self.views:
            if not hasattr(view, '__predicated__'):
                return view
            if view.__predicated__(context, request):
                return view
        raise NotFound(self.name)

    def __permitted__(self, context, request):
        view = self.match(context, request)
        if hasattr(view, '__permitted__'):
            return view.__permitted__(context, request)
        return True

    def __call_permissive__(self, context, request):
        view = self.match(context, request)
        view = getattr(view, '__call_permissive__', view)
        return view(context, request)

    def __call__(self, context, request):
        for score, view in self.views:
            try:
                return view(context, request)
            except NotFound:
                continue
        raise NotFound(self.name)

def decorate_view(wrapped_view, original_view):
    if wrapped_view is original_view:
        return False
    wrapped_view.__module__ = original_view.__module__
    wrapped_view.__doc__ = original_view.__doc__
    try:
        wrapped_view.__name__ = original_view.__name__
    except AttributeError:
        wrapped_view.__name__ = repr(original_view)
    try:
        wrapped_view.__permitted__ = original_view.__permitted__
    except AttributeError:
        pass
    try:
        wrapped_view.__call_permissive__ = original_view.__call_permissive__
    except AttributeError:
        pass
    try:
        wrapped_view.__predicated__ = original_view.__predicated__
    except AttributeError:
        pass
    return True

def rendered_response(renderer, response, view, context,request,
                      renderer_name):
    if ( hasattr(response, 'app_iter') and hasattr(response, 'headerlist')
         and hasattr(response, 'status') ):
        return response
    result = renderer(response, {'view':view, 'renderer_name':renderer_name,
                                 'context':context, 'request':request})
    response_factory = queryUtility(IResponseFactory, default=Response)
    response = response_factory(result)
    if request is not None: # in tests, it may be None
        attrs = request.__dict__
        content_type = attrs.get('response_content_type', None)
        if content_type is not None:
            response.content_type = content_type
        headerlist = attrs.get('response_headerlist', None)
        if headerlist is not None:
            for k, v in headerlist:
                response.headers.add(k, v)
        status = attrs.get('response_status', None)
        if status is not None:
            response.status = status
        charset = attrs.get('response_charset', None)
        if charset is not None:
            response.charset = charset
        cache_for = attrs.get('response_cache_for', None)
        if cache_for is not None:
            response.cache_expires = cache_for
    return response

def requestonly(class_or_callable, attr=None):
    """ Return true of the class or callable accepts only a request argument,
    as opposed to something that accepts context, request """
    if attr is None:
        attr = '__call__'
    if inspect.isfunction(class_or_callable):
        fn = class_or_callable
    elif inspect.isclass(class_or_callable):
        try:
            fn = class_or_callable.__init__
        except AttributeError:
            return False
    else:
        try:
            fn = getattr(class_or_callable, attr)
        except AttributeError:
            return False

    try:
        argspec = inspect.getargspec(fn)
    except TypeError:
        return False

    args = argspec[0]
    defaults = argspec[3]

    if hasattr(fn, 'im_func'):
        # it's an instance method
        if not args:
            return False
        args = args[1:]
    if not args:
        return False

    if len(args) == 1:
        return True

    elif args[0] == 'request':
        if len(args) - len(defaults) == 1:
            return True

    return False

