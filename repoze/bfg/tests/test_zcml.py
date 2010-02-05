import logging

logging.basicConfig()

import unittest

from repoze.bfg import testing

from zope.interface import Interface
from zope.interface import implements

class TestViewDirective(unittest.TestCase):
    def setUp(self):
        testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _callFUT(self, *arg, **kw):
        from repoze.bfg.zcml import view
        return view(*arg, **kw)

    def test_request_type_ashttpmethod(self):
        from repoze.bfg.threadlocal import get_current_registry
        from repoze.bfg.interfaces import IView
        from repoze.bfg.interfaces import IRequest
        context = DummyContext()
        view = lambda *arg: None
        self._callFUT(context, 'repoze.view', IDummy, view=view,
                      request_type='GET')
        actions = context.actions
        self.assertEqual(len(actions), 1)
        action = actions[0]
        discrim = ('view', IDummy, '', None, IView, None, None, 'GET', None,
                   None, False, None, None, None)
        self.assertEqual(action['discriminator'], discrim)
        register = action['callable']
        register()
        reg = get_current_registry()
        wrapper = reg.adapters.lookup((IRequest, IDummy), IView, name='')
        request = DummyRequest()
        request.method = 'GET'
        self.assertEqual(wrapper.__predicated__(None, request), True)
        request.method = 'POST'
        self.assertEqual(wrapper.__predicated__(None, request), False)
        
    def test_request_type_asinterfacestring(self):
        from zope.interface import directlyProvides
        from repoze.bfg.threadlocal import get_current_registry
        from repoze.bfg.interfaces import IView
        from repoze.bfg.interfaces import IRequest
        context = DummyContext(IDummy)
        view = lambda *arg: 'OK'
        self._callFUT(context, 'repoze.view', IDummy, view=view,
                      request_type='whatever')
        actions = context.actions
        self.assertEqual(len(actions), 1)
        discrim = ('view', IDummy, '', IDummy, IView, None, None, None, None,
                   None, False, None, None, None)
        self.assertEqual(actions[0]['discriminator'], discrim)
        register = actions[0]['callable']
        register()
        reg = get_current_registry()
        regview = reg.adapters.lookup((IRequest, IDummy), IView, name='')
        self.assertNotEqual(view, regview)
        request = DummyRequest()
        directlyProvides(request, IDummy)
        result = regview(None, request)
        self.assertEqual(result, 'OK')
        self.failIf(hasattr(view, '__call_permissive__'))

    def test_request_type_asnoninterfacestring(self):
        from repoze.bfg.exceptions import ConfigurationError
        context = DummyContext('notaninterface')
        view = lambda *arg: 'OK'
        self.assertRaises(ConfigurationError,
                          self._callFUT,
                          context, 'repoze.view', IDummy, view=view,
                          request_type='whatever')

    def test_with_dotted_renderer(self):
        from repoze.bfg.threadlocal import get_current_registry
        from repoze.bfg.interfaces import IView
        from repoze.bfg.interfaces import IRendererFactory
        from repoze.bfg.interfaces import IRequest
        context = DummyContext()
        reg = get_current_registry()
        def factory(path):
            def foo(*arg):
                return 'OK'
            return foo
        reg.registerUtility(factory, IRendererFactory, name='.pt')
        view = lambda *arg: None
        self._callFUT(context, 'repoze.view', IDummy, view=view,
                      renderer='foo/template.pt')
        actions = context.actions
        self.assertEqual(len(actions), 1)
        discrim = ('view', IDummy, '', None, IView, None, None, None, None,
                   None, False, None, None, None)
        self.assertEqual(actions[0]['discriminator'], discrim)
        register = actions[0]['callable']
        register()
        regview = reg.adapters.lookup((IRequest, IDummy), IView, name='')
        self.assertEqual(regview(None, None).body, 'OK')

    def test_with_custom_predicates(self):
        from repoze.bfg.threadlocal import get_current_registry
        from repoze.bfg.interfaces import IView
        from repoze.bfg.interfaces import IRequest
        context = DummyContext()
        reg = get_current_registry()
        view = lambda *arg: 'OK'
        def pred1(context, request):
            return True
        def pred2(context, request):
            return True
        preds = (pred1, pred2)
        self._callFUT(context, 'repoze.view', IDummy, view=view,
                      custom_predicates=preds)
        actions = context.actions
        self.assertEqual(len(actions), 1)
        discrim = ('view', IDummy, '', None, IView, None, None, None, None,
                   None, False, None, None, None)
        discrim = discrim + tuple(sorted(preds))
        self.assertEqual(actions[0]['discriminator'], discrim)
        register = actions[0]['callable']
        register()
        regview = reg.adapters.lookup((IRequest, IDummy), IView, name='')
        self.assertEqual(regview(None, None), 'OK')

    def test_context_trumps_for(self):
        from repoze.bfg.threadlocal import get_current_registry
        from repoze.bfg.interfaces import IView
        from repoze.bfg.interfaces import IRequest
        context = DummyContext()
        reg = get_current_registry()
        view = lambda *arg: 'OK'
        class Foo:
            pass
        self._callFUT(context, 'repoze.view', for_=Foo, view=view,
                      context=IDummy)
        actions = context.actions
        self.assertEqual(len(actions), 1)
        discrim = ('view', IDummy, '', None, IView, None, None, None, None,
                   None, False, None, None, None)
        self.assertEqual(actions[0]['discriminator'], discrim)
        register = actions[0]['callable']
        register()
        regview = reg.adapters.lookup((IRequest, IDummy), IView, name='')
        self.assertEqual(regview(None, None), 'OK')

    def test_with_for(self):
        from repoze.bfg.threadlocal import get_current_registry
        from repoze.bfg.interfaces import IView
        from repoze.bfg.interfaces import IRequest
        context = DummyContext()
        reg = get_current_registry()
        view = lambda *arg: 'OK'
        class Foo:
            pass
        self._callFUT(context, 'repoze.view', for_=IDummy, view=view)
        actions = context.actions
        self.assertEqual(len(actions), 1)
        discrim = ('view', IDummy, '', None, IView, None, None, None, None,
                   None, False, None, None, None)
        self.assertEqual(actions[0]['discriminator'], discrim)
        register = actions[0]['callable']
        register()
        regview = reg.adapters.lookup((IRequest, IDummy), IView, name='')
        self.assertEqual(regview(None, None), 'OK')

class TestNotFoundDirective(unittest.TestCase):
    def setUp(self):
        testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _callFUT(self, context, view):
        from repoze.bfg.zcml import notfound
        return notfound(context, view)
    
    def test_it(self):
        from repoze.bfg.threadlocal import get_current_registry
        from repoze.bfg.interfaces import INotFoundView

        context = DummyContext()
        def view(request):
            return 'OK'
        self._callFUT(context, view)
        actions = context.actions
        self.assertEqual(len(actions), 1)

        regadapt = actions[0]
        self.assertEqual(regadapt['discriminator'], INotFoundView)
        register = regadapt['callable']
        register()
        reg = get_current_registry()
        derived_view = reg.getUtility(INotFoundView)
        self.assertEqual(derived_view(None, None), 'OK')
        self.assertEqual(derived_view.__name__, view.__name__)

class TestForbiddenDirective(unittest.TestCase):
    def setUp(self):
        testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _callFUT(self, context, view):
        from repoze.bfg.zcml import forbidden
        return forbidden(context, view)
    
    def test_it(self):
        from repoze.bfg.threadlocal import get_current_registry
        context = DummyContext()
        def view(request):
            return 'OK'
        self._callFUT(context, view)
        actions = context.actions
        from repoze.bfg.interfaces import IForbiddenView

        self.assertEqual(len(actions), 1)

        regadapt = actions[0]
        self.assertEqual(regadapt['discriminator'], IForbiddenView)
        register = regadapt['callable']
        register()
        reg = get_current_registry()
        derived_view = reg.getUtility(IForbiddenView)
        self.assertEqual(derived_view(None, None), 'OK')
        self.assertEqual(derived_view.__name__, view.__name__)

class TestSystemViewHandler(unittest.TestCase):
    def setUp(self):
        testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _makeOne(self, iface):
        from repoze.bfg.zcml import SystemViewHandler
        return SystemViewHandler(iface)

    def test_no_view_no_renderer(self):
        handler = self._makeOne(IDummy)
        from repoze.bfg.exceptions import ConfigurationError
        context = DummyContext()
        handler(context)
        actions = context.actions
        self.assertEqual(len(actions), 1)
        regadapt = actions[0]
        self.assertEqual(regadapt['discriminator'], IDummy)
        register = regadapt['callable']
        self.assertRaises(ConfigurationError, register)
    
    def test_no_view_with_renderer(self):
        from repoze.bfg.threadlocal import get_current_registry
        from repoze.bfg.interfaces import IRendererFactory
        reg = get_current_registry()
        def renderer(path):
            return lambda *arg: 'OK'
        reg.registerUtility(renderer, IRendererFactory, name='dummy')
        context = DummyContext()
        handler = self._makeOne(IDummy)
        handler(context, renderer='dummy')
        actions = context.actions
        self.assertEqual(len(actions), 1)
        regadapt = actions[0]
        self.assertEqual(regadapt['discriminator'], IDummy)
        register = regadapt['callable']
        register()
        derived_view = reg.getUtility(IDummy)
        request = DummyRequest()
        self.assertEqual(derived_view(None, request).body, 'OK')

    def test_template_renderer(self):
        from repoze.bfg.threadlocal import get_current_registry
        from repoze.bfg.interfaces import IRendererFactory
        reg = get_current_registry()
        def renderer(path):
            return lambda *arg: 'OK'
        reg.registerUtility(renderer, IRendererFactory, name='.pt')
        context = DummyContext()
        handler = self._makeOne(IDummy)
        handler(context, renderer='fixtures/minimal.pt')
        actions = context.actions
        self.assertEqual(len(actions), 1)
        regadapt = actions[0]
        self.assertEqual(regadapt['discriminator'], IDummy)
        register = regadapt['callable']
        register()
        derived_view = reg.getUtility(IDummy)
        request = DummyRequest()
        self.assertEqual(derived_view(None, request).body, 'OK')

class TestRepozeWho1AuthenticationPolicyDirective(unittest.TestCase):
    def setUp(self):
        testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _callFUT(self, context, **kw):
        from repoze.bfg.zcml import repozewho1authenticationpolicy
        return repozewho1authenticationpolicy(context, **kw)

    def test_it_defaults(self):
        from repoze.bfg.threadlocal import get_current_registry
        reg = get_current_registry()
        from repoze.bfg.interfaces import IAuthenticationPolicy
        context = DummyContext()
        self._callFUT(context)
        actions = context.actions
        self.assertEqual(len(actions), 1)
        regadapt = actions[0]
        self.assertEqual(regadapt['discriminator'], IAuthenticationPolicy)
        self.assertEqual(regadapt['callable'], None)
        self.assertEqual(regadapt['args'], ())
        policy = reg.getUtility(IAuthenticationPolicy)
        self.assertEqual(policy.callback, None)
        self.assertEqual(policy.identifier_name, 'auth_tkt')
    
    def test_it(self):
        from repoze.bfg.threadlocal import get_current_registry
        reg = get_current_registry()
        from repoze.bfg.interfaces import IAuthenticationPolicy
        context = DummyContext()
        def callback(identity, request):
            """ """
        self._callFUT(context, identifier_name='something', callback=callback)
        actions = context.actions
        self.assertEqual(len(actions), 1)
        regadapt = actions[0]
        self.assertEqual(regadapt['discriminator'], IAuthenticationPolicy)
        self.assertEqual(regadapt['callable'], None)
        self.assertEqual(regadapt['args'], ())
        policy = reg.getUtility(IAuthenticationPolicy)
        self.assertEqual(policy.callback, callback)
        self.assertEqual(policy.identifier_name, 'something')

class TestRemoteUserAuthenticationPolicyDirective(unittest.TestCase):
    def setUp(self):
        testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _callFUT(self, context, **kw):
        from repoze.bfg.zcml import remoteuserauthenticationpolicy
        return remoteuserauthenticationpolicy(context, **kw)

    def test_defaults(self):
        from repoze.bfg.interfaces import IAuthenticationPolicy
        from repoze.bfg.threadlocal import get_current_registry
        reg = get_current_registry()
        context = DummyContext()
        def callback(identity, request):
            """ """
        self._callFUT(context)
        actions = context.actions
        self.assertEqual(len(actions), 1)
        regadapt = actions[0]
        self.assertEqual(regadapt['discriminator'], IAuthenticationPolicy)
        self.assertEqual(regadapt['callable'], None)
        self.assertEqual(regadapt['args'], ())
        policy = reg.getUtility(IAuthenticationPolicy)
        self.assertEqual(policy.environ_key, 'REMOTE_USER')
        self.assertEqual(policy.callback, None)

    def test_it(self):
        from repoze.bfg.interfaces import IAuthenticationPolicy
        from repoze.bfg.threadlocal import get_current_registry
        context = DummyContext()
        def callback(identity, request):
            """ """
        self._callFUT(context, environ_key='BLAH', callback=callback)
        actions = context.actions
        self.assertEqual(len(actions), 1)
        regadapt = actions[0]
        self.assertEqual(regadapt['discriminator'], IAuthenticationPolicy)
        self.assertEqual(regadapt['callable'], None)
        self.assertEqual(regadapt['args'], ())
        reg = get_current_registry()
        policy = reg.getUtility(IAuthenticationPolicy)
        self.assertEqual(policy.environ_key, 'BLAH')
        self.assertEqual(policy.callback, callback)

class TestAuthTktAuthenticationPolicyDirective(unittest.TestCase):
    def setUp(self):
        testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _callFUT(self, context, secret, **kw):
        from repoze.bfg.zcml import authtktauthenticationpolicy
        return authtktauthenticationpolicy(context, secret, **kw)

    def test_it_defaults(self):
        from repoze.bfg.interfaces import IAuthenticationPolicy
        from repoze.bfg.threadlocal import get_current_registry
        reg = get_current_registry()
        context = DummyContext()
        self._callFUT(context, 'sosecret')
        actions = context.actions
        self.assertEqual(len(actions), 1)
        regadapt = actions[0]
        self.assertEqual(regadapt['discriminator'], IAuthenticationPolicy)
        self.assertEqual(regadapt['callable'], None)
        self.assertEqual(regadapt['args'], ())
        policy = reg.getUtility(IAuthenticationPolicy)
        self.assertEqual(policy.cookie.secret, 'sosecret')
        self.assertEqual(policy.callback, None)

    def test_it_noconfigerror(self):
        from repoze.bfg.interfaces import IAuthenticationPolicy
        from repoze.bfg.threadlocal import get_current_registry
        reg = get_current_registry()
        context = DummyContext()
        def callback(identity, request):
            """ """
        self._callFUT(context, 'sosecret', callback=callback,
                      cookie_name='repoze.bfg.auth_tkt',
                      secure=True, include_ip=True, timeout=100,
                      reissue_time=60, http_only=True, path="/sub/")
        actions = context.actions
        self.assertEqual(len(actions), 1)
        regadapt = actions[0]
        self.assertEqual(regadapt['discriminator'], IAuthenticationPolicy)
        self.assertEqual(regadapt['callable'], None)
        self.assertEqual(regadapt['args'], ())
        policy = reg.getUtility(IAuthenticationPolicy)
        self.assertEqual(policy.cookie.path, '/sub/')
        self.assertEqual(policy.cookie.http_only, True)
        self.assertEqual(policy.cookie.secret, 'sosecret')
        self.assertEqual(policy.callback, callback)

    def test_it_configerror(self):
        from repoze.bfg.exceptions import ConfigurationError
        context = DummyContext()
        def callback(identity, request):
            """ """
        self.assertRaises(ConfigurationError,
                          self._callFUT,
                          context, 'sosecret', callback=callback,
                          cookie_name='repoze.bfg.auth_tkt',
                          secure=True, include_ip=True, timeout=100,
                          reissue_time=500, http_only=True,
                          path="/cgi-bin/bfg.cgi/")

class TestACLAuthorizationPolicyDirective(unittest.TestCase):
    def setUp(self):
        testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _callFUT(self, context, **kw):
        from repoze.bfg.zcml import aclauthorizationpolicy
        return aclauthorizationpolicy(context, **kw)
    
    def test_it(self):
        from repoze.bfg.threadlocal import get_current_registry
        from repoze.bfg.authorization import ACLAuthorizationPolicy
        from repoze.bfg.interfaces import IAuthorizationPolicy
        reg = get_current_registry()
        context = DummyContext()
        def callback(identity, request):
            """ """
        self._callFUT(context)
        actions = context.actions
        self.assertEqual(len(actions), 1)
        regadapt = actions[0]
        self.assertEqual(regadapt['discriminator'], IAuthorizationPolicy)
        self.assertEqual(regadapt['callable'], None)
        self.assertEqual(regadapt['args'], ())
        policy = reg.getUtility(IAuthorizationPolicy)
        self.assertEqual(policy.__class__, ACLAuthorizationPolicy)

class TestRouteDirective(unittest.TestCase):
    def setUp(self):
        testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _callFUT(self, *arg, **kw):
        from repoze.bfg.zcml import route
        return route(*arg, **kw)

    def _assertRoute(self, name, path, num_predicates=0):
        from repoze.bfg.threadlocal import get_current_registry
        from repoze.bfg.interfaces import IRoutesMapper
        reg = get_current_registry()
        mapper = reg.getUtility(IRoutesMapper)
        routes = mapper.get_routes()
        route = routes[0]
        self.assertEqual(len(routes), 1)
        self.assertEqual(route.name, name)
        self.assertEqual(route.path, path)
        self.assertEqual(len(routes[0].predicates), num_predicates)
        return route

    def test_with_view(self):
        from repoze.bfg.threadlocal import get_current_registry
        from zope.interface import Interface
        from repoze.bfg.interfaces import IView
        from repoze.bfg.interfaces import IRouteRequest
        context = DummyContext()
        view = lambda *arg: 'OK'
        self._callFUT(context, 'name', 'path', view=view)
        actions = context.actions
        self.assertEqual(len(actions), 2)

        route_action = actions[0]
        route_action['callable']()
        route_discriminator = route_action['discriminator']
        self.assertEqual(route_discriminator,
                         ('route', 'name', False, None, None, None, None,None))
        self._assertRoute('name', 'path')

        view_action = actions[1]
        reg = get_current_registry()
        request_type = reg.getUtility(IRouteRequest, 'name')
        view_discriminator = view_action['discriminator']
        discrim = ('view', None, '', None, IView, 'name', None)
        self.assertEqual(view_discriminator, discrim)
        wrapped = reg.adapters.lookup((request_type, Interface), IView, name='')
        self.failUnless(wrapped)

    def test_with_view_and_view_context(self):
        from repoze.bfg.threadlocal import get_current_registry
        from repoze.bfg.interfaces import IView
        from repoze.bfg.interfaces import IRouteRequest
        context = DummyContext()
        view = lambda *arg: 'OK'
        self._callFUT(context, 'name', 'path', view=view, view_context=IDummy)
        actions = context.actions
        self.assertEqual(len(actions), 2)

        route_action = actions[0]
        route_action['callable']()
        route_discriminator = route_action['discriminator']
        self.assertEqual(route_discriminator,
                         ('route', 'name', False, None, None, None, None,None))
        self._assertRoute('name', 'path')

        view_action = actions[1]
        reg = get_current_registry()
        request_type = reg.getUtility(IRouteRequest, 'name')
        view_discriminator = view_action['discriminator']
        discrim = ('view', IDummy, '', None, IView, 'name', None)
        self.assertEqual(view_discriminator, discrim)
        wrapped = reg.adapters.lookup((request_type, IDummy), IView, name='')
        self.failUnless(wrapped)

    def test_with_view_context_trumps_view_for(self):
        from repoze.bfg.threadlocal import get_current_registry
        from repoze.bfg.interfaces import IView
        from repoze.bfg.interfaces import IRouteRequest
        context = DummyContext()
        view = lambda *arg: 'OK'
        class Foo:
            pass
        self._callFUT(context, 'name', 'path', view=view, view_context=IDummy,
                      view_for=Foo)
        actions = context.actions
        self.assertEqual(len(actions), 2)

        route_action = actions[0]
        route_action['callable']()
        route_discriminator = route_action['discriminator']
        self.assertEqual(route_discriminator,
                         ('route', 'name', False, None, None, None, None,None))
        self._assertRoute('name', 'path')

        view_action = actions[1]
        reg = get_current_registry()
        request_type = reg.getUtility(IRouteRequest, 'name')
        view_discriminator = view_action['discriminator']
        discrim = ('view', IDummy, '', None, IView, 'name', None)
        self.assertEqual(view_discriminator, discrim)
        wrapped = reg.adapters.lookup((request_type, IDummy), IView, name='')
        self.failUnless(wrapped)

    def test_with_dotted_renderer(self):

        from repoze.bfg.threadlocal import get_current_registry
        from zope.interface import Interface
        from repoze.bfg.interfaces import IView
        from repoze.bfg.interfaces import IRouteRequest


        from repoze.bfg.interfaces import IRendererFactory
        reg = get_current_registry()
        def renderer(path):
            return lambda *arg: 'OK'
        reg.registerUtility(renderer, IRendererFactory, name='.pt')

        context = DummyContext()
        view = lambda *arg: 'OK'
        self._callFUT(context, 'name', 'path', view=view,
                      renderer='fixtureapp/templates/foo.pt')
        actions = context.actions
        self.assertEqual(len(actions), 2)

        route_action = actions[0]
        route_action['callable']()
        route_discriminator = route_action['discriminator']
        self.assertEqual(route_discriminator,
                         ('route', 'name', False, None, None, None, None,None))
        self._assertRoute('name', 'path')

        view_action = actions[1]
        request_type = reg.getUtility(IRouteRequest, 'name')
        view_discriminator = view_action['discriminator']
        discrim = ('view', None, '', None, IView, 'name', None)
        self.assertEqual(view_discriminator, discrim)
        wrapped = reg.adapters.lookup((request_type, Interface), IView, name='')
        self.failUnless(wrapped)
        request = DummyRequest()
        result = wrapped(None, request)
        self.assertEqual(result.body, 'OK')

    def test_with_custom_predicates(self):
        def pred1(context, request): pass
        def pred2(context, request): pass
        preds = tuple(sorted([pred1, pred2]))

        context = DummyContext()
        self._callFUT(context, 'name', 'path', custom_predicates=(pred1, pred2))
        actions = context.actions
        self.assertEqual(len(actions), 1)

        route_action = actions[0]
        route_action['callable']()
        route_discriminator = route_action['discriminator']
        self.assertEqual(
            route_discriminator,
            ('route', 'name', False, None, None, None, None,None) + preds)
        self._assertRoute('name', 'path', 2)

class TestStaticDirective(unittest.TestCase):
    def setUp(self):
        testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _callFUT(self, *arg, **kw):
        from repoze.bfg.zcml import static
        return static(*arg, **kw)

    def test_it(self):
        from repoze.bfg.static import PackageURLParser
        from repoze.bfg.threadlocal import get_current_registry
        from zope.interface import implementedBy
        from repoze.bfg.static import StaticRootFactory
        from repoze.bfg.interfaces import IView
        from repoze.bfg.interfaces import IRouteRequest
        from repoze.bfg.interfaces import IRoutesMapper
        context = DummyContext()
        self._callFUT(context, 'name', 'fixtures/static')
        actions = context.actions
        self.assertEqual(len(actions), 2)

        reg = get_current_registry()

        route_action = actions[0]
        discriminator = route_action['discriminator']
        self.assertEqual(discriminator,
                         ('route', 'name', False, None, None, None, None, None))
        route_action['callable'](*route_action['args'])
        mapper = reg.getUtility(IRoutesMapper)
        routes = mapper.get_routes()
        self.assertEqual(len(routes), 1)
        self.assertEqual(routes[0].path, 'name*subpath')
        self.assertEqual(routes[0].name, 'name')

        view_action = actions[1]
        discriminator = view_action['discriminator']
        self.assertEqual(discriminator[:3], ('view', StaticRootFactory, ''))
        self.assertEqual(discriminator[4], IView)
        iface = implementedBy(StaticRootFactory)
        request_type = reg.getUtility(IRouteRequest, 'name')
        view = reg.adapters.lookup((request_type, iface), IView, name='')
        request = DummyRequest()
        self.assertEqual(view(None, request).__class__, PackageURLParser)


class TestResourceDirective(unittest.TestCase):
    def setUp(self):
        testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _callFUT(self, *arg, **kw):
        from repoze.bfg.zcml import resource
        return resource(*arg, **kw)

    def test_it(self):
        from repoze.bfg.configuration import Configurator
        context = DummyContext()
        self._callFUT(context, 'a', 'b')
        actions = context.actions
        self.assertEqual(len(actions), 1)
        action = actions[0]
        self.assertEqual(action['callable'].im_func,
                         Configurator.override_resource.im_func)
        self.assertEqual(action['discriminator'], None)
        self.assertEqual(action['args'], ('a', 'b', None))


class TestRendererDirective(unittest.TestCase):
    def setUp(self):
        testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _callFUT(self, *arg, **kw):
        from repoze.bfg.zcml import renderer
        return renderer(*arg, **kw)

    def test_it(self):
        from repoze.bfg.threadlocal import get_current_registry
        from repoze.bfg.interfaces import IRendererFactory
        context = DummyContext()
        renderer = lambda *arg, **kw: None
        self._callFUT(context, renderer, 'r')
        actions = context.actions
        self.assertEqual(len(actions), 1)
        action = actions[0]
        self.assertEqual(action['discriminator'], (IRendererFactory, 'r'))
        reg = get_current_registry()
        self.failUnless(reg.getUtility(IRendererFactory, 'r'), renderer)
    
class TestZCMLConfigure(unittest.TestCase):
    i = 0
    def _callFUT(self, path, package):
        from repoze.bfg.zcml import zcml_configure
        return zcml_configure(path, package)
    
    def setUp(self):
        testing.setUp()
        self.tempdir = None
        import sys
        import os
        import tempfile
        from repoze.bfg.path import package_path
        from repoze.bfg.tests import fixtureapp as package
        import shutil
        tempdir = tempfile.mkdtemp()
        modname = 'myfixture%s' % self.i
        self.i += 1
        self.packagepath = os.path.join(tempdir, modname)
        fixturedir = package_path(package)
        shutil.copytree(fixturedir, self.packagepath)
        sys.path.insert(0, tempdir)
        self.module = __import__(modname)
        self.tempdir = tempdir

    def tearDown(self):
        testing.tearDown()
        import sys
        import shutil
        if self.module is not None:
            del sys.modules[self.module.__name__]
        if self.tempdir is not None:
            sys.path.pop(0)
            shutil.rmtree(self.tempdir)

    def test_zcml_configure(self):
        actions = self._callFUT('configure.zcml', self.module)
        self.failUnless(actions)
        self.failUnless(isinstance(actions, list))

    def test_zcml_configure_nonexistent_configure_dot_zcml(self):
        import os
        os.remove(os.path.join(self.packagepath, 'configure.zcml'))
        self.assertRaises(IOError, self._callFUT, 'configure.zcml',
                          self.module)

class TestZCMLScanDirective(unittest.TestCase):
    def setUp(self):
        testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _callFUT(self, context, package):
        from repoze.bfg.zcml import scan
        return scan(context, package)

    def test_it(self):
        from repoze.bfg.configuration import Configurator
        dummy_module = DummyModule()
        context = DummyContext()
        self._callFUT(context, dummy_module)
        actions = context.actions
        self.assertEqual(len(actions), 1)
        action = actions[0]
        self.assertEqual(action['callable'].im_func, Configurator.scan.im_func)
        self.assertEqual(action['discriminator'], None)
        self.assertEqual(action['args'], (dummy_module, None))


class TestAdapterDirective(unittest.TestCase):
    def setUp(self):
        testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _callFUT(self, *arg, **kw):
        from repoze.bfg.zcml import adapter
        return adapter(*arg, **kw)

    def test_for_is_None_no_adaptedBy(self):
        context = DummyContext()
        factory = DummyFactory()
        self.assertRaises(TypeError, self._callFUT, context, [factory],
                          provides=None, for_=None)

    def test_for_is_None_adaptedBy_still_None(self):
        context = DummyContext()
        factory = DummyFactory()
        factory.__component_adapts__ = None
        self.assertRaises(TypeError, self._callFUT, context, [factory],
                      provides=None, for_=None)

    def test_for_is_None_adaptedBy_set(self):
        from repoze.bfg.registry import Registry
        context = DummyContext()
        factory = DummyFactory()
        factory.__component_adapts__ = (IDummy,)
        self._callFUT(context, [factory], provides=IFactory, for_=None)
        self.assertEqual(len(context.actions), 1)
        regadapt = context.actions[0]
        self.assertEqual(regadapt['discriminator'],
                         ('adapter', (IDummy,), IFactory, ''))
        self.assertEqual(regadapt['callable'].im_func,
                         Registry.registerAdapter.im_func)
        self.assertEqual(regadapt['args'],
                         (factory, (IDummy,), IFactory, '', None))

    def test_provides_missing(self):
        context = DummyContext()
        factory = DummyFactory()
        self.assertRaises(TypeError, self._callFUT, context, [factory],
                          provides=None, for_=(IDummy,))

    def test_provides_obtained_via_implementedBy(self):
        from repoze.bfg.registry import Registry
        context = DummyContext()
        self._callFUT(context, [DummyFactory], for_=(IDummy,))
        regadapt = context.actions[0]
        self.assertEqual(regadapt['discriminator'],
                         ('adapter', (IDummy,), IFactory, ''))
        self.assertEqual(regadapt['callable'].im_func,
                         Registry.registerAdapter.im_func)
        self.assertEqual(regadapt['args'],
                         (DummyFactory, (IDummy,), IFactory, '', None))

    def test_multiple_factories_multiple_for(self):
        context = DummyContext()
        factory = DummyFactory()
        self.assertRaises(ValueError, self._callFUT, context,
                          [factory, factory],
                          provides=IFactory,
                          for_=(IDummy, IDummy))

    def test_no_factories_multiple_for(self):
        context = DummyContext()
        self.assertRaises(ValueError, self._callFUT, context,
                          factory=[],
                          provides=IFactory,
                          for_=(IDummy, IDummy))
        
    def test_rolled_up_factories(self):
        from repoze.bfg.registry import Registry
        context = DummyContext()
        factory = DummyFactory()
        self._callFUT(context,
                      [factory, factory],
                      provides=IFactory,
                      for_=(IDummy,))
        regadapt = context.actions[0]
        self.assertEqual(regadapt['discriminator'],
                         ('adapter', (IDummy,), IFactory, ''))
        self.assertEqual(regadapt['callable'].im_func,
                         Registry.registerAdapter.im_func)
        self.assertEqual(regadapt['args'][0].__module__, 'repoze.bfg.zcml')

class TestSubscriberDirective(unittest.TestCase):
    def setUp(self):
        testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _callFUT(self, *arg, **kw):
        from repoze.bfg.zcml import subscriber
        return subscriber(*arg, **kw)

    def test_no_factory_no_handler(self):
        context = DummyContext()
        self.assertRaises(TypeError,
                          self._callFUT, context, for_=None, factory=None,
                          handler=None,
                          provides=None)

    def test_handler_with_provides(self):
        context = DummyContext()
        self.assertRaises(TypeError,
                          self._callFUT, context, for_=None, factory=None,
                          handler=1, provides=1)

    def test_handler_and_factory(self):
        context = DummyContext()
        self.assertRaises(TypeError,
                          self._callFUT, context, for_=None, factory=1,
                          handler=1, provides=None)

    def test_no_provides_with_factory(self):
        context = DummyContext()
        self.assertRaises(TypeError,
                          self._callFUT, context, for_=None, factory=1,
                          handler=None, provides=None)

    def test_adapted_by_as_for_is_None(self):
        context = DummyContext()
        factory = DummyFactory()
        factory.__component_adapts__ = None
        self.assertRaises(TypeError, self._callFUT, context, for_=None,
                          factory=factory, handler=None, provides=IFactory)
        
    def test_register_with_factory(self):
        from repoze.bfg.registry import Registry
        context = DummyContext()
        factory = DummyFactory()
        self._callFUT(context, for_=(IDummy,),
                      factory=factory, handler=None, provides=IFactory)
        self.assertEqual(len(context.actions), 1)
        subadapt = context.actions[0]
        self.assertEqual(subadapt['discriminator'], None)
        self.assertEqual(subadapt['callable'].im_func,
                         Registry.registerSubscriptionAdapter.im_func)
        self.assertEqual(subadapt['args'],
                         (factory, (IDummy,), IFactory, None, None) )

    def test_register_with_handler(self):
        from repoze.bfg.configuration import Configurator
        context = DummyContext()
        factory = DummyFactory()
        self._callFUT(context, for_=(IDummy,),
                      factory=None, handler=factory)
        self.assertEqual(len(context.actions), 1)
        subadapt = context.actions[0]
        self.assertEqual(subadapt['discriminator'], None)
        self.assertEqual(subadapt['callable'].im_func,
                         Configurator.add_subscriber.im_func)
        self.assertEqual(subadapt['args'], (factory, (IDummy,), None) )

class TestUtilityDirective(unittest.TestCase):
    def setUp(self):
        testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _callFUT(self, *arg, **kw):
        from repoze.bfg.zcml import utility
        return utility(*arg, **kw)

    def test_factory_and_component(self):
        context = DummyContext()
        self.assertRaises(TypeError, self._callFUT,
                          context, factory=1, component=1)

    def test_missing_provides(self):
        context = DummyContext()
        self.assertRaises(TypeError, self._callFUT, context, provides=None)
        
    def test_provides_from_factory_implements(self):
        from repoze.bfg.registry import Registry
        context = DummyContext()
        self._callFUT(context, factory=DummyFactory)
        self.assertEqual(len(context.actions), 1)
        utility = context.actions[0]
        self.assertEqual(utility['discriminator'], ('utility', IFactory, ''))
        self.assertEqual(utility['callable'].im_func,
                         Registry.registerUtility.im_func)
        self.assertEqual(utility['args'], (None, IFactory, '', None))
        self.assertEqual(utility['kw'], {'factory':DummyFactory})

    def test_provides_from_component_provides(self):
        from repoze.bfg.registry import Registry
        context = DummyContext()
        component = DummyFactory()
        self._callFUT(context, component=component)
        self.assertEqual(len(context.actions), 1)
        utility = context.actions[0]
        self.assertEqual(utility['discriminator'], ('utility', IFactory, ''))
        self.assertEqual(utility['callable'].im_func,
                         Registry.registerUtility.im_func)
        self.assertEqual(utility['args'], (component, IFactory, '', None))
        self.assertEqual(utility['kw'], {})

class TestLoadZCML(unittest.TestCase):
    def setUp(self):
        testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def test_it(self):
        from zope.configuration import xmlconfig
        import repoze.bfg.includes
        xmlconfig.file('configure.zcml', package=repoze.bfg.includes)

class TestRolledUpFactory(unittest.TestCase):
    def _callFUT(self, *factories):
        from repoze.bfg.zcml import _rolledUpFactory
        return _rolledUpFactory(factories)

    def test_it(self):
        def foo(ob):
            return ob
        factory = self._callFUT(foo, foo)
        result = factory(True)
        self.assertEqual(result, True)

class Test_path_spec(unittest.TestCase):
    def _callFUT(self, context, path):
        from repoze.bfg.zcml import path_spec
        return path_spec(context, path)

    def test_no_package_attr(self):
        context = DummyContext()
        path = '/thepath'
        result = self._callFUT(context, path)
        self.assertEqual(result, path)

    def test_package_attr_None(self):
        context = DummyContext()
        context.package = None
        path = '/thepath'
        result = self._callFUT(context, path)
        self.assertEqual(result, path)

    def test_package_path_doesnt_start_with_abspath(self):
        context = DummyContext()
        context.package = DummyPackage('repoze.bfg.tests')
        path = '/thepath'
        result = self._callFUT(context, path)
        self.assertEqual(result, path)

    def test_package_path_starts_with_abspath(self):
        import pkg_resources
        import os
        context = DummyContext()
        package = DummyPackage('repoze.bfg.tests')
        package_path = pkg_resources.resource_filename('repoze.bfg.tests', '')
        template_path = os.path.join(package_path, 'templates/foo.pt')
        context.package = package
        result = self._callFUT(context, template_path)
        self.assertEqual(result, 'repoze.bfg.tests:templates/foo.pt')

    def test_package_name_is___main__(self):
        context = DummyContext()
        package = DummyPackage('__main__')
        context.package = package
        result = self._callFUT(context, '/foo.pt')
        self.assertEqual(result, '/foo.pt')

    def test_path_is_already_resource_spec(self):
        context = DummyContext()
        result = self._callFUT(context, 'repoze.bfg.tests:foo.pt')
        self.assertEqual(result, 'repoze.bfg.tests:foo.pt')

class IDummy(Interface):
    pass

class IFactory(Interface):
    pass

class DummyFactory(object):
    implements(IFactory)
    def __call__(self):
        """ """
        
class DummyModule:
    __path__ = "foo"
    __name__ = "dummy"
    __file__ = ''

class DummyContext:
    def __init__(self, resolved=DummyModule):
        self.actions = []
        self.info = None
        self.resolved = resolved
        self.package = None

    def action(self, discriminator, callable=None, args=(), kw={}, order=0):
        self.actions.append(
            {'discriminator':discriminator,
             'callable':callable,
             'args':args,
             'kw':kw}
            )

    def path(self, path):
        return path

    def resolve(self, dottedname):
        return self.resolved

class Dummy:
    pass

class DummyRoute:
    pass

class DummyRequest:
    subpath = ()
    def __init__(self, environ=None):
        if environ is None:
            environ = {}
        self.environ = environ
        self.path_info = environ.get('PATH_INFO', None)

    def get_response(self, app):
        return app

    def copy(self):
        return self

class DummyPackage(object):
    def __init__(self, name):
        self.__name__ = name
        self.__file__ = '/__init__.py'
        
