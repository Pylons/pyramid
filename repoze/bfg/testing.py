import copy

from zope.configuration.xmlconfig import _clearContext
from zope.component import getSiteManager
from zope.deprecation import deprecated
from zope.interface import implements
from zope.interface import Interface

from repoze.bfg.interfaces import IRequest

from repoze.bfg.configuration import zcml_configure # API import alias
from repoze.bfg.registry import Registry

_marker = object()

def registerDummySecurityPolicy(userid=None, groupids=(), permissive=True):
    """ Registers a dummy ``repoze.bfg`` security policy (actually, a
    pair of policies: an authorization policy and an authentication
    policy) using the userid ``userid`` and the group ids
    ``groupids``.  If ``permissive`` is true, a 'permissive' security
    policy is registered; this policy allows all access.  If
    ``permissive`` is false, a nonpermissive security policy is
    registered; this policy denies all access.  This function is most
    useful when testing code that uses the ``repoze.bfg.security``
    APIs named ``has_permission``, ``authenticated_userid``,
    ``effective_principals``, ``principals_allowed_by_permission``,
    and so on.
    """
    policy = DummySecurityPolicy(userid, groupids, permissive)
    from repoze.bfg.interfaces import IAuthorizationPolicy
    from repoze.bfg.interfaces import IAuthenticationPolicy
    registerUtility(policy, IAuthorizationPolicy)
    registerUtility(policy, IAuthenticationPolicy)

def registerModels(models):
    """ Registers a dictionary of models.  This is most useful for
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

        def __call__(self, environ):
            path = environ['PATH_INFO']
            ob = models[path]
            from repoze.bfg.traversal import traversal_path
            traversed = traversal_path(path)
            return {'context':ob, 'view_name':'','subpath':(),
                    'traversed':traversed, 'virtual_root':ob,
                    'virtual_root_path':(), 'root':ob}

    registerTraverserFactory(DummyTraverserFactory)
    return models

def registerEventListener(event_iface=Interface):
    """ Registers an event listener (aka 'subscriber') listening for
    events of the type ``event_iface`` and returns a list which is
    appended to by the subscriber.  When an event is dispatched that
    matches ``event_iface``, that event will be appended to the list.
    You can then compare the values in the list to expected event
    notifications.  This method is useful when testing code that wants
    to call ``zope.component.event.dispatch`` or
    ``zope.component.event.objectEventNotify``."""
    L = []
    def subscriber(*event):
        L.extend(event)
    registerSubscriber(subscriber, event_iface)
    return L

def registerTemplateRenderer(path, renderer=None):
    """ Register a 'template renderer' at ``path`` (usually a relative
    filename ala ``templates/foo.pt``) and return the renderer object.
    If the ``renderer`` argument is None, a 'dummy' renderer will be
    used.  This function is useful when testing code that calls the
    ``render_template_to_response`` or any other ``render_template*``
    API of any of the built-in templating systems."""
    from repoze.bfg.interfaces import ITemplateRenderer
    if renderer is None:
        renderer = DummyTemplateRenderer()
    return registerUtility(renderer, ITemplateRenderer, path)

# registerDummyRenderer is a deprecated alias that should never be removed
# (far too much usage in the wild)
registerDummyRenderer = registerTemplateRenderer

def registerView(name, result='', view=None, for_=(Interface, Interface),
                 permission=None):
    """ Registers ``repoze.bfg`` view function under the name
    ``name``.  The view will return a webob Response object with the
    ``result`` value as its body attribute.  To gain more control, if
    you pass in a non-None ``view``, this view function will be used
    instead of an automatically generated view function (and
    ``result`` is not used).  To protect the view using a permission,
    pass in a non-``None`` value as ``permission``.  This permission
    will be checked by any existing security policy when view
    execution is attempted.  This function is useful when dealing with
    code that wants to call,
    e.g. ``repoze.bfg.view.render_view_to_response``."""
    from repoze.bfg.interfaces import IView
    from repoze.bfg.interfaces import ISecuredView
    from repoze.bfg.security import has_permission
    from repoze.bfg.exceptions import Forbidden
    if view is None:
        def view(context, request):
            from webob import Response
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
    """ Registers a ``repoze.bfg`` 'view permission' object under
    the name ``name``.  The view permission return a result
    denoted by the ``result`` argument.  If ``result`` is True, a
    ``repoze.bfg.security.Allowed`` object is returned; else a
    ``repoze.bfg.security.Denied`` object is returned.  To gain
    more control, if you pass in a non-None ``viewpermission``,
    this view permission object will be used instead of an
    automatically generated view permission (and ``result`` is not
    used).  This method is useful when dealing with code that
    wants to call, e.g. ``repoze.bfg.view.view_execution_permitted``.
    Note that view permissions are not checked unless a security
    policy is in effect (see ``registerSecurityPolicy``).

    **This function was deprecated in repoze.bfg 1.1.**
    """
    from repoze.bfg.security import Allowed
    from repoze.bfg.security import Denied
    if result is True:
        result = Allowed('message')
    else:
        result = Denied('message')
    if viewpermission is None:
        def viewpermission(context, request):
            return result
    from repoze.bfg.interfaces import IViewPermission
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
    """ Register a Zope component architecture utility component.
    This is exposed as a convenience in this package to avoid needing
    to import the ``registerUtility`` function from ``zope.component``
    within unit tests that make use of the ZCA.  ``impl`` is the
    implementation of the utility.  ``iface`` is the interface type
    ``zope.interface.Interface`` by default.  ``name`` is the empty
    string by default.  See `The ZCA book
    <http://www.muthukadan.net/docs/zca.html>`_ for more information
    about ZCA utilities."""
    import zope.component 
    sm = zope.component.getSiteManager()
    sm.registerUtility(impl, iface, name=name)
    return impl

def registerAdapter(impl, for_=Interface, provides=Interface, name=''):
    """ Register a Zope component architecture adapter component.
    This is exposed as a convenience in this package to avoid needing
    to import the ``registerAdapter`` function from ``zope.component``
    within unit tests that make use of the ZCA.  ``impl`` is the
    implementation of the component (often a class).  ``for_`` is the
    ``for`` interface type ``zope.interface.Interface`` by default. If
    ``for`` is not a tuple or list, it will be converted to a
    one-tuple before being passed to underlying ZCA registerAdapter
    API.  ``name`` is the empty string by default.  ``provides`` is
    the ZCA provides interface, also ``zope.interface.Interface`` by
    default.  ``name`` is the name of the adapter, the empty string by
    default.  See `The ZCA book
    <http://www.muthukadan.net/docs/zca.html>`_ for more information
    about ZCA adapters."""
    import zope.component
    sm = zope.component.getSiteManager()
    if not isinstance(for_, (tuple, list)):
        for_ = (for_,)
    sm.registerAdapter(impl, for_, provides, name=name)
    return impl

def registerSubscriber(subscriber, iface=Interface):
    """ Register a Zope component architecture subscriber component.
    This is exposed as a convenience in this package to avoid needing
    to import the ``registerHandler`` function from ``zope.component``
    within unit tests that make use of the ZCA.  ``subscriber`` is the
    implementation of the component (often a function).  ``iface`` is
    the interface type the subscriber will be registered for
    (``zope.interface.Interface`` by default). If ``iface`` is not a
    tuple or list, it will be converted to a one-tuple before being
    passed to underlying zca registerHandler query.  See `The ZCA book
    <http://www.muthukadan.net/docs/zca.html>`_ for more information
    about ZCA subscribers."""
    import zope.component
    sm = zope.component.getSiteManager()
    if not isinstance(iface, (tuple, list)):
        iface = (iface,)
    sm.registerHandler(subscriber, iface)
    return subscriber

def registerTraverserFactory(traverser, for_=Interface):
    from repoze.bfg.interfaces import ITraverserFactory
    return registerAdapter(traverser, for_, ITraverserFactory)

def registerRoute(path, name, factory=None):
    """ Register a new route using a path (e.g. ``:pagename``), a name
    (e.g. 'home'), and an optional root factory.  This is useful for
    testing code that calls e.g. ``route_url``."""
    from repoze.bfg.interfaces import IRoutesMapper
    from zope.component import queryUtility
    from repoze.bfg.urldispatch import RoutesRootFactory
    mapper = queryUtility(IRoutesMapper)
    if mapper is None:
        mapper = RoutesRootFactory(DummyRootFactory)
        sm = getSiteManager()
        sm.registerUtility(mapper, IRoutesMapper)
    mapper.connect(path, name, factory)

class DummyRootFactory(object):
    __parent__ = None
    __name__ = None
    def __init__(self, environ):
        if 'bfg.routes.matchdict' in environ:
            self.__dict__.update(environ['bfg.routes.matchdict'])

class DummySecurityPolicy:
    """ A standin for both an IAuthentication and IAuthorization policy """
    def __init__(self, userid=None, groupids=(), permissive=True):
        self.userid = userid
        self.groupids = groupids
        self.permissive = permissive

    def authenticated_userid(self, request):
        return self.userid

    def effective_principals(self, request):
        from repoze.bfg.security import Everyone
        from repoze.bfg.security import Authenticated
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
    ``registerTemplateRenderer``.  It has a helper function (``assert_``)
    that makes it possible to make an assertion which compares data
    passed to the renderer by the view function against expected
    key/value pairs. 
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
    def __init__(self, __name__=None, __parent__=None, **kw):
        """ The he model's ``__name__`` attribute will be set to the
        value of ``__name__``, and the model's ``__parent__``
        attribute will be set to the value of ``__parent__``.  Any
        extra keywords will be set as direct attributes of the model."""
        self.__name__ = __name__
        self.__parent__ = __parent__
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
    """ A dummy request object (imitates a :term:`WebOb` ``Request`` object).
    
    The ``params``, ``environ``, ``headers``, ``path``, and ``cookies`` 
    arguments  correspond to their WebOb equivalents.

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
        self.registry = getSiteManager()
        self.__dict__.update(kw)

def setUp():
    """Set up a fresh BFG testing registry.  Use in the ``setUp``
    method of unit tests that use the ``register*`` methods in the
    testing module (e.g. if your unit test uses
    ``repoze.bfg.testing.registerDummySecurityPolicy``).  If you use
    the ``register*`` functions without calling ``setUp``, unit tests
    will not be isolated with respect to registrations they perform.
    Additionally, the *global* component registry will be used, which
    may have a different API than is expected by BFG itself.

    .. note:: This feature is new as of :mod:`repoze.bfg` 1.1.
    """
    registry = Registry('testing')
    getSiteManager.sethook(lambda *arg: registry)
    _clearContext()

def tearDown():
    """Tear down a previously set up (via
    ``repoze.bfg.testing.setUp``) testing registry.  Use in the
    ``tearDown`` method of unit tests that use the ``register*``
    methods in the testing module (e.g. if your unit test uses
    ``repoze.bfg.testing.registerDummySecurityPolicy``).  Using
    ``tearDown`` is effectively optional if you call setUp at the
    beginning of every test which requires registry isolation.

    .. note:: This feature is new as of :mod:`repoze.bfg` 1.1.

    """
    getSiteManager.reset()

def cleanUp():
    """ Deprecated (as of BFG 1.1) function whichs sets up a new
    registry for BFG testing registrations.  Use in the ``setUp`` and
    ``tearDown`` of unit tests that use the ``register*`` methods in
    the testing module (e.g. if your unit test uses
    ``repoze.bfg.testing.registerDummySecurityPolicy``).  Use of this
    function is deprecated in favor of using
    ``repoze.bfg.testing.setUp`` in the test setUp and
    ``repoze.bfg.testing.tearDown`` in the test tearDown.  This is
    currently just an alias for ``repoze.bfg.testing.setUp``.
    Although this function is effectively deprecated, due to its
    extensive production usage, it will never be removed."""
    setUp()
