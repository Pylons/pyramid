import copy

from webob import Response

from zope.configuration.xmlconfig import _clearContext

from zope.deprecation import deprecated

from zope.interface import implements
from zope.interface import Interface
from zope.interface import alsoProvides

from repoze.bfg.interfaces import IAuthenticationPolicy
from repoze.bfg.interfaces import IAuthorizationPolicy
from repoze.bfg.interfaces import IRequest
from repoze.bfg.interfaces import IRoutesMapper
from repoze.bfg.interfaces import ISecuredView
from repoze.bfg.interfaces import ISettings
from repoze.bfg.interfaces import ITemplateRenderer
from repoze.bfg.interfaces import ITraverser
from repoze.bfg.interfaces import IView
from repoze.bfg.interfaces import IViewPermission

from repoze.bfg.configuration import Configurator
from repoze.bfg.exceptions import Forbidden
from repoze.bfg.registry import Registry
from repoze.bfg.security import Allowed
from repoze.bfg.security import Authenticated
from repoze.bfg.security import Denied
from repoze.bfg.security import Everyone
from repoze.bfg.security import has_permission
from repoze.bfg.settings import Settings
from repoze.bfg.threadlocal import get_current_registry
from repoze.bfg.threadlocal import manager
from repoze.bfg.traversal import traversal_path
from repoze.bfg.urldispatch import RoutesMapper
from repoze.bfg.zcml import zcml_configure # API

zcml_configure # prevent pyflakes from complaining

_marker = object()

def registerDummySecurityPolicy(userid=None, groupids=(), permissive=True):
    """ Registers a a pair of dummy :mod:`repoze.bfg` security
    policies: an :term:`authorization policy` and an
    :term:`authentication policy`) using the userid ``userid`` and the
    group ids ``groupids``.  If ``permissive`` is true, a 'permissive'
    authorization policy is registered; this policy allows all access.
    If ``permissive`` is false, a nonpermissive authorization policy
    is registered; this policy denies all access.  This function is
    most useful when testing code that uses the
    ``repoze.bfg.security`` APIs named ``has_permission``,
    ``authenticated_userid``, ``effective_principals``,
    ``principals_allowed_by_permission``, and so on.
    """
    policy = DummySecurityPolicy(userid, groupids, permissive)
    reg = get_current_registry()
    reg.registerUtility(policy, IAuthorizationPolicy)
    reg.registerUtility(policy, IAuthenticationPolicy)

def registerModels(models):
    """ Registers a dictionary of models that can be resolved via
    ``repoze.bfg.traversal.find_model``.  This is most useful for
    testing code that wants to call the
    ``repoze.bfg.traversal.find_model`` API.  The ``find_model`` API
    is called with a path as one of its arguments.  If the dictionary
    you register when calling this method contains that path as a
    string key (e.g. ``/foo/bar`` or ``foo/bar``), the corresponding
    value will be returned to ``find_model`` (and thus to your code)
    when ``find_model`` is called with an equivalent path string or
    tuple."""
    class DummyTraverserFactory:
        def __init__(self, context):
            self.context = context

        def __call__(self, request):
            path = request['PATH_INFO']
            ob = models[path]
            traversed = traversal_path(path)
            return {'context':ob, 'view_name':'','subpath':(),
                    'traversed':traversed, 'virtual_root':ob,
                    'virtual_root_path':(), 'root':ob}

    registerTraverser(DummyTraverserFactory)
    return models

def registerEventListener(event_iface=Interface):
    """ Registers an :term:`event` listener (aka :term:`subscriber`)
    listening for events of the type ``event_iface`` and returns a
    list which is appended to by the subscriber.  When an event is
    dispatched that matches ``event_iface``, that event will be
    appended to the list.  You can then compare the values in the list
    to expected event notifications.  This method is useful when
    testing code that wants to call ``registry.notify``,
    ``zope.component.event.dispatch`` or
    ``zope.component.event.objectEventNotify``."""
    L = []
    def subscriber(*event):
        L.extend(event)
    registerSubscriber(subscriber, event_iface)
    return L

def registerTemplateRenderer(path, renderer=None):
    """ Register a template tenderer at ``path`` (usually a relative
    filename ala ``templates/foo.pt``) and return the renderer object.
    If the ``renderer`` argument is None, a 'dummy' renderer will be
    used.  This function is useful when testing code that calls the
    ``render_template_to_response`` or any other ``render_template*``
    API of any of the built-in templating systems."""
    if renderer is None:
        renderer = DummyTemplateRenderer()
    return registerUtility(renderer, ITemplateRenderer, path)

# registerDummyRenderer is a deprecated alias that should never be removed
# (far too much usage in the wild)
registerDummyRenderer = registerTemplateRenderer

def registerView(name, result='', view=None, for_=(Interface, Interface),
                 permission=None):
    """ Registers a :mod:`repoze.bfg` view callable under the name
    ``name``.  The view will return a webob Response object with the
    ``result`` value as its body attribute.  To gain more control, if
    you pass in a non-None ``view``, this view function will be used
    instead of an automatically generated view function (and
    ``result`` is not used).  To protect the view using a
    :term:`permission`, pass in a non-``None`` value as
    ``permission``.  This permission will be checked by any existing
    security policy when view execution is attempted.  This function
    is useful when dealing with code that wants to call,
    e.g. ``repoze.bfg.view.render_view_to_response``."""
    if view is None:
        def view(context, request):
            return Response(result)
    if permission is None:
        return registerAdapter(view, for_, IView, name)
    else:
        def _secure(context, request):
            if not has_permission(permission, context, request):
                raise Forbidden('no permission')
            else:
                return view(context, request)
        _secure.__call_permissive__ = view
        def permitted(context, request):
            return has_permission(permission, context, request)
        _secure.__permitted__ = permitted
        return registerAdapter(_secure, for_, ISecuredView, name)

def registerViewPermission(name, result=True, viewpermission=None,
                           for_=(Interface, Interface)):
    """ Registers a :mod:`repoze.bfg` 'view permission' object under
    the name ``name``.  The view permission return a result denoted by
    the ``result`` argument.  If ``result`` is True, a
    ``repoze.bfg.security.Allowed`` object is returned; else a
    ``repoze.bfg.security.Denied`` object is returned.  To gain more
    control, if you pass in a non-None ``viewpermission``, this view
    permission object will be used instead of an automatically
    generated view permission (and ``result`` is not used).  This
    method is useful when dealing with code that wants to call,
    e.g. ``repoze.bfg.view.view_execution_permitted``.  Note that view
    permissions are not checked unless a security policy is in effect
    (see ``registerSecurityPolicy``).

    .. warning:: This function was deprecated in repoze.bfg 1.1; it
                 has no real effect in 1.2+.
    """
    if result is True:
        result = Allowed('message')
    else:
        result = Denied('message')
    if viewpermission is None:
        def viewpermission(context, request):
            return result
    return registerAdapter(viewpermission, for_, IViewPermission, name)

deprecated('registerViewPermission',
           'registerViewPermission has been deprecated.  As of repoze.bfg '
           'version 1.1, view functions are now responsible for protecting '
           'their own execution.  A call to this function won\'t prevent a '
           'view from being executed by the repoze.bfg router, nor '
           'will the ``repoze.bfg.security.view_execution_permitted`` function '
           'use the permission registered with this function.  Instead,'
           'to register a view permission during testing, use the '
           '``repoze.bfg.testing.registerView`` directive with a '
           '``permission`` argument.')

def registerUtility(impl, iface=Interface, name=''):
    """ Register a utility component.

   ``impl`` is the implementation of the utility.  ``iface`` is the
    interface type ``zope.interface.Interface`` by default.  ``name``
    is the empty string by default.

    See `The ZCA book <http://www.muthukadan.net/docs/zca.html>`_ for
    more information about ZCA utilities."""
    reg = get_current_registry()
    reg.registerUtility(impl, iface, name=name)
    return impl

def registerAdapter(impl, for_=Interface, provides=Interface, name=''):
    """ Register an adapter component.

    ``impl`` is the implementation of the component (often a class).
    ``for_`` is the ``for`` interface type
    ``zope.interface.Interface`` by default. If ``for`` is not a tuple
    or list, it will be converted to a one-tuple before being passed
    to underlying ZCA registerAdapter API.  ``name`` is the empty
    string by default.  ``provides`` is the ZCA provides interface,
    also ``zope.interface.Interface`` by default.  ``name`` is the
    name of the adapter, the empty string by default.

    See `The ZCA book <http://www.muthukadan.net/docs/zca.html>`_ for
    more information about ZCA adapters."""
    reg = get_current_registry()
    if not isinstance(for_, (tuple, list)):
        for_ = (for_,)
    reg.registerAdapter(impl, for_, provides, name=name)
    return impl

def registerSubscriber(subscriber, iface=Interface):
    """ Register a subscriber component.

    ``subscriber`` is the implementation of the component (often a
    function).  ``iface`` is the interface type the subscriber will be
    registered for (``zope.interface.Interface`` by default). If
    ``iface`` is not a tuple or list, it will be converted to a
    one-tuple before being passed to underlying ZCA registerHandler
    query.

    See `The ZCA book <http://www.muthukadan.net/docs/zca.html>`_ for
    more information about ZCA subscribers."""
    reg = get_current_registry()
    if not isinstance(iface, (tuple, list)):
        iface = (iface,)
    reg.registerHandler(subscriber, iface)
    return subscriber

def registerTraverser(traverser, for_=Interface):
    return registerAdapter(traverser, for_, ITraverser)

def registerRoute(path, name, factory=None):
    """ Register a new :term:`route` using a path
    (e.g. ``:pagename``), a name (e.g. 'home'), and an optional root
    factory.  This is useful for testing code that calls
    e.g. ``route_url``.

    .. note:: This API was added in :mod:`repoze.bfg` version 1.1.
    """
    reg = get_current_registry()
    mapper = reg.queryUtility(IRoutesMapper)
    if mapper is None:
        mapper = registerRoutesMapper(factory)
    mapper.connect(path, name, factory)

def registerRoutesMapper(root_factory=None):
    """ Register a new routes mapper using the provided
    ``root_factory`` as the root factory it wraps.  If
    ``root_factory`` is ``None``, use a default root factory
    implementation.

    Use of this function is beneficial when you want to register an
    empty routes mapper with a custom ``root_factory``.

    Note that ``repoze.bfg.testing.registerRoute`` also registers a
    route mapper if one is not already registered, thus it is not
    necessary to call this function before calling
    ``repoze.bfg.testing.registerRoute``.  However, if
    ``repoze.bfg.registerRoutesMapper`` *is* called before
    ``repoze.bfg.testing.registerRoute``, the routes mapper registered
    by ``repoze.bfg.testing.registerRoutesMapper`` will be used as the
    mapper in which the route is registered during
    ``repoze.bfg.testing.registerRoute``.

    .. note:: This API was added in :mod:`repoze.bfg` version 1.1.

    """
    mapper = RoutesMapper()
    reg = get_current_registry()
    reg.registerUtility(mapper, IRoutesMapper)
    return mapper

def registerSettings(dictarg=None, **kw):
    """ Register one or more 'setting' key/value pairs.  A setting is
    a single key/value pair in the dictionary-ish object returned from
    the API ``repoze.bfg.settings.get_settings()``.

    You may pass a dictionary::

       registerSettings({'external_uri':'http://example.com'})

    Or a set of key/value pairs::
    
       registerSettings(external_uri='http://example.com')

    Use of this function is required when you need to test code that
    calls the ``repoze.bfg.settings.get_settings()`` API and uses
    return values from it.

    .. note:: This API is new as of :mod:`repoze.bfg` 1.1.
    """
    reg = get_current_registry()
    settings = reg.queryUtility(ISettings)
    if settings is None:
        settings = Settings()
        reg.registerUtility(settings, ISettings)
    if dictarg is not None:
        settings.update(dictarg)
    settings.update(kw)

class DummyRootFactory(object):
    __parent__ = None
    __name__ = None
    def __init__(self, request):
        if 'bfg.routes.matchdict' in request:
            self.__dict__.update(request['bfg.routes.matchdict'])

class DummySecurityPolicy:
    """ A standin for both an IAuthentication and IAuthorization policy """
    def __init__(self, userid=None, groupids=(), permissive=True):
        self.userid = userid
        self.groupids = groupids
        self.permissive = permissive

    def authenticated_userid(self, request):
        return self.userid

    def effective_principals(self, request):
        effective_principals = [Everyone]
        if self.userid:
            effective_principals.append(Authenticated)
            effective_principals.append(self.userid)
            effective_principals.extend(self.groupids)
        return effective_principals

    def remember(self, request, principal, **kw):
        return []

    def forget(self, request):
        return []

    def permits(self, context, principals, permission):
        return self.permissive

    def principals_allowed_by_permission(self, context, permission):
        return self.effective_principals(None)

class DummyTemplateRenderer:
    """
    An instance of this class is returned from
    ``registerTemplateRenderer``.  It has a helper function
    (``assert_``) that makes it possible to make an assertion which
    compares data passed to the renderer by the view function against
    expected key/value pairs.
    """

    def __init__(self, string_response=''):
        self._received = {}
        self.string_response = string_response
        
    def implementation(self):
        def callit(**kw):
            return self(kw)
        return callit
    
    def __call__(self, kw, system=None):
        self._received.update(kw)
        return self.string_response

    def __getattr__(self, k):
        """ Backwards compatibility """
        val = self._received.get(k, _marker)
        if val is _marker:
            raise AttributeError(k)
        return val

    def assert_(self, **kw):
        """ Accept an arbitrary set of assertion key/value pairs.  For
        each assertion key/value pair assert that the renderer
        (eg. ``render_template_to_response``) received the key with a
        value that equals the asserted value. If the renderer did not
        receive the key at all, or the value received by the renderer
        doesn't match the assertion value, raise an AssertionError."""
        for k, v in kw.items():
            myval = self._received.get(k, _marker)
            if myval is _marker:
                raise AssertionError(
                    'A value for key "%s" was not passed to the renderer' % k)
                    
            if myval != v:
                raise AssertionError(
                    '\nasserted value for %s: %r\nactual value: %r' % (
                    v, k, myval))
        return True

class DummyModel:
    """ A dummy :mod:`repoze.bfg` model object.  The value of ``name``
    to the constructor will be used as the ``__name__`` attribute of
    the model.  the value of ``parent`` will be used as the
    ``__parent__`` attribute of the model. """
    def __init__(self, __name__=None, __parent__=None, __provides__=None,
                 **kw):
        """ The he model's ``__name__`` attribute will be set to the
        value of ``__name__``, and the model's ``__parent__``
        attribute will be set to the value of ``__parent__``.  If
        ``__provides__`` is specified, it should be an interface
        object or tuple of interface objects that will be attached to
        the resulting model via ``zope.interface.alsoProvides``. Any
        extra keywords will be set as direct attributes of the model."""
        self.__name__ = __name__
        self.__parent__ = __parent__
        if __provides__ is not None:
            alsoProvides(self, __provides__)
        self.kw = kw
        self.__dict__.update(**kw)
        self.subs = {}

    def __setitem__(self, name, val):
        """ When the ``__setitem__`` method is called, the object
        passed in as ``val`` will be decorated with a ``__parent__``
        attribute pointing at the dummy model and a ``__name__``
        attribute that is the value of ``name``.  The value will then
        be returned when dummy model's ``__getitem__`` is called with
        the name ``name```."""
        val.__name__ = name
        val.__parent__ = self
        self.subs[name] = val
        
    def __getitem__(self, name):
        """ Return a named subobject (see ``__setitem__``)"""
        ob = self.subs[name]
        return ob

    def __delitem__(self, name):
        del self.subs[name]

    def get(self, name, default=None):
        return self.subs.get(name, default)

    def values(self):
        """ Return the values set by __setitem__ """
        return self.subs.values()

    def items(self):
        """ Return the items set by __setitem__ """
        return self.subs.items()

    def keys(self):
        """ Return the keys set by __setitem__ """
        return self.subs.keys()

    __iter__ = keys

    def __nonzero__(self):
        return True

    def __len__(self):
        return len(self.subs)

    def __contains__(self, name):
        return name in self.subs
    
    def clone(self, __name__=_marker, __parent__=_marker, **kw):
        """ Create a clone of the model object.  If ``__name__`` or
        ``__parent__`` is passed in, use the value to override the
        existing ``__name__`` or ``__parent__`` of the model.  If any
        extra keyword args are passed in, use these keywords to add to
        or override existing model keywords (attributes)."""
        oldkw = self.kw.copy()
        oldkw.update(kw)
        inst = self.__class__(self.__name__, self.__parent__, **oldkw)
        inst.subs = copy.deepcopy(self.subs)
        if __name__ is not _marker:
            inst.__name__ = __name__
        if __parent__ is not _marker:
            inst.__parent__ = __parent__
        return inst

class DummyRequest:
    """ A dummy request object (imitates a :term:`request` object).
    
    The ``params``, ``environ``, ``headers``, ``path``, and
    ``cookies`` arguments correspond to their :term`WebOb`
    equivalents.

    The ``post`` argument,  if passed, populates the request's
    ``POST`` attribute, but *not* ``params``, in order to allow testing
    that the app accepts data for a given view only from POST requests.
    This argument also sets ``self.method`` to "POST".

    Extra keyword arguments are assigned as attributes of the request
    itself.
    """
    implements(IRequest)
    method = 'GET'
    application_url = 'http://example.com'
    host = 'example.com:80'
    content_length = 0
    def __init__(self, params=None, environ=None, headers=None, path='/',
                 cookies=None, post=None, **kw):
        if environ is None:
            environ = {}
        if params is None:
            params = {}
        if headers is None:
            headers = {}
        if cookies is None:
            cookies = {}
        self.environ = environ
        self.headers = headers
        self.params = params
        self.cookies = cookies
        self.matchdict = {}
        self.GET = params
        if post is not None:
            self.method = 'POST'
            self.POST = post
        else:
            self.POST = params
        self.host_url = self.application_url
        self.path_url = self.application_url
        self.url = self.application_url
        self.path = path
        self.path_info = path
        self.script_name = ''
        self.path_qs = ''
        self.body = ''
        self.view_name = ''
        self.subpath = ()
        self.traversed = ()
        self.virtual_root_path = ()
        self.context = None
        self.root = None
        self.virtual_root = None
        self.marshalled = params # repoze.monty
        self.registry = get_current_registry()
        self.__dict__.update(kw)

def setUp(registry=None, request=None, hook_zca=True):
    """
    Set BFG registry and request thread locals for the duration of a
    single unit test.

    .. note:: The ``setUp`` function is new as of :mod:`repoze.bfg`
       1.1.

    Use this function in the ``setUp`` method of a unittest test case
    which directly or indirectly uses:

    - any of the ``register*`` functions in ``repoze.bfg.testing``
      (such as ``repoze.bfg.testing.registerModels``)

    - the ``repoze.bfg.threadlocal.get_current_registry`` or
      ``repoze.bfg.threadlocal.get_current_request`` functions.

    If you use the ``testing.register*`` APIs, or the
    ``get_current_*`` functions (or call :mod:`repoze.bfg` code that
    uses these functions) without calling ``setUp``,
    ``get_current_registry`` will return a *global* :term:`application
    registry`, which may cause unit tests to not be isolated with
    respect to registrations they perform.

    If the ``registry`` argument is ``None``, a new empty
    :term:`application registry` will be created (an instance of
    ``repoze.bfg.registry.Registry``).  If the argument is not
    ``None``, the value passed in should be an instance of the
    :mod:`repoze.bfg.registry.Registry` class or a suitable testing
    analogue.  After ``setUp`` is finished, the registry returned by
    the ``repoze.bfg.threadlocal.get_current_request`` function will
    be the passed (or constructed) registry until
    ``repoze.bfg.testing.tearDown`` is called (or
    ``repoze.bfg.testing.setUp`` is called again) .

    .. note:: The ``registry`` argument is new as of :mod:`repoze.bfg`
       1.2.

    When ``setUp`` is finished, the value of the ``request`` argument
    to ``setUp`` will be returned by the
    ``repoze.bfg.threadlocal.get_current_registry`` function until
    ``repoze.bfg.testing.tearDown`` is called (or
    ``repoze.bfg.testing.setUp`` is called again) ..

    .. note:: The ``request`` argument is new as of :mod:`repoze.bfg`
       1.2.

    If ``hook_zca`` is True, ``setUp`` will attempt to perform
    ``zope.component.getSiteManager.sethook(
    repoze.bfg.threadlocal.get_current_registry)``, which will cause
    the :term:`Zope Component Architecture` global API
    (e.g. ``getSiteManager``, ``getAdapter``, and so on) to use the
    registry constructed by ``setUp`` as the value it returns from
    ``zope.component.getSiteManager``.  If ``zope.component`` cannot
    be imported, or if ``hook_zca`` is ``False``, the hook will not be
    set.

    .. note:: The ``hook_zca`` argument is new as of :mod:`repoze.bfg`
       1.2.

    .. warning:: Although this method of tearing a test setup down
                 will never disappear, after :mod:`repoze.bfg` 1.2a6,
                 using the ``begin`` and ``end`` methods of a
                 ``Configurator`` are prefered to using
                 ``repoze.bfg.testing.setUp`` and
                 ``repoze.bfg.testing.tearDown``.  See
                 :ref:`unittesting_chapter` for more information.
    """
    manager.clear()
    if registry is None:
        registry = Registry('testing')
    config = Configurator(registry=registry)
    config.begin(request=request)
    if hook_zca:
        hook_zca_api()

def tearDown(unhook_zca=True):
    """Undo the effects ``repoze.bfg.testing.setUp``.  Use this
    function in the ``tearDown`` of a unit test that uses
    ``repoze.bfg.testing.setUp`` in its setUp method.

    .. note:: This function is new as of :mod:`repoze.bfg` 1.1.

    If the ``unhook_zca`` argument is ``True`` (the default), call
    ``zope.component.getSiteManager.reset()``.  This undoes the action
    of ``repze.bfg.testing.setUp`` called with ``hook_zca=True``.  If
    ``zope.component`` cannot be imported, ignore the argument.

    .. note:: The ``unhook_zca`` argument is new as of
       :mod:`repoze.bfg` 1.2.

    .. warning:: Although this method of tearing a test setup down
                 will never disappear, after :mod:`repoze.bfg` 1.2a6,
                 using the ``begin`` and ``end`` methods of a
                 ``Configurator`` are prefered to using
                 ``repoze.bfg.testing.setUp`` and
                 ``repoze.bfg.testing.tearDown``.  See
                 :ref:`unittesting_chapter` for more information.

    """
    if unhook_zca:
        unhook_zca_api()
    info = manager.pop()
    manager.clear()
    if info is not None:
        registry = info['registry']
        if hasattr(registry, '__init__') and hasattr(registry, '__name__'):
            try:
                registry.__init__(registry.__name__)
            except TypeError:
                # calling __init__ is largely for the benefit of
                # people who want to use the global ZCA registry;
                # however maybe somebody's using a registry we don't
                # understand, let's not blow up
                pass
    _clearContext() # XXX why?

def cleanUp(*arg, **kw):
    """ ``repoze.bfg.testing.cleanUp`` is an alias for
    ``repoze.bfg.testing.setUp``.  Although this function is
    effectively deprecated as of :mod:`repoze.bfg` 1.1, due to its
    extensive production usage, it will never be removed."""
    setUp(*arg, **kw)

def hook_zca_api():
    try:
        from zope.component import getSiteManager
        getSiteManager.sethook(get_current_registry)
    except ImportError: # pragma: no cover
        pass
    
def unhook_zca_api():
    try:
        from zope.component import getSiteManager
        getSiteManager.reset()
    except ImportError: # pragma: no cover
        pass
    
