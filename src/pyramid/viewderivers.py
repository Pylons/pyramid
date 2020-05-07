import inspect
from zope.interface import implementer, provider

from pyramid import renderers
from pyramid.csrf import check_csrf_origin, check_csrf_token
from pyramid.exceptions import ConfigurationError
from pyramid.httpexceptions import HTTPForbidden
from pyramid.interfaces import (
    IDebugLogger,
    IDefaultCSRFOptions,
    IDefaultPermission,
    IResponse,
    ISecurityPolicy,
    IViewMapper,
    IViewMapperFactory,
)
from pyramid.response import Response
from pyramid.security import NO_PERMISSION_REQUIRED
from pyramid.util import (
    is_bound_method,
    is_unbound_method,
    object_description,
    takes_one_arg,
)
from pyramid.view import render_view_to_response


def view_description(view):
    try:
        return view.__text__
    except AttributeError:
        # custom view mappers might not add __text__
        return object_description(view)


def requestonly(view, attr=None):
    return takes_one_arg(view, attr=attr, argname='request')


@implementer(IViewMapper)
@provider(IViewMapperFactory)
class DefaultViewMapper:
    def __init__(self, **kw):
        self.attr = kw.get('attr')

    def __call__(self, view):
        if is_unbound_method(view) and self.attr is None:
            raise ConfigurationError(
                'Unbound method calls are not supported, please set the '
                'class as your `view` and the method as your `attr`'
            )

        if inspect.isclass(view):
            view = self.map_class(view)
        else:
            view = self.map_nonclass(view)
        return view

    def map_class(self, view):
        ronly = requestonly(view, self.attr)
        if ronly:
            mapped_view = self.map_class_requestonly(view)
        else:
            mapped_view = self.map_class_native(view)
        mapped_view.__text__ = 'method %s of %s' % (
            self.attr or '__call__',
            object_description(view),
        )
        return mapped_view

    def map_nonclass(self, view):
        # We do more work here than appears necessary to avoid wrapping the
        # view unless it actually requires wrapping (to avoid function call
        # overhead).
        mapped_view = view
        ronly = requestonly(view, self.attr)
        if ronly:
            mapped_view = self.map_nonclass_requestonly(view)
        elif self.attr:
            mapped_view = self.map_nonclass_attr(view)
        if inspect.isroutine(mapped_view):
            # This branch will be true if the view is a function or a method.
            # We potentially mutate an unwrapped object here if it's a
            # function.  We do this to avoid function call overhead of
            # injecting another wrapper.  However, we must wrap if the
            # function is a bound method because we can't set attributes on a
            # bound method.
            if is_bound_method(view):
                _mapped_view = mapped_view

                def mapped_view(context, request):
                    return _mapped_view(context, request)

            if self.attr is not None:
                mapped_view.__text__ = 'attr %s of %s' % (
                    self.attr,
                    object_description(view),
                )
            else:
                mapped_view.__text__ = object_description(view)
        return mapped_view

    def map_class_requestonly(self, view):
        # its a class that has an __init__ which only accepts request
        attr = self.attr

        def _class_requestonly_view(context, request):
            inst = view(request)
            request.__view__ = inst
            if attr is None:
                response = inst()
            else:
                response = getattr(inst, attr)()
            return response

        return _class_requestonly_view

    def map_class_native(self, view):
        # its a class that has an __init__ which accepts both context and
        # request
        attr = self.attr

        def _class_view(context, request):
            inst = view(context, request)
            request.__view__ = inst
            if attr is None:
                response = inst()
            else:
                response = getattr(inst, attr)()
            return response

        return _class_view

    def map_nonclass_requestonly(self, view):
        # its a function that has a __call__ which accepts only a single
        # request argument
        attr = self.attr

        def _requestonly_view(context, request):
            if attr is None:
                response = view(request)
            else:
                response = getattr(view, attr)(request)
            return response

        return _requestonly_view

    def map_nonclass_attr(self, view):
        # its a function that has a __call__ which accepts both context and
        # request, but still has an attr
        def _attr_view(context, request):
            response = getattr(view, self.attr)(context, request)
            return response

        return _attr_view


def wraps_view(wrapper):
    def inner(view, info):
        wrapper_view = wrapper(view, info)
        return preserve_view_attrs(view, wrapper_view)

    return inner


def preserve_view_attrs(view, wrapper):
    if view is None:
        return wrapper

    if wrapper is view:
        return view

    original_view = getattr(view, '__original_view__', None)

    if original_view is None:
        original_view = view

    wrapper.__wraps__ = view
    wrapper.__original_view__ = original_view
    wrapper.__module__ = view.__module__
    wrapper.__doc__ = view.__doc__

    try:
        wrapper.__name__ = view.__name__
    except AttributeError:
        wrapper.__name__ = repr(view)

    # attrs that may not exist on "view", but, if so, must be attached to
    # "wrapped view"
    for attr in (
        '__permitted__',
        '__call_permissive__',
        '__permission__',
        '__predicated__',
        '__predicates__',
        '__accept__',
        '__order__',
        '__text__',
    ):
        try:
            setattr(wrapper, attr, getattr(view, attr))
        except AttributeError:
            pass

    return wrapper


def mapped_view(view, info):
    mapper = info.options.get('mapper')
    if mapper is None:
        mapper = getattr(view, '__view_mapper__', None)
        if mapper is None:
            mapper = info.registry.queryUtility(IViewMapperFactory)
            if mapper is None:
                mapper = DefaultViewMapper

    mapped_view = mapper(**info.options)(view)
    return mapped_view


mapped_view.options = ('mapper', 'attr')


def owrapped_view(view, info):
    wrapper_viewname = info.options.get('wrapper')
    viewname = info.options.get('name')
    if not wrapper_viewname:
        return view

    def _owrapped_view(context, request):
        response = view(context, request)
        request.wrapped_response = response
        request.wrapped_body = response.body
        request.wrapped_view = view
        wrapped_response = render_view_to_response(
            context, request, wrapper_viewname
        )
        if wrapped_response is None:
            raise ValueError(
                'No wrapper view named %r found when executing view '
                'named %r' % (wrapper_viewname, viewname)
            )
        return wrapped_response

    return _owrapped_view


owrapped_view.options = ('name', 'wrapper')


def http_cached_view(view, info):
    if info.settings.get('prevent_http_cache', False):
        return view

    seconds = info.options.get('http_cache')

    if seconds is None:
        return view

    options = {}

    if isinstance(seconds, (tuple, list)):
        try:
            seconds, options = seconds
        except ValueError:
            raise ConfigurationError(
                'If http_cache parameter is a tuple or list, it must be '
                'in the form (seconds, options); not %s' % (seconds,)
            )

    def wrapper(context, request):
        response = view(context, request)
        prevent_caching = getattr(
            response.cache_control, 'prevent_auto', False
        )
        if not prevent_caching:
            response.cache_expires(seconds, **options)
        return response

    return wrapper


http_cached_view.options = ('http_cache',)


def secured_view(view, info):
    for wrapper in (_secured_view, _authdebug_view):
        view = wraps_view(wrapper)(view, info)
    return view


secured_view.options = ('permission',)


def _secured_view(view, info):
    permission = explicit_val = info.options.get('permission')
    if permission is None:
        permission = info.registry.queryUtility(IDefaultPermission)
    if permission == NO_PERMISSION_REQUIRED:
        # allow views registered within configurations that have a
        # default permission to explicitly override the default
        # permission, replacing it with no permission at all
        permission = None

    policy = info.registry.queryUtility(ISecurityPolicy)

    # no-op on exception-only views without an explicit permission
    if explicit_val is None and info.exception_only:
        return view

    if policy and (permission is not None):

        def permitted(context, request):
            return policy.permits(request, context, permission)

        def secured_view(context, request):
            result = permitted(context, request)
            if result:
                return view(context, request)
            view_name = getattr(view, '__name__', view)
            msg = getattr(
                request,
                'authdebug_message',
                'Unauthorized: %s failed permission check' % view_name,
            )
            raise HTTPForbidden(msg, result=result)

        secured_view.__call_permissive__ = view
        secured_view.__permitted__ = permitted
        secured_view.__permission__ = permission
        return secured_view
    else:
        return view


def _authdebug_view(view, info):
    wrapped_view = view
    settings = info.settings
    permission = explicit_val = info.options.get('permission')
    if permission is None:
        permission = info.registry.queryUtility(IDefaultPermission)
    policy = info.registry.queryUtility(ISecurityPolicy)
    logger = info.registry.queryUtility(IDebugLogger)

    # no-op on exception-only views without an explicit permission
    if explicit_val is None and info.exception_only:
        return view

    if settings and settings.get('debug_authorization', False):

        def authdebug_view(context, request):
            view_name = getattr(request, 'view_name', None)

            if policy:
                if permission is NO_PERMISSION_REQUIRED:
                    msg = 'Allowed (NO_PERMISSION_REQUIRED)'
                elif permission is None:
                    msg = 'Allowed (no permission registered)'
                else:
                    result = policy.permits(request, context, permission)
                    msg = str(result)
            else:
                msg = 'Allowed (no security policy in use)'

            view_name = getattr(request, 'view_name', None)
            url = getattr(request, 'url', None)
            msg = (
                'debug_authorization of url %s (view name %r against '
                'context %r): %s' % (url, view_name, context, msg)
            )
            if logger:
                logger.debug(msg)
            if request is not None:
                request.authdebug_message = msg
            return view(context, request)

        wrapped_view = authdebug_view

    return wrapped_view


def rendered_view(view, info):
    # one way or another this wrapper must produce a Response (unless
    # the renderer is a NullRendererHelper)
    renderer = info.options.get('renderer')
    if renderer is None:
        # register a default renderer if you want super-dynamic
        # rendering.  registering a default renderer will also allow
        # override_renderer to work if a renderer is left unspecified for
        # a view registration.
        def viewresult_to_response(context, request):
            result = view(context, request)
            if result.__class__ is Response:  # common case
                response = result
            else:
                response = info.registry.queryAdapterOrSelf(result, IResponse)
                if response is None:
                    if result is None:
                        append = (
                            ' You may have forgotten to return a value '
                            'from the view callable.'
                        )
                    elif isinstance(result, dict):
                        append = (
                            ' You may have forgotten to define a '
                            'renderer in the view configuration.'
                        )
                    else:
                        append = ''

                    msg = (
                        'Could not convert return value of the view '
                        'callable %s into a response object. '
                        'The value returned was %r.' + append
                    )

                    raise ValueError(msg % (view_description(view), result))

            return response

        return viewresult_to_response

    if renderer is renderers.null_renderer:
        return view

    def rendered_view(context, request):
        result = view(context, request)
        if result.__class__ is Response:  # potential common case
            response = result
        else:
            # this must adapt, it can't do a simple interface check
            # (avoid trying to render webob responses)
            response = info.registry.queryAdapterOrSelf(result, IResponse)
            if response is None:
                attrs = getattr(request, '__dict__', {})
                if 'override_renderer' in attrs:
                    # renderer overridden by newrequest event or other
                    renderer_name = attrs.pop('override_renderer')
                    view_renderer = renderers.RendererHelper(
                        name=renderer_name,
                        package=info.package,
                        registry=info.registry,
                    )
                else:
                    view_renderer = renderer.clone()
                if '__view__' in attrs:
                    view_inst = attrs.pop('__view__')
                else:
                    view_inst = getattr(view, '__original_view__', view)
                response = view_renderer.render_view(
                    request, result, view_inst, context
                )
        return response

    return rendered_view


rendered_view.options = ('renderer',)


def decorated_view(view, info):
    decorator = info.options.get('decorator')
    if decorator is None:
        return view
    return decorator(view)


decorated_view.options = ('decorator',)


def csrf_view(view, info):
    explicit_val = info.options.get('require_csrf')
    defaults = info.registry.queryUtility(IDefaultCSRFOptions)
    if defaults is None:
        default_val = False
        token = 'csrf_token'
        header = 'X-CSRF-Token'
        safe_methods = frozenset(["GET", "HEAD", "OPTIONS", "TRACE"])
        check_origin = True
        allow_no_origin = False
        callback = None
    else:
        default_val = defaults.require_csrf
        token = defaults.token
        header = defaults.header
        safe_methods = defaults.safe_methods
        check_origin = defaults.check_origin
        allow_no_origin = defaults.allow_no_origin
        callback = defaults.callback

    enabled = (
        explicit_val is True
        or
        # fallback to the default val if not explicitly enabled
        # but only if the view is not an exception view
        (explicit_val is not False and default_val and not info.exception_only)
    )
    # disable if both header and token are disabled
    enabled = enabled and (token or header)
    wrapped_view = view
    if enabled:

        def csrf_view(context, request):
            if request.method not in safe_methods and (
                callback is None or callback(request)
            ):
                if check_origin:
                    check_csrf_origin(
                        request, raises=True, allow_no_origin=allow_no_origin
                    )
                check_csrf_token(request, token, header, raises=True)
            return view(context, request)

        wrapped_view = csrf_view
    return wrapped_view


csrf_view.options = ('require_csrf',)

VIEW = 'VIEW'
INGRESS = 'INGRESS'
