import copy

from zope.interface import Interface
from zope.interface import implements

from repoze.bfg.interfaces import IRequest

_marker = ()

def registerDummySecurityPolicy(userid=None, groupids=(), permissive=True):
    """ Registers a dummy ``repoze.bfg`` security policy using the
    userid ``userid`` and the group ids ``groupids``.  If
    ``permissive`` is true, a 'permissive' security policy is
    registered; this policy allows all access.  If ``permissive`` is
    false, a nonpermissive security policy is registered; this policy
    denies all access.  This function is most useful when testing code
    that uses the ``repoze.bfg.security`` APIs named
    ``has_permission``, ``authenticated_userid``,
    ``effective_principals``, and ``principals_allowed_by_permission``.
    """
    if permissive:
        policy = DummyAllowingSecurityPolicy(userid, groupids)
    else:
        policy = DummyDenyingSecurityPolicy(userid, groupids)
    from repoze.bfg.interfaces import ISecurityPolicy
    return registerUtility(policy, ISecurityPolicy)

def registerModels(models):
    """ Registers a dictionary of models.  This is most useful for
    testing code that wants to call the
    ``repoze.bfg.traversal.find_model`` API.  The ``find_model`` API
    is called with a path as one of its arguments.  If the dictionary
    you register when calling this method contains that path as a key
    (e.g. '/foo/bar' or 'foo'), the corresponding value will be
    returned to ``find_model`` (and thus to your code)."""
    traverser = make_traverser_factory(models)
    registerTraverserFactory(traverser)
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

def registerDummyRenderer(path):
    """ Create and register a dummy template renderer at ``path``
    (usually a relative filename ala ``templates/foo.pt``) and return
    the renderer object.  This function is useful when testing code
    that calls the ``render_template_to_response`` or any other
    ``render_template*`` API of any of the built-in templating
    systems."""
    from repoze.bfg.interfaces import ITestingTemplateRenderer
    renderer = DummyTemplateRenderer()
    return registerUtility(renderer, ITestingTemplateRenderer, path)

def registerView(name, result='', view=None, for_=(Interface, Interface)):
    """ Registers ``repoze.bfg`` view function under the name
    ``name``.  The view will return a webob Response object with the
    ``result`` value as its body attribute.  To gain more control, if
    you pass in a non-None ``view``, this view function will be used
    instead of an automatically generated view function (and
    ``result`` is not used).  This function is useful when dealing
    with code that wants to call,
    e.g. ``repoze.bfg.view.render_view_to_response``."""
    if view is None:
        view = make_view(result)
    from repoze.bfg.interfaces import IView
    return registerAdapter(view, for_, IView, name)

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
    policy is in effect (see ``registerSecurityPolicy``)."""
    from repoze.bfg.security import Allowed
    from repoze.bfg.security import Denied
    if result is True:
        result = Allowed('message')
    else:
        result = Denied('message')
    if viewpermission is None:
        viewpermission = make_view_permission(result)
    from repoze.bfg.interfaces import IViewPermission
    return registerAdapter(viewpermission, for_, IViewPermission, name)

def registerUtility(impl, iface=Interface, name=''):
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

def registerTraverserFactory(traverser, for_=Interface):
    from repoze.bfg.interfaces import ITraverserFactory
    return registerAdapter(traverser, for_, ITraverserFactory)

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
        return self
    
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

    def values(self):
        """ Return the values set by __setitem__ """
        return self.subs.values()

    def items(self):
        """ Return the items set by __setitem__ """
        return self.subs.items()

    def keys(self):
        """ Return the keys set by __setitem__ """
        return self.subs.keys()

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
    """ A dummy request object (imitates a :term:`WebOb` ``Request``
    object).  The named constructor arguments correspond to their
    WebOb equivalents.  Extra keyword arguments are assigned as
    attributes of the request itself."""
    implements(IRequest)
    method = 'GET'
    application_url = 'http://example.com'
    host = 'example.com:80'
    content_length = 0
    def __init__(self, params=None, environ=None, headers=None, path='/',
                 cookies=None, **kw):
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
        self.GET = params
        self.POST = params
        self.host_url = self.application_url
        self.path_url = self.application_url
        self.url = self.application_url
        self.path = path
        self.path_info = path
        self.script_name = ''
        self.path_qs = ''
        self.body = ''
        self.cookies = {}
        self.view_name = ''
        self.subpath = []
        self.context = None
        self.marshalled = params # repoze.monty
        self.__dict__.update(kw)

