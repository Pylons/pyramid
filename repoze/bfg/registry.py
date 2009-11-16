import re
import sys

from zope.component.registry import Components

from zope.configuration.exceptions import ConfigurationError

from zope.interface import Interface
from zope.interface import implementedBy
from zope.interface.interfaces import IInterface

import martian

from repoze.bfg.interfaces import IAuthenticationPolicy
from repoze.bfg.interfaces import IAuthorizationPolicy
from repoze.bfg.interfaces import IForbiddenView
from repoze.bfg.interfaces import IMultiView
from repoze.bfg.interfaces import INotFoundView
from repoze.bfg.interfaces import IPackageOverrides
from repoze.bfg.interfaces import IRendererFactory
from repoze.bfg.interfaces import IRequest
from repoze.bfg.interfaces import IRouteRequest
from repoze.bfg.interfaces import IRoutesMapper
from repoze.bfg.interfaces import ISecuredView
from repoze.bfg.interfaces import IView
from repoze.bfg.interfaces import IViewPermission

from repoze.bfg.request import route_request_iface
from repoze.bfg.resource import PackageOverrides
from repoze.bfg.static import StaticRootFactory
from repoze.bfg.traversal import find_interface
from repoze.bfg.view import MultiView
from repoze.bfg.view import derive_view
from repoze.bfg.view import static as static_view
from repoze.bfg.urldispatch import RoutesRootFactory

class Registry(Components, dict):

    # for optimization purposes, if no listeners are listening, don't try
    # to notify them
    has_listeners = False

    def __init__(self, name='', bases=()):
        Components.__init__(self, name=name, bases=bases)
        mapper = RoutesRootFactory(DefaultRootFactory)
        self.registerUtility(mapper, IRoutesMapper)

    def registerSubscriptionAdapter(self, *arg, **kw):
        result = Components.registerSubscriptionAdapter(self, *arg, **kw)
        self.has_listeners = True
        return result
        
    def registerHandler(self, *arg, **kw):
        result = Components.registerHandler(self, *arg, **kw)
        self.has_listeners = True
        return result

    def notify(self, *events):
        if self.has_listeners:
            # iterating over subscribers assures they get executed
            [ _ for _ in self.subscribers(events, None) ]

    def view(self, permission=None, for_=None, view=None, name="",
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

        if request_type in ('GET', 'HEAD', 'PUT', 'POST', 'DELETE'):
            # b/w compat for 1.0
            request_method = request_type
            request_type = None

        if request_type is None:
            if route_name is None:
                request_type = IRequest
            else:
                request_type = self.queryUtility(IRouteRequest, name=route_name)
                if request_type is None:
                    request_type = route_request_iface(route_name)
                    self.registerUtility(request_type, IRouteRequest,
                                         name=route_name)

        score, predicates = _make_predicates(
            xhr=xhr, request_method=request_method, path_info=path_info,
            request_param=request_param, header=header, accept=accept,
            containment=containment)

        derived_view = derive_view(view, permission, predicates, attr,
                                   renderer, wrapper, name)
        r_for_ = for_
        r_request_type = request_type
        if r_for_ is None:
            r_for_ = Interface
        if not IInterface.providedBy(r_for_):
            r_for_ = implementedBy(r_for_)
        if not IInterface.providedBy(r_request_type):
            r_request_type = implementedBy(r_request_type)
        old_view = self.adapters.lookup((r_for_, r_request_type),
                                        IView,name=name)
        if old_view is None:
            if hasattr(derived_view, '__call_permissive__'):
                self.registerAdapter(derived_view, (for_, request_type),
                                     ISecuredView, name, info=_info)
                if hasattr(derived_view, '__permitted__'):
                    # bw compat
                    self.registerAdapter(
                        derived_view.__permitted__,
                        (for_, request_type), IViewPermission,
                        name, info=_info)
            else:
                self.registerAdapter(derived_view, (for_, request_type),
                                     IView, name, info=_info)
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
                self.adapters.unregister((r_for_, r_request_type), i,
                                         name=name)
            self.registerAdapter(multiview, (for_, request_type),
                                 IMultiView, name, info=_info)
            # b/w compat
            self.registerAdapter(multiview.__permitted__,
                                 (for_, request_type), IViewPermission,
                                 name, info=_info)

    def route(self, name, path, view=None, view_for=None,
              permission=None, factory=None, request_type=None, for_=None,
              header=None, xhr=False, accept=None, path_info=None,
              request_method=None, request_param=None, 
              view_permission=None, view_request_type=None, 
              view_request_method=None, view_request_param=None,
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

        if request_type in ('GET', 'HEAD', 'PUT', 'POST', 'DELETE'):
            # b/w compat for 1.0
            view_request_method = request_type
            request_type = None

        request_iface = self.queryUtility(IRouteRequest, name=name)
        if request_iface is None:
            request_iface = route_request_iface(name)
            self.registerUtility(request_iface, IRouteRequest, name=name)

        if view:
            view_for = view_for or for_
            view_request_type = view_request_type or request_type
            view_permission = view_permission or permission
            view_renderer = view_renderer or renderer
            self.view(
                permission=view_permission,
                for_=view_for,
                view=view,
                name='',
                request_type=view_request_type,
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
                info=_info,
                )

        mapper = self.getUtility(IRoutesMapper)
        mapper.connect(path, name, factory, predicates=predicates)

    def scan(self, package, _info=u'', martian=martian):
        # martian overrideable only for unit tests
        multi_grokker = BFGMultiGrokker()
        multi_grokker.register(BFGViewGrokker())
        module_grokker = martian.ModuleGrokker(grokker=multi_grokker)
        martian.grok_dotted_name(
            package.__name__, grokker=module_grokker,
            _info=_info, _registry=self,
            exclude_filter=lambda name: name.startswith('.'))

    def authentication_policy(self, policy, _info=u''):
        self.registerUtility(policy, IAuthenticationPolicy, info=_info)
        
    def authorization_policy(self, policy, _info=u''):
        self.registerUtility(policy, IAuthorizationPolicy, info=_info)

    def renderer(self, factory, name, _info=u''):
        self.registerUtility(factory, IRendererFactory, name=name, info=_info)

    def resource(self, to_override, override_with, _override=None,
                 _info=u''):
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
            override = self.queryUtility(IPackageOverrides, name=pkg_name)
            if override is None:
                override = PackageOverrides(package)
                self.registerUtility(override, IPackageOverrides, name=pkg_name,
                                     info=_info)
            override.insert(path, override_pkg_name, override_prefix)


    def notfound(self, view=None, attr=None, renderer=None, wrapper=None,
                 _info=u''):
        self._view_utility(view, attr, renderer, wrapper, INotFoundView,
                           _info=_info)

    def forbidden(self, view=None, attr=None, renderer=None, wrapper=None,
                  _info=u''):
        self._view_utility(view, attr, renderer, wrapper,
                           IForbiddenView, _info=_info)

    def view_utility(self, view, attr, renderer, wrapper, iface, _info=u''):
        if not view:
            if renderer:
                def view(context, request):
                    return {}
            else:
                raise ConfigurationError('"view" attribute was not specified and '
                                         'no renderer specified')

        derived_view = derive_view(view, attr=attr, renderer_name=renderer,
                                   wrapper_viewname=wrapper)
        self.registerUtility(derived_view, iface, '', info=_info)

    def static(self, name, path, cache_max_age=3600, _info=u''):
        view = static_view(path, cache_max_age=cache_max_age)
        self.route(name, "%s*subpath" % name, view=view,
                   view_for=StaticRootFactory, factory=StaticRootFactory(path),
                   _info=_info)
        

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
            registry = kw['_registry']
            info = kw['_info']
            registry.view(view=obj, _info=info, **settings)
        return bool(config)

class DefaultRootFactory:
    __parent__ = None
    __name__ = None
    def __init__(self, request):
        matchdict = getattr(request, 'matchdict', {})
        # provide backwards compatibility for applications which
        # used routes (at least apps without any custom "context
        # factory") in BFG 0.9.X and before
        self.__dict__.update(matchdict)

