import unittest
from zope.component.testing import PlacelessSetup
from zope.interface import Interface

class BFGTestCase(unittest.TestCase, PlacelessSetup):
    """ A class which inherits from both ``unittest.TestCase`` and
    ``zope.component.testing.PlacelessSetup`` that provides a
    convenience API for writing BFG-specific tests.  This class can be
    subclassed within test modules and those subclasses will be found
    by test loaders. Since this test case inherits from
    ``PlacelessSetup`` the Zope component architecture registry is set
    up and torn down between each test, which provides isolation
    between tests."""
    
    def setUp(self):
        PlacelessSetup.setUp(self)

    def tearDown(self):
        PlacelessSetup.tearDown(self)

    def registerSecurityPolicy(self, userid=None, groupids=(), permissive=True):
        """ Registers a ``repoze.bfg`` security policy using the
        userid ``userid`` and the group ids ``groupids``.  If
        ``permissive`` is true, a 'permissive' security policy is
        registered; this policy allows all access.  If ``permissive``
        is false, a nonpermissive security policy is registered; this
        policy denies all access.  To register your own (possibly more
        granular) security policy, see the ``registerSecurityPolicy``
        *function* in the testing package.  This function is most
        useful when dealing with code that uses the
        ``repoze.bfg.security``APIs named ``has_permission``,
        ``authenticated_userid``, effective_principals, and
        ``principals_allowed_by_permission``."""
        if permissive:
            policy = DummyAllowingSecurityPolicy(userid, groupids)
        else:
            policy = DummyDenyingSecurityPolicy(userid, groupids)
        return registerSecurityPolicy(policy)

    def registerModels(self, models):
        """ Registers a dictionary of models.  This is most useful for
        dealing with code that wants to call the
        ``repoze.bfg.traversal.find_model`` API.  This API is called
        with a path as one of its arguments.  If the dictionary you
        register when calling this method contains that path as a key
        (e.g. '/foo/bar' or 'foo'), the corresponding value will be
        returned to ``find_model`` (and thus to your code)."""
        traverser = make_traverser_factory(models)
        registerTraverserFactory(traverser)
        return models

    def registerTemplate(self, name):
        """ Registers a 'dummy' template renderer implementation and
        returns it. This is most useful when dealing with code that
        wants to call ``repoze.bfg.chameleon_zpt.render_template*``or
        ``repoze.bfg.chameleon_genshi.render_template*``.  If you call
        this method with the exact template path string that a call to
        one of the ``render_template`` functions uses, the dummy
        template will stand in for the real implementation.  The dummy
        template object will set attributes on itself corresponding to
        the non-path keyword arguments provided to the ``render``
        function.  You can then compare these values against what you
        expect.  """
        return registerTemplateRenderer(name)

    def registerEventListener(self, event_iface=Interface):
        """ Registers an event listener (aka 'subscriber') listening
        for events of the type ``event_iface`` and returns a list
        which is appended to by the subscriber.  When an event is
        dispatched that matches ``event_iface``, that event will be
        appended to the list.  You can then compare the values in the
        list to expected event notifications.  This method is useful
        when dealing with code that wants to call
        ``zope.component.event.dispatch``."""
        L = []
        def subscriber(event):
            L.append(event)
        registerSubscriber(subscriber, event_iface)
        return L

    def registerView(self, name, result='', view=None):
        """ Registers a ``repoze.bfg`` view function under the name
        ``name``.  The view will return a webob Response object with
        the ``result`` value as its body attribute.  To gain more
        control, if you pass in a non-None ``view``, this view
        function will be used instead of an automatically generated
        view function (and ``result`` is not used).  This method is
        useful when dealing with code that wants to call,
        e.g. ``repoze.bfg.view.render_view_to_response``."""
        if view is None:
            view = make_view(result)
        registerView(view, name)
        return view

    def registerViewPermission(self, name, result=True, viewpermission=None):
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
        policy is in effect (see ``registerSecurityPolicy``)."""
        from repoze.bfg.security import Allowed
        from repoze.bfg.security import Denied
        if result is True:
            result = Allowed('message')
        else:
            result = Denied('message')
        if viewpermission is None:
            viewpermission = make_view_permission(result)
        return registerViewPermission(viewpermission, name)

    def registerAdapter(self, impl, for_, provides, name=''):
        """ A shortcut for calling the Zope Component Architecture's
        global site manager's ``registerAdapter`` function.  The
        argument ordering matches that function's exactly.  Registers a
        ZCA adapter."""
        return registerAdapter(impl, for_, provides, name)

    def registerUtility(self, impl, iface, name=''):
        """ A shortcut for calling the Zope Component Architecture's
        global site manager's ``registerUtility`` function.  The
        argument ordering matches that function's exactly.  Registers
        a ZCA utility."""
        return registerUtility(impl, iface, name)

    def makeModel(self, name=None, parent=None):
        """ Returns a 'dummy' model object, with the model's
        ``__name__`` attribute set to the value of ``name``, and the
        model's ``__parent__`` attribute set to the value of
        ``parent``.  A dummy model has a ``__setitem__`` method and a
        ``__getitem__`` method.  The ``__setitem__`` method can be
        called with a key/value pair; the value will be decorated with
        a ``__parent__`` attribute pointing at the dummy object and a
        ``__name__`` attribute that is the value of the key.
        A dummy model has no other attributes or methods."""
        return DummyModel(name, parent)

    def makeRequest(self, path='/', params=None, environ=None, headers=None,
                    **kw):
        """ Returns a ``DummyRequest`` object (mimics a WebOb Request
        object) using ``path`` as the path.  If ``environ`` is
        non-None, it should contain keys that will form the request's
        environment.  If ``base_url`` is passed in, then the
        ``wsgi.url_scheme``, ``HTTP_HOST``, and ``SCRIPT_NAME`` will
        be filled in from that value.  If ``headers`` is not None,
        these will be used as ``request.headers``.  The returned
        request object will implement the ``repoze.bfg.IRequest``
        interface."""
        return makeRequest(path, params, environ, headers, **kw)
    
def registerUtility(impl, iface, name=''):
    import zope.component 
    gsm = zope.component.getGlobalSiteManager()
    gsm.registerUtility(impl, iface, name=name)
    return impl

def registerAdapter(impl, for_=Interface, provides=Interface, name=''):
    import zope.component
    gsm = zope.component.getGlobalSiteManager()
    if not isinstance(for_, (tuple, list)):
        for_ = (for_,)
    gsm.registerAdapter(impl, for_, provides, name=name)
    return impl

def registerSubscriber(subscriber, iface=Interface):
    import zope.component
    gsm = zope.component.getGlobalSiteManager()
    if not isinstance(iface, (tuple, list)):
        iface = (iface,)
    gsm.registerHandler(subscriber, iface)
    return subscriber

def registerTemplateRenderer(path, renderer=None, iface=None):
    if iface is None:
        from repoze.bfg.interfaces import ITestingTemplateRenderer
        iface = ITestingTemplateRenderer
    if renderer is None:
        renderer = DummyTemplateRenderer()
    return registerUtility(renderer, iface, path)

def registerSecurityPolicy(policy):
    from repoze.bfg.interfaces import ISecurityPolicy
    return registerUtility(policy, ISecurityPolicy)

def registerTraverserFactory(traverser, for_=Interface):
    from repoze.bfg.interfaces import ITraverserFactory
    return registerAdapter(traverser, for_, ITraverserFactory)

def registerView(view, name, for_=(Interface, Interface)):
    from repoze.bfg.interfaces import IView
    return registerAdapter(view, for_, IView, name)

def registerViewPermission(viewpermission, name, for_=(Interface, Interface)):
    from repoze.bfg.interfaces import IViewPermission
    return registerAdapter(viewpermission, for_, IViewPermission, name)

def makeRequest(path, environ=None, base_url=None, headers=None, **kw):
    return DummyRequest(path, environ, base_url, headers, **kw)

from zope.interface import implements
from repoze.bfg.interfaces import IRequest

class DummyRequest:
    implements(IRequest)
    def __init__(self, path, params=None, environ=None, headers=None, **kw):
        if environ is None:
            environ = {}
        if params is None:
            params = {}
        if headers is None:
            headers = {}
        self.environ = environ
        self.headers = headers
        self.params = params
        self.GET = params
        self.POST = params
        self.application_url = 'http://example.com'
        self.host_url = self.application_url
        self.path_url = self.application_url
        self.path = path
        self.path_info = path
        self.script_name = ''
        self.path_qs = ''
        self.url = self.application_url
        self.host = 'example.com:80'
        self.body = ''
        self.cookies = {}
        self.__dict__.update(kw)

class _DummySecurityPolicy:
    def __init__(self, userid=None, groupids=()):
        self.userid = userid
        self.groupids = groupids

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

class DummyAllowingSecurityPolicy(_DummySecurityPolicy):
    def permits(self, context, request, permission):
        return True

    def principals_allowed_by_permission(self, context, permission):
        return self.effective_principals(None)

class DummyDenyingSecurityPolicy(_DummySecurityPolicy):
    def permits(self, context, request, permission):
        return False

    def principals_allowed_by_permission(self, context, permission):
        return []

def make_traverser_factory(root):
    class DummyTraverserFactory:
        def __init__(self, context):
            self.context = context

        def __call__(self, environ):
            ob = root[environ['PATH_INFO']]
            return ob, '', []

    return DummyTraverserFactory

class DummyTemplateRenderer:
    def implementation(self):
        return None
    
    def __call__(self, **kw):
        self.__dict__.update(kw)
        return ''

def make_view(result):
    def dummy_view(context, request):
        from webob import Response
        return Response(result)
    return dummy_view

def make_view_permission(result):
    class DummyViewPermission:
        def __init__(self, context, request):
            self.context = context
            self.request = request

        def __call__(self, secpol):
            return result

    return DummyViewPermission
        
class DummyModel:
    def __init__(self, name=None, parent=None):
        self.__name__ = name
        self.__parent__ = parent
        self.subs = {}

    def __setitem__(self, name, val):
        val.__name__ = name
        val.__parent__ = self
        self.subs[name] = val
        
    def __getitem__(self, name):
        ob = self.subs[name]
        return ob
    
