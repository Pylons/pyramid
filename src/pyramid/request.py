from collections import deque
import functools
import weakref
from webob import BaseRequest
from zope.interface import implementer
from zope.interface.interface import InterfaceClass

from pyramid.decorator import reify
from pyramid.i18n import LocalizerRequestMixin
from pyramid.interfaces import (
    IRequest,
    IRequestExtensions,
    IResponse,
    ISessionFactory,
)
from pyramid.response import Response, _get_response_factory
from pyramid.security import AuthenticationAPIMixin, SecurityAPIMixin
from pyramid.url import URLMethodsMixin
from pyramid.util import (
    InstancePropertyHelper,
    InstancePropertyMixin,
    Sentinel,
    bytes_,
    text_,
)
from pyramid.view import ViewMethodsMixin


class TemplateContext:
    pass


class CallbackMethodsMixin:
    @reify
    def finished_callbacks(self):
        return deque()

    @reify
    def response_callbacks(self):
        return deque()

    def add_response_callback(self, callback):
        """
        Add a callback to the set of callbacks to be called by the
        :term:`router` at a point after a :term:`response` object is
        successfully created.  :app:`Pyramid` does not have a
        global response object: this functionality allows an
        application to register an action to be performed against the
        response once one is created.

        A 'callback' is a callable which accepts two positional
        parameters: ``request`` and ``response``.  For example:

        .. code-block:: python
           :linenos:

           def cache_callback(request, response):
               'Set the cache_control max_age for the response'
               response.cache_control.max_age = 360
           request.add_response_callback(cache_callback)

        Response callbacks are called in the order they're added
        (first-to-most-recently-added).  No response callback is
        called if an exception happens in application code, or if the
        response object returned by :term:`view` code is invalid.

        All response callbacks are called *after* the tweens and
        *before* the :class:`pyramid.events.NewResponse` event is sent.

        Errors raised by callbacks are not handled specially.  They
        will be propagated to the caller of the :app:`Pyramid`
        router application.

        .. seealso::

            See also :ref:`using_response_callbacks`.
        """

        self.response_callbacks.append(callback)

    def _process_response_callbacks(self, response):
        callbacks = self.response_callbacks
        while callbacks:
            callback = callbacks.popleft()
            callback(self, response)

    def add_finished_callback(self, callback):
        """
        Add a callback to the set of callbacks to be called
        unconditionally by the :term:`router` at the very end of
        request processing.

        ``callback`` is a callable which accepts a single positional
        parameter: ``request``.  For example:

        .. code-block:: python
           :linenos:

           import transaction

           def commit_callback(request):
               '''commit or abort the transaction associated with request'''
               if request.exception is not None:
                   transaction.abort()
               else:
                   transaction.commit()
           request.add_finished_callback(commit_callback)

        Finished callbacks are called in the order they're added (
        first- to most-recently- added).  Finished callbacks (unlike
        response callbacks) are *always* called, even if an exception
        happens in application code that prevents a response from
        being generated.

        The set of finished callbacks associated with a request are
        called *very late* in the processing of that request; they are
        essentially the last thing called by the :term:`router`. They
        are called after response processing has already occurred in a
        top-level ``finally:`` block within the router request
        processing code.  As a result, mutations performed to the
        ``request`` provided to a finished callback will have no
        meaningful effect, because response processing will have
        already occurred, and the request's scope will expire almost
        immediately after all finished callbacks have been processed.

        Errors raised by finished callbacks are not handled specially.
        They will be propagated to the caller of the :app:`Pyramid`
        router application.

        .. seealso::

            See also :ref:`using_finished_callbacks`.
        """
        self.finished_callbacks.append(callback)

    def _process_finished_callbacks(self):
        callbacks = self.finished_callbacks
        while callbacks:
            callback = callbacks.popleft()
            callback(self)


@implementer(IRequest)
class Request(
    BaseRequest,
    URLMethodsMixin,
    CallbackMethodsMixin,
    InstancePropertyMixin,
    LocalizerRequestMixin,
    SecurityAPIMixin,
    AuthenticationAPIMixin,
    ViewMethodsMixin,
):
    """
    A subclass of the :term:`WebOb` Request class.  An instance of
    this class is created by the :term:`router` and is provided to a
    view callable (and to other subsystems) as the ``request``
    argument.

    The documentation below (save for the ``add_response_callback`` and
    ``add_finished_callback`` methods, which are defined in this subclass
    itself, and the attributes ``context``, ``registry``, ``root``,
    ``subpath``, ``traversed``, ``view_name``, ``virtual_root`` , and
    ``virtual_root_path``, each of which is added to the request by the
    :term:`router` at request ingress time) are autogenerated from the WebOb
    source code used when this documentation was generated.

    Due to technical constraints, we can't yet display the WebOb
    version number from which this documentation is autogenerated, but
    it will be the 'prevailing WebOb version' at the time of the
    release of this :app:`Pyramid` version.  See
    https://webob.org/ for further information.
    """

    exception = None
    exc_info = None
    matchdict = None
    matched_route = None
    request_iface = IRequest

    ResponseClass = Response

    @reify
    def tmpl_context(self):
        # docs-deprecated template context for Pylons-like apps; do not
        # remove.
        return TemplateContext()

    @reify
    def session(self):
        """Obtain the :term:`session` object associated with this
        request.  If a :term:`session factory` has not been registered
        during application configuration, a
        :class:`pyramid.exceptions.ConfigurationError` will be raised"""
        factory = self.registry.queryUtility(ISessionFactory)
        if factory is None:
            raise AttributeError(
                'No session factory registered '
                '(see the Sessions chapter of the Pyramid documentation)'
            )
        return factory(self)

    @reify
    def response(self):
        """This attribute is actually a "reified" property which returns an
        instance of the :class:`pyramid.response.Response`. class.  The
        response object returned does not exist until this attribute is
        accessed.  Subsequent accesses will return the same Response object.

        The ``request.response`` API is used by renderers.  A render obtains
        the response object it will return from a view that uses that renderer
        by accessing ``request.response``.  Therefore, it's possible to use the
        ``request.response`` API to set up a response object with "the
        right" attributes (e.g. by calling ``request.response.set_cookie()``)
        within a view that uses a renderer.  Mutations to this response object
        will be preserved in the response sent to the client."""
        response_factory = _get_response_factory(self.registry)
        return response_factory(self)

    def is_response(self, ob):
        """Return ``True`` if the object passed as ``ob`` is a valid
        response object, ``False`` otherwise."""
        if ob.__class__ is Response:
            return True
        registry = self.registry
        adapted = registry.queryAdapterOrSelf(ob, IResponse)
        if adapted is None:
            return False
        return adapted is ob


def route_request_iface(name, bases=()):
    # zope.interface treats the __name__ as the __doc__ and changes __name__
    # to None for interfaces that contain spaces if you do not pass a
    # nonempty __doc__ (insane); see
    # zope.interface.interface.Element.__init__ and
    # https://github.com/Pylons/pyramid/issues/232; as a result, always pass
    # __doc__ to the InterfaceClass constructor.
    iface = InterfaceClass(
        '%s_IRequest' % name,
        bases=bases,
        __doc__="route_request_iface-generated interface",
    )
    # for exception view lookups
    iface.combined = InterfaceClass(
        '%s_combined_IRequest' % name,
        bases=(iface, IRequest),
        __doc__='route_request_iface-generated combined interface',
    )
    return iface


def add_global_response_headers(request, headerlist):
    def add_headers(request, response):
        for k, v in headerlist:
            response.headerlist.append((k, v))

    request.add_response_callback(add_headers)


def call_app_with_subpath_as_path_info(request, app):
    # Copy the request.  Use the source request's subpath (if it exists) as
    # the new request's PATH_INFO.  Set the request copy's SCRIPT_NAME to the
    # prefix before the subpath.  Call the application with the new request
    # and return a response.
    #
    # Postconditions:
    # - SCRIPT_NAME and PATH_INFO are empty or start with /
    # - At least one of SCRIPT_NAME or PATH_INFO are set.
    # - SCRIPT_NAME is not '/' (it should be '', and PATH_INFO should
    #   be '/').

    environ = request.environ
    script_name = environ.get('SCRIPT_NAME', '')
    path_info = environ.get('PATH_INFO', '/')
    subpath = list(getattr(request, 'subpath', ()))

    new_script_name = ''

    # compute new_path_info
    new_path_info = '/' + '/'.join(
        [text_(x.encode('utf-8'), 'latin-1') for x in subpath]
    )

    if new_path_info != '/':  # don't want a sole double-slash
        if path_info != '/':  # if orig path_info is '/', we're already done
            if path_info.endswith('/'):
                # readd trailing slash stripped by subpath (traversal)
                # conversion
                new_path_info += '/'

    # compute new_script_name
    workback = (script_name + path_info).split('/')

    tmp = []
    while workback:
        if tmp == subpath:
            break
        el = workback.pop()
        if el:
            tmp.insert(0, text_(bytes_(el, 'latin-1'), 'utf-8'))

    # strip all trailing slashes from workback to avoid appending undue slashes
    # to end of script_name
    while workback and (workback[-1] == ''):
        workback = workback[:-1]

    new_script_name = '/'.join(workback)

    new_request = request.copy()
    new_request.environ['SCRIPT_NAME'] = new_script_name
    new_request.environ['PATH_INFO'] = new_path_info

    return new_request.get_response(app)


def apply_request_extensions(request, extensions=None):
    """Apply request extensions (methods and properties) to an instance of
    :class:`pyramid.interfaces.IRequest`. This method is dependent on the
    ``request`` containing a properly initialized registry.

    After invoking this method, the ``request`` should have the methods
    and properties that were defined using
    :meth:`pyramid.config.Configurator.add_request_method`.
    """
    if extensions is None:
        extensions = request.registry.queryUtility(IRequestExtensions)
    if extensions is not None:
        for name, fn in extensions.methods.items():
            method = fn.__get__(request, request.__class__)
            setattr(request, name, method)

        InstancePropertyHelper.apply_properties(
            request, extensions.descriptors
        )


class RequestLocalCache:
    """
    A store that caches values during for the lifecycle of a request.

    Wrapping Functions

    Instantiate and use it to decorate functions that accept a request
    parameter. The result is cached and returned in subsequent invocations
    of the function.

    .. code-block:: python

        @RequestLocalCache()
        def get_user(request):
            result = ...  # do some expensive computations
            return result

        value = get_user(request)

        # manipulate the cache directly
        get_user.cache.clear(request)

    The cache instance is attached to the resulting function as the ``cache``
    attribute such that the function may be used to manipulate the cache.

    Wrapping Methods

    A method can be used as the creator function but it needs to be bound to
    an instance such that it only accepts one argument - the request. An easy
    way to do this is to bind the creator in the constructor and then use
    :meth:`.get_or_create`:

    .. code-block:: python

        class SecurityPolicy:
            def __init__(self):
                self.identity_cache = RequestLocalCache(self.load_identity)

            def load_identity(self, request):
                result = ...  # do some expensive computations
                return result

            def identity(self, request):
                return self.identity_cache.get_or_create(request)

    The cache maintains a weakref to each request and will release the cached
    values when the request is garbage-collected. However, in most scenarios,
    it will release resources earlier via
    :meth:`pyramid.request.Request.add_finished_callback`.

    .. versionadded:: 2.0

    """

    NO_VALUE = Sentinel('NO_VALUE')

    def __init__(self, creator=None):
        self._store = weakref.WeakKeyDictionary()
        self._creator = creator

    def __call__(self, fn):
        @functools.wraps(fn)
        def wrapper(request):
            return wrapper.cache.get_or_create(request, fn)

        wrapper.cache = self
        self._creator = fn
        return wrapper

    def get_or_create(self, request, creator=None):
        """
        Return the value from the cache. Compute if necessary.

        If no value is cached then execute the creator, cache the result,
        and return it.

        The creator may be passed in as an argument or bound to the cache
        by decorating a function or supplied as a constructor argument.

        """
        result = self._store.get(request, self.NO_VALUE)
        if result is self.NO_VALUE:
            if creator is None:
                creator = self._creator
                if creator is None:
                    raise ValueError(
                        'no creator function has been registered with the '
                        'cache or supplied to "get_or_create"'
                    )
            result = creator(request)
            self.set(request, result)
        return result

    def get(self, request, default=NO_VALUE):
        """
        Return the value from the cache.

        The cached value is returned or ``default``.

        """
        return self._store.get(request, default)

    def set(self, request, value):
        """
        Update the cache with a new value.

        """
        already_set = request in self._store
        self._store[request] = value

        # avoid registering the callback more than once
        if not already_set:
            request.add_finished_callback(self._store.pop)

    def clear(self, request):
        """
        Delete the value from the cache.

        The cached value is returned or :attr:`.NO_VALUE`.

        """
        old_value = self.NO_VALUE
        if request in self._store:
            old_value = self._store[request]

            # keep a value in the store so that we don't register another
            # finished callback when set is invoked
            self._store[request] = self.NO_VALUE
        return old_value
