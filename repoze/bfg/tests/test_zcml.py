import logging

logging.basicConfig()

import unittest

from repoze.bfg import testing

class TestViewDirective(unittest.TestCase):
    def setUp(self):
        testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _callFUT(self, *arg, **kw):
        from repoze.bfg.zcml import view
        return view(*arg, **kw)

    def test_request_type_ashttpmethod(self):
        from zope.interface import Interface
        from zope.component import getSiteManager
        from repoze.bfg.interfaces import IView
        from repoze.bfg.interfaces import IRequest
        context = DummyContext()
        class IFoo(Interface):
            pass
        view = lambda *arg: None
        self._callFUT(context, 'repoze.view', IFoo, view=view,
                      request_type='GET')
        actions = context.actions

        self.assertEqual(len(actions), 1)

        action = actions[0]
        discrim = ('view', IFoo, '', None, IView, None, None, 'GET', None,
                   None, False, None, None, None)
        self.assertEqual(action['discriminator'], discrim)
        register = action['callable']
        register()
        sm = getSiteManager()
        wrapper = sm.adapters.lookup((IFoo, IRequest), IView, name='')
        request = DummyRequest()
        request.method = 'GET'
        self.assertEqual(wrapper.__predicated__(None, request), True)
        request.method = 'POST'
        self.assertEqual(wrapper.__predicated__(None, request), False)
        
    def test_request_type_asinterfacestring(self):
        from zope.component import getSiteManager
        from zope.interface import Interface
        from repoze.bfg.interfaces import IView
        from repoze.bfg.interfaces import IViewPermission
        class IFoo(Interface):
            pass
        class IRequest(Interface):
            pass
        context = DummyContext(IRequest)
        view = lambda *arg: None
        self._callFUT(context, 'repoze.view', IFoo, view=view,
                      request_type='whatever')
        actions = context.actions
        self.assertEqual(len(actions), 1)

        discrim = ('view', IFoo, '', IRequest, IView, None, None, None, None,
                   None, False, None, None, None)
        self.assertEqual(actions[0]['discriminator'], discrim)
        register = actions[0]['callable']
        register()
        sm = getSiteManager()
        regview = sm.adapters.lookup((IFoo, IRequest), IView, name='')
        self.assertEqual(view, regview)
        self.failIf(hasattr(view, '__call_permissive__'))

        perm = sm.adapters.lookup((IFoo, IRequest), IViewPermission, name='')
        self.assertEqual(perm, None)

class TestNotFoundDirective(unittest.TestCase):
    def setUp(self):
        testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _callFUT(self, context, view):
        from repoze.bfg.zcml import notfound
        return notfound(context, view)
    
    def test_it(self):
        from zope.component import getSiteManager
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
        sm = getSiteManager()
        derived_view = sm.getUtility(INotFoundView)
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
        from zope.component import getSiteManager
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
        sm = getSiteManager()
        derived_view = sm.getUtility(IForbiddenView)
        self.assertEqual(derived_view(None, None), 'OK')
        self.assertEqual(derived_view.__name__, view.__name__)

class TestViewUtility(unittest.TestCase):
    def setUp(self):
        testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _callFUT(self, context, view, attr, renderer, wrapper, iface):
        from repoze.bfg.zcml import view_utility
        return view_utility(context, view, attr, renderer, wrapper, iface)

    def test_no_view_no_renderer(self):
        from zope.configuration.exceptions import ConfigurationError
        context = DummyContext()
        self.assertRaises(ConfigurationError, self._callFUT, context,
                          None, None, None, None, None)
    
    def test_no_view_with_renderer(self):
        from zope.component import getSiteManager
        from zope.interface import Interface
        from repoze.bfg.interfaces import IRendererFactory
        sm = getSiteManager()
        def renderer(path):
            return lambda *arg: 'OK'
        sm.registerUtility(renderer, IRendererFactory, name='dummy')
        class IDummy(Interface):
            pass
        context = DummyContext()
        self._callFUT(context, None, None, 'dummy', None, IDummy)
        actions = context.actions
        self.assertEqual(len(actions), 1)
        regadapt = actions[0]
        self.assertEqual(regadapt['discriminator'], IDummy)
        register = regadapt['callable']
        register()
        derived_view = sm.getUtility(IDummy)
        request = DummyRequest()
        self.assertEqual(derived_view(None, request).body, 'OK')

    def test_template_renderer(self):
        from zope.component import getSiteManager
        from zope.interface import Interface
        from repoze.bfg.interfaces import IRendererFactory
        sm = getSiteManager()
        def renderer(path):
            return lambda *arg: 'OK'
        sm.registerUtility(renderer, IRendererFactory, name='.pt')
        class IDummy(Interface):
            pass
        context = DummyContext()
        self._callFUT(context, None, None, 'fixtures/minimal.pt', None, IDummy)
        actions = context.actions
        self.assertEqual(len(actions), 1)
        regadapt = actions[0]
        self.assertEqual(regadapt['discriminator'], IDummy)
        register = regadapt['callable']
        register()
        derived_view = sm.getUtility(IDummy)
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
        from zope.component import getUtility
        from repoze.bfg.interfaces import IAuthenticationPolicy
        context = DummyContext()
        self._callFUT(context)
        actions = context.actions
        self.assertEqual(len(actions), 1)
        regadapt = actions[0]
        self.assertEqual(regadapt['discriminator'], IAuthenticationPolicy)
        self.assertEqual(regadapt['callable'], None)
        self.assertEqual(regadapt['args'], ())
        policy = getUtility(IAuthenticationPolicy)
        self.assertEqual(policy.callback, None)
        self.assertEqual(policy.identifier_name, 'auth_tkt')
    
    def test_it(self):
        from zope.component import getUtility
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
        policy = getUtility(IAuthenticationPolicy)
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
        from zope.component import getUtility
        context = DummyContext()
        def callback(identity, request):
            """ """
        self._callFUT(context)
        actions = context.actions
        self.assertEqual(len(actions), 1)
        regadapt = actions[0]
        regadapt_discriminator = 'authentication_policy'
        self.assertEqual(regadapt['discriminator'], IAuthenticationPolicy)
        self.assertEqual(regadapt['callable'], None)
        self.assertEqual(regadapt['args'], ())
        policy = getUtility(IAuthenticationPolicy)
        self.assertEqual(policy.environ_key, 'REMOTE_USER')
        self.assertEqual(policy.callback, None)

    def test_it(self):
        from zope.component import getUtility
        from repoze.bfg.interfaces import IAuthenticationPolicy
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
        policy = getUtility(IAuthenticationPolicy)
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
        from zope.component import getUtility
        from repoze.bfg.interfaces import IAuthenticationPolicy
        context = DummyContext()
        self._callFUT(context, 'sosecret')
        actions = context.actions
        self.assertEqual(len(actions), 1)
        regadapt = actions[0]
        self.assertEqual(regadapt['discriminator'], IAuthenticationPolicy)
        self.assertEqual(regadapt['callable'], None)
        self.assertEqual(regadapt['args'], ())
        policy = getUtility(IAuthenticationPolicy)
        self.assertEqual(policy.cookie.secret, 'sosecret')
        self.assertEqual(policy.callback, None)

    def test_it_noconfigerror(self):
        from zope.component import getUtility
        from repoze.bfg.interfaces import IAuthenticationPolicy
        context = DummyContext()
        def callback(identity, request):
            """ """
        self._callFUT(context, 'sosecret', callback=callback,
                      cookie_name='repoze.bfg.auth_tkt',
                      secure=True, include_ip=True, timeout=100,
                      reissue_time=60)
        actions = context.actions
        self.assertEqual(len(actions), 1)
        regadapt = actions[0]
        self.assertEqual(regadapt['discriminator'], IAuthenticationPolicy)
        self.assertEqual(regadapt['callable'], None)
        self.assertEqual(regadapt['args'], ())
        policy = getUtility(IAuthenticationPolicy)
        self.assertEqual(policy.cookie.secret, 'sosecret')
        self.assertEqual(policy.callback, callback)

    def test_it_configerror(self):
        from zope.configuration.exceptions import ConfigurationError
        context = DummyContext()
        def callback(identity, request):
            """ """
        self.assertRaises(ConfigurationError,
                          self._callFUT,
                          context, 'sosecret', callback=callback,
                          cookie_name='repoze.bfg.auth_tkt',
                          secure=True, include_ip=True, timeout=100,
                          reissue_time=500)

class TestACLAuthorizationPolicyDirective(unittest.TestCase):
    def setUp(self):
        testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _callFUT(self, context, **kw):
        from repoze.bfg.zcml import aclauthorizationpolicy
        return aclauthorizationpolicy(context, **kw)
    
    def test_it(self):
        from zope.component import getUtility
        from repoze.bfg.authorization import ACLAuthorizationPolicy
        from repoze.bfg.interfaces import IAuthorizationPolicy
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
        policy = getUtility(IAuthorizationPolicy)
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
        from zope.component import getSiteManager
        from repoze.bfg.interfaces import IRoutesMapper
        sm = getSiteManager()
        mapper = sm.getUtility(IRoutesMapper)
        routes = mapper.get_routes()
        route = routes[0]
        self.assertEqual(len(routes), 1)
        self.assertEqual(route.name, name)
        self.assertEqual(route.path, path)
        self.assertEqual(len(routes[0].predicates), num_predicates)
        return route

    def test_with_view(self):
        from zope.component import getSiteManager
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
        sm = getSiteManager()
        request_type = sm.getUtility(IRouteRequest, 'name')
        view_discriminator = view_action['discriminator']
        discrim = ('view', None, '', request_type, IView, None, None, None,
                   'name', None, False, None, None, None)
        self.assertEqual(view_discriminator, discrim)
        wrapped = sm.adapters.lookup((Interface, request_type), IView, name='')
        self.failUnless(wrapped)

    # route predicates

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
        from zope.component import getSiteManager
        from zope.interface import implementedBy
        from repoze.bfg.static import StaticRootFactory
        from repoze.bfg.interfaces import IView
        from repoze.bfg.interfaces import IRouteRequest
        from repoze.bfg.interfaces import IRoutesMapper
        context = DummyContext()
        self._callFUT(context, 'name', 'fixtures/static')
        actions = context.actions
        self.assertEqual(len(actions), 2)

        sm = getSiteManager()

        route_action = actions[0]
        discriminator = route_action['discriminator']
        self.assertEqual(discriminator,
                         ('route', 'name', False, None, None, None, None, None))
        route_action['callable']()
        mapper = sm.getUtility(IRoutesMapper)
        routes = mapper.get_routes()
        self.assertEqual(len(routes), 1)
        self.assertEqual(routes[0].path, 'name*subpath')
        self.assertEqual(routes[0].name, 'name')

        view_action = actions[1]
        discriminator = view_action['discriminator']
        self.assertEqual(discriminator[:3], ('view', StaticRootFactory, ''))
        self.assertEqual(discriminator[4], IView)
        iface = implementedBy(StaticRootFactory)
        request_type = sm.getUtility(IRouteRequest, 'name')
        view = sm.adapters.lookup((iface, request_type), IView, name='')
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

    def test_samename(self):
        from zope.configuration.exceptions import ConfigurationError
        context = DummyContext()
        self.assertRaises(ConfigurationError, self._callFUT, context, 'a', 'a')

    def test_override_directory_with_file(self):
        from zope.configuration.exceptions import ConfigurationError
        context = DummyContext()
        self.assertRaises(ConfigurationError, self._callFUT, context,
                          'a:foo/', 'a:foo.pt')

    def test_override_file_with_directory(self):
        from zope.configuration.exceptions import ConfigurationError
        context = DummyContext()
        self.assertRaises(ConfigurationError, self._callFUT, context,
                          'a:foo.pt', 'a:foo/')

    def test_no_colons(self):
        from zope.component import getSiteManager
        from repoze.bfg.configuration import Configurator
        context = DummyContext()
        self._callFUT(context, 'a', 'b')
        actions = context.actions
        self.assertEqual(len(actions), 1)
        action = actions[0]
        sm = getSiteManager()
        self.assertEqual(action['callable'].im_func,
                         Configurator.resource.im_func)
        self.assertEqual(action['discriminator'], None)
        self.assertEqual(action['args'], ('a', 'b', None))

    def test_with_colons(self):
        from zope.component import getSiteManager
        from repoze.bfg.configuration import Configurator
        context = DummyContext()
        self._callFUT(context, 'a:foo.pt', 'b:foo.pt')
        actions = context.actions
        self.assertEqual(len(actions), 1)
        action = actions[0]
        sm = getSiteManager()
        self.assertEqual(action['callable'].im_func,
                         Configurator.resource.im_func)
        self.assertEqual(action['discriminator'], None)
        self.assertEqual(action['args'], ('a:foo.pt', 'b:foo.pt', None))

    def test_override_module_with_directory(self):
        from zope.component import getSiteManager
        from repoze.bfg.configuration import Configurator
        context = DummyContext()
        self._callFUT(context, 'a', 'b:foo/')
        actions = context.actions
        self.assertEqual(len(actions), 1)
        action = actions[0]
        sm = getSiteManager()
        self.assertEqual(action['callable'].im_func,
                         Configurator.resource.im_func)
        self.assertEqual(action['discriminator'], None)
        self.assertEqual(action['args'], ('a', 'b:foo/', None))

    def test_override_directory_with_module(self):
        from zope.component import getSiteManager
        from repoze.bfg.configuration import Configurator
        context = DummyContext()
        self._callFUT(context, 'a:foo/', 'b')
        actions = context.actions
        self.assertEqual(len(actions), 1)
        action = actions[0]
        sm = getSiteManager()
        self.assertEqual(action['callable'].im_func,
                         Configurator.resource.im_func)
        self.assertEqual(action['discriminator'], None)
        self.assertEqual(action['args'], ('a:foo/', 'b', None))

    def test_override_module_with_module(self):
        from repoze.bfg.configuration import Configurator
        from zope.component import getSiteManager
        context = DummyContext()
        self._callFUT(context, 'a', 'b')
        actions = context.actions
        self.assertEqual(len(actions), 1)
        action = actions[0]
        sm = getSiteManager()
        self.assertEqual(action['callable'].im_func,
                         Configurator.resource.im_func)
        self.assertEqual(action['discriminator'], None)
        self.assertEqual(action['args'], ('a', 'b', None))

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

    def _callFUT(self, context, package, martian):
        from repoze.bfg.zcml import scan
        return scan(context, package, martian)

    def test_it(self):
        from repoze.bfg.configuration import BFGMultiGrokker
        martian = DummyMartianModule()
        module_grokker = DummyModuleGrokker()
        dummy_module = DummyModule()
        context = DummyContext()
        self._callFUT(context, dummy_module, martian)
        context.actions[-1]['callable']()
        self.assertEqual(martian.name, 'dummy')
        multi_grokker = martian.module_grokker.multi_grokker
        self.assertEqual(multi_grokker.__class__, BFGMultiGrokker)
        self.assertEqual(martian.info, context.info)
        self.failUnless(martian.exclude_filter)

class DummyModule:
    __path__ = "foo"
    __name__ = "dummy"
    __file__ = ''

class DummyModuleGrokker:
    def __init__(self, grokker=None):
        self.multi_grokker = grokker
        
class DummyMartianModule:
    def grok_dotted_name(self, name, grokker, _info, _configurator,
                         exclude_filter=None):
        self.name = name
        self.info = _info
        self.configurator = _configurator
        self.exclude_filter = exclude_filter
        return True

    def ModuleGrokker(self, grokker=None):
        self.module_grokker = DummyModuleGrokker(grokker)
        return self.module_grokker

class DummyContext:
    def __init__(self, resolved=DummyModule):
        self.actions = []
        self.info = None
        self.resolved = resolved

    def action(self, discriminator, callable=None, args=(), kw={}, order=0):
        self.actions.append(
            {'discriminator':discriminator,
             'callable':callable,
             'args':args}
            )

    def resolve(self, dottedname):
        return self.resolved

class Dummy:
    pass

class DummyRoute:
    pass

from zope.interface import Interface
class IDummy(Interface):
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

