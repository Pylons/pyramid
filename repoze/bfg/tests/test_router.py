import unittest

from repoze.bfg.testing import cleanUp

class RouterTests(unittest.TestCase):
    def setUp(self):
        from repoze.bfg.registry import Registry
        from zope.component import getSiteManager
        self.registry = Registry()
        getSiteManager.sethook(lambda *arg: self.registry)

    def tearDown(self):
        from zope.component import getSiteManager
        getSiteManager.reset()
        cleanUp()

    def _registerLogger(self):
        from zope.component import getSiteManager
        gsm = getSiteManager()
        from repoze.bfg.interfaces import ILogger
        logger = DummyLogger()
        gsm.registerUtility(logger, ILogger, name='repoze.bfg.debug')
        return logger

    def _registerSettings(self, **kw):
        from repoze.bfg.interfaces import ISettings
        settings = {'debug_authorization':False, 'debug_notfound':False}
        settings.update(kw)
        self.registry.registerUtility(settings, ISettings)

    def _registerTraverserFactory(self, context, view_name='', subpath=None,
                                  traversed=None, virtual_root=None,
                                  virtual_root_path=None, **kw):
        from repoze.bfg.interfaces import ITraverserFactory

        if virtual_root is None:
            virtual_root = context
        if subpath is None:
            subpath = []
        if traversed is None:
            traversed = []
        if virtual_root_path is None:
            virtual_root_path = []

        class DummyTraverserFactory:
            def __init__(self, root):
                self.root = root

            def __call__(self, path):
                values = {'root':self.root,
                          'context':context,
                          'view_name':view_name,
                          'subpath':subpath,
                          'traversed':traversed,
                          'virtual_root':virtual_root,
                          'virtual_root_path':virtual_root_path}
                kw.update(values)
                return kw
            
        self.registry.registerAdapter(DummyTraverserFactory, (None,),
                                      ITraverserFactory, name='')

    def _registerView(self, app, name, *for_):
        from repoze.bfg.interfaces import IView
        self.registry.registerAdapter(app, for_, IView, name)

    def _registerEventListener(self, iface):
        L = []
        def listener(event):
            L.append(event)
        self.registry.registerHandler(listener, (iface,))
        return L

    def _registerRootFactory(self, val):
        rootfactory = DummyRootFactory(val)
        from repoze.bfg.interfaces import IRootFactory
        self.registry.registerUtility(rootfactory, IRootFactory)
        return rootfactory

    def _getTargetClass(self):
        from repoze.bfg.router import Router
        return Router

    def _makeOne(self):
        klass = self._getTargetClass()
        return klass(self.registry)

    def _makeEnviron(self, **extras):
        environ = {
            'wsgi.url_scheme':'http',
            'SERVER_NAME':'localhost',
            'SERVER_PORT':'8080',
            'REQUEST_METHOD':'GET',
            'PATH_INFO':'/',
            }
        environ.update(extras)
        return environ

    def test_root_policy(self):
        environ = self._makeEnviron()
        context = DummyContext()
        self._registerTraverserFactory(context)
        rootfactory = self._registerRootFactory('abc')
        router = self._makeOne()
        self.assertEqual(router.root_policy, rootfactory)

    def test_iforbiddenview_override(self):
        from repoze.bfg.interfaces import IForbiddenView
        def app():
            """ """
        self.registry.registerUtility(app, IForbiddenView)
        router = self._makeOne()
        self.assertEqual(router.forbidden_view, app)

    def test_iforbiddenview_nooverride(self):
        context = DummyContext()
        router = self._makeOne()
        from repoze.bfg.view import default_forbidden_view
        self.assertEqual(router.forbidden_view, default_forbidden_view)

    def test_inotfoundview_override(self):
        from repoze.bfg.interfaces import INotFoundView
        def app():
            """ """
        self.registry.registerUtility(app, INotFoundView)
        router = self._makeOne()
        self.assertEqual(router.notfound_view, app)

    def test_inotfoundview_nooverride(self):
        context = DummyContext()
        router = self._makeOne()
        from repoze.bfg.view import default_notfound_view
        self.assertEqual(router.notfound_view, default_notfound_view)

    def test_call_traverser_default(self):
        environ = self._makeEnviron()
        context = DummyContext()
        logger = self._registerLogger()
        router = self._makeOne()
        start_response = DummyStartResponse()
        result = router(environ, start_response)
        headers = start_response.headers
        self.assertEqual(len(headers), 2)
        status = start_response.status
        self.assertEqual(status, '404 Not Found')
        self.failUnless('<code>/</code>' in result[0], result)
        self.failIf('debug_notfound' in result[0])
        self.assertEqual(len(logger.messages), 0)

    def test_has_webob_adhoc_attrs(self):
        environ = self._makeEnviron()
        environ['webob.adhoc_attrs'] = {}
        context = DummyContext()
        logger = self._registerLogger()
        router = self._makeOne()
        start_response = DummyStartResponse()
        result = router(environ, start_response)
        headers = start_response.headers
        self.assertEqual(len(headers), 2)
        status = start_response.status
        self.assertEqual(status, '404 Not Found')
        self.failUnless('<code>/</code>' in result[0], result)
        self.failIf('debug_notfound' in result[0])
        self.assertEqual(len(logger.messages), 0)

    def test_call_no_view_registered_no_isettings(self):
        environ = self._makeEnviron()
        context = DummyContext()
        self._registerTraverserFactory(context)
        logger = self._registerLogger()
        router = self._makeOne()
        start_response = DummyStartResponse()
        result = router(environ, start_response)
        headers = start_response.headers
        self.assertEqual(len(headers), 2)
        status = start_response.status
        self.assertEqual(status, '404 Not Found')
        self.failUnless('<code>/</code>' in result[0], result)
        self.failIf('debug_notfound' in result[0])
        self.assertEqual(len(logger.messages), 0)

    def test_call_no_view_registered_debug_notfound_false(self):
        environ = self._makeEnviron()
        context = DummyContext()
        self._registerTraverserFactory(context)
        logger = self._registerLogger()
        self._registerSettings(debug_notfound=False)
        router = self._makeOne()
        start_response = DummyStartResponse()
        result = router(environ, start_response)
        headers = start_response.headers
        self.assertEqual(len(headers), 2)
        status = start_response.status
        self.assertEqual(status, '404 Not Found')
        self.failUnless('<code>/</code>' in result[0], result)
        self.failIf('debug_notfound' in result[0])
        self.assertEqual(len(logger.messages), 0)

    def test_call_no_view_registered_debug_notfound_true(self):
        environ = self._makeEnviron()
        context = DummyContext()
        self._registerTraverserFactory(context)
        self._registerSettings(debug_notfound=True)
        logger = self._registerLogger()
        router = self._makeOne()
        start_response = DummyStartResponse()
        result = router(environ, start_response)
        headers = start_response.headers
        self.assertEqual(len(headers), 2)
        status = start_response.status
        self.assertEqual(status, '404 Not Found')
        self.failUnless(
            "debug_notfound of url http://localhost:8080/; path_info: '/', "
            "context:" in result[0])
        self.failUnless(
            "view_name: '', subpath: []" in result[0])
        self.failUnless('http://localhost:8080' in result[0], result)
        self.assertEqual(len(logger.messages), 1)
        message = logger.messages[0]
        self.failUnless('of url http://localhost:8080' in message)
        self.failUnless("path_info: '/'" in message)
        self.failUnless('DummyContext instance at' in message)
        self.failUnless("view_name: ''" in message)
        self.failUnless("subpath: []" in message)

    def test_call_view_returns_nonresponse(self):
        context = DummyContext()
        self._registerTraverserFactory(context)
        environ = self._makeEnviron()
        view = DummyView('abc')
        self._registerView(view, '', None, None)
        router = self._makeOne()
        start_response = DummyStartResponse()
        self.assertRaises(ValueError, router, environ, start_response)

    def test_inotfoundview_returns_nonresponse(self):
        from repoze.bfg.interfaces import INotFoundView
        context = DummyContext()
        environ = self._makeEnviron()
        self._registerTraverserFactory(context)
        def app(context, request):
            """ """
        self.registry.registerUtility(app, INotFoundView)
        router = self._makeOne()
        start_response = DummyStartResponse()
        self.assertRaises(ValueError, router, environ, start_response)

    def test_call_view_registered_nonspecific_default_path(self):
        context = DummyContext()
        self._registerTraverserFactory(context)
        response = DummyResponse()
        response.app_iter = ['Hello world']
        view = DummyView(response)
        environ = self._makeEnviron()
        self._registerView(view, '', None, None)
        rootfactory = self._registerRootFactory(context)
        router = self._makeOne()
        start_response = DummyStartResponse()
        result = router(environ, start_response)
        self.assertEqual(result, ['Hello world'])
        self.assertEqual(start_response.headers, ())
        self.assertEqual(start_response.status, '200 OK')
        self.assertEqual(environ['webob.adhoc_attrs']['view_name'], '')
        self.assertEqual(environ['webob.adhoc_attrs']['subpath'], [])
        self.assertEqual(environ['webob.adhoc_attrs']['context'], context)
        self.assertEqual(environ['webob.adhoc_attrs']['root'], context)

    def test_call_view_registered_nonspecific_nondefault_path_and_subpath(self):
        context = DummyContext()
        self._registerTraverserFactory(context, view_name='foo',
                                       subpath=['bar'],
                                       traversed=['context'])
        rootfactory = self._registerRootFactory(context)
        response = DummyResponse()
        response.app_iter = ['Hello world']
        view = DummyView(response)
        environ = self._makeEnviron()
        self._registerView(view, 'foo', None, None)
        router = self._makeOne()
        start_response = DummyStartResponse()
        result = router(environ, start_response)
        self.assertEqual(result, ['Hello world'])
        self.assertEqual(start_response.headers, ())
        self.assertEqual(start_response.status, '200 OK')
        self.assertEqual(environ['webob.adhoc_attrs']['view_name'], 'foo')
        self.assertEqual(environ['webob.adhoc_attrs']['subpath'], ['bar'])
        self.assertEqual(environ['webob.adhoc_attrs']['context'], context)
        self.assertEqual(environ['webob.adhoc_attrs']['root'], context)

    def test_call_view_registered_specific_success(self):
        from zope.interface import Interface
        from zope.interface import directlyProvides
        class IContext(Interface):
            pass
        from repoze.bfg.interfaces import IRequest
        context = DummyContext()
        directlyProvides(context, IContext)
        self._registerTraverserFactory(context)
        rootfactory = self._registerRootFactory(context)
        response = DummyResponse()
        response.app_iter = ['Hello world']
        view = DummyView(response)
        environ = self._makeEnviron()
        self._registerView(view, '', IContext, IRequest)
        router = self._makeOne()
        start_response = DummyStartResponse()
        result = router(environ, start_response)
        self.assertEqual(result, ['Hello world'])
        self.assertEqual(start_response.headers, ())
        self.assertEqual(start_response.status, '200 OK')
        self.assertEqual(environ['webob.adhoc_attrs']['view_name'], '')
        self.assertEqual(environ['webob.adhoc_attrs']['subpath'], [])
        self.assertEqual(environ['webob.adhoc_attrs']['context'], context)
        self.assertEqual(environ['webob.adhoc_attrs']['root'], context)

    def test_call_view_registered_specific_fail(self):
        from zope.interface import Interface
        from zope.interface import directlyProvides
        class IContext(Interface):
            pass
        class INotContext(Interface):
            pass
        from repoze.bfg.interfaces import IRequest
        context = DummyContext()
        directlyProvides(context, INotContext)
        self._registerTraverserFactory(context, subpath=[''])
        response = DummyResponse()
        view = DummyView(response)
        environ = self._makeEnviron()
        self._registerView(view, '', IContext, IRequest)
        router = self._makeOne()
        start_response = DummyStartResponse()
        result = router(environ, start_response)
        self.assertEqual(start_response.status, '404 Not Found')
        self.failUnless('404' in result[0])

    def test_call_view_raises_unauthorized(self):
        from zope.interface import Interface
        from zope.interface import directlyProvides
        class IContext(Interface):
            pass
        from repoze.bfg.interfaces import IRequest
        context = DummyContext()
        directlyProvides(context, IContext)
        self._registerTraverserFactory(context, subpath=[''])
        response = DummyResponse()
        view = DummyView(response, raise_unauthorized=True)
        environ = self._makeEnviron()
        self._registerView(view, '', IContext, IRequest)
        router = self._makeOne()
        start_response = DummyStartResponse()
        response = router(environ, start_response)
        self.assertEqual(start_response.status, '401 Unauthorized')
        self.assertEqual(environ['repoze.bfg.message'], 'unauthorized')

    def test_call_view_raises_notfound(self):
        from zope.interface import Interface
        from zope.interface import directlyProvides
        class IContext(Interface):
            pass
        from repoze.bfg.interfaces import IRequest
        context = DummyContext()
        directlyProvides(context, IContext)
        self._registerTraverserFactory(context, subpath=[''])
        response = DummyResponse()
        view = DummyView(response, raise_notfound=True)
        environ = self._makeEnviron()
        self._registerView(view, '', IContext, IRequest)
        router = self._makeOne()
        start_response = DummyStartResponse()
        response = router(environ, start_response)
        self.assertEqual(start_response.status, '404 Not Found')
        self.assertEqual(environ['repoze.bfg.message'], 'notfound')

    def test_call_eventsends(self):
        context = DummyContext()
        self._registerTraverserFactory(context)
        response = DummyResponse()
        response.app_iter = ['Hello world']
        view = DummyView(response)
        environ = self._makeEnviron()
        self._registerView(view, '', None, None)
        from repoze.bfg.interfaces import INewRequest
        from repoze.bfg.interfaces import INewResponse
        request_events = self._registerEventListener(INewRequest)
        response_events = self._registerEventListener(INewResponse)
        router = self._makeOne()
        start_response = DummyStartResponse()
        result = router(environ, start_response)
        self.assertEqual(len(request_events), 1)
        self.assertEqual(request_events[0].request.environ, environ)
        self.assertEqual(len(response_events), 1)
        self.assertEqual(response_events[0].response, response)

    def test_call_pushes_and_pops_threadlocal_manager(self):
        context = DummyContext()
        self._registerTraverserFactory(context)
        response = DummyResponse()
        response.app_iter = ['Hello world']
        view = DummyView(response)
        environ = self._makeEnviron()
        self._registerView(view, '', None, None)
        router = self._makeOne()
        start_response = DummyStartResponse()
        router.threadlocal_manager = DummyThreadLocalManager()
        result = router(environ, start_response)
        self.assertEqual(len(router.threadlocal_manager.pushed), 1)
        self.assertEqual(len(router.threadlocal_manager.popped), 1)

class MakeAppTests(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()
        
    def _callFUT(self, *arg, **kw):
        from repoze.bfg.router import make_app
        return make_app(*arg, **kw)

    def test_fixtureapp_default_filename_withpackage(self):
        manager = DummyRegistryManager()
        from repoze.bfg.tests import fixtureapp
        rootfactory = DummyRootFactory(None)
        app = self._callFUT(rootfactory, fixtureapp, manager=manager)
        self.assertEqual(app.registry.__name__, 'repoze.bfg.tests.fixtureapp')
        from repoze.bfg.tests.fixtureapp.models import IFixture
        self.failUnless(app.registry.queryUtility(IFixture)) # only in c.zcml

    def test_fixtureapp_explicit_filename(self):
        manager = DummyRegistryManager()
        from repoze.bfg.tests import fixtureapp
        rootfactory = DummyRootFactory(None)
        app = self._callFUT(rootfactory, fixtureapp, filename='another.zcml',
                            manager=manager)
        self.assertEqual(app.registry.__name__, 'repoze.bfg.tests.fixtureapp')
        from repoze.bfg.tests.fixtureapp.models import IFixture
        self.failIf(app.registry.queryUtility(IFixture)) # only in c.zcml

    def test_fixtureapp_explicit_filename_in_options(self):
        import os
        manager = DummyRegistryManager()
        rootfactory = DummyRootFactory(None)
        from repoze.bfg.tests import fixtureapp
        zcmlfile = os.path.join(os.path.dirname(fixtureapp.__file__),
                                'another.zcml')
        app = self._callFUT(rootfactory, fixtureapp, filename='configure.zcml',
                            options={'configure_zcml':zcmlfile},
                            manager=manager)
        self.assertEqual(app.registry.__name__, 'repoze.bfg.tests.fixtureapp')
        from repoze.bfg.tests.fixtureapp.models import IFixture
        self.failIf(app.registry.queryUtility(IFixture)) # only in c.zcml

    def test_fixtureapp_explicit_specification_in_options(self):
        manager = DummyRegistryManager()
        rootfactory = DummyRootFactory(None)
        from repoze.bfg.tests import fixtureapp
        zcmlfile = 'repoze.bfg.tests.fixtureapp.subpackage:yetanother.zcml'
        app = self._callFUT(rootfactory, fixtureapp, filename='configure.zcml',
                            options={'configure_zcml':zcmlfile},
                            manager=manager)
        self.assertEqual(app.registry.__name__,
                         'repoze.bfg.tests.fixtureapp.subpackage')
        from repoze.bfg.tests.fixtureapp.models import IFixture
        self.failIf(app.registry.queryUtility(IFixture)) # only in c.zcml

    def test_fixtureapp_filename_hascolon_isabs(self):
        manager = DummyRegistryManager()
        rootfactory = DummyRootFactory(None)
        from repoze.bfg.tests import fixtureapp
        zcmlfile = 'repoze.bfg.tests.fixtureapp.subpackage:yetanother.zcml'
        class Dummy:
            def isabs(self, name):
                return True
        os = Dummy()
        os.path = Dummy()
        self.assertRaises(IOError, self._callFUT,
                          rootfactory,
                          fixtureapp,
                          filename='configure.zcml',
                          options={'configure_zcml':zcmlfile},
                          manager=manager,
                          os=os)
        
    def test_event(self):
        manager = DummyRegistryManager()
        def subscriber(event):
            event.app.created = True        
        from repoze.bfg.interfaces import IWSGIApplicationCreatedEvent
        from zope.component import getGlobalSiteManager
        getGlobalSiteManager().registerHandler(
            subscriber,
            (IWSGIApplicationCreatedEvent,)
            )
        from repoze.bfg.tests import fixtureapp
        rootfactory = DummyRootFactory(None)
        app = self._callFUT(rootfactory, fixtureapp, manager=manager)
        assert app.created is True

    def test_custom_settings(self):
        manager = DummyRegistryManager()
        options= {'mysetting':True}
        from repoze.bfg.tests import fixtureapp
        rootfactory = DummyRootFactory(None)
        app = self._callFUT(rootfactory, fixtureapp, options=options,
                            manager=manager)
        from repoze.bfg.interfaces import ISettings
        settings = app.registry.getUtility(ISettings)
        self.assertEqual(settings.reload_templates, False)
        self.assertEqual(settings.debug_authorization, False)
        self.assertEqual(settings.mysetting, True)

    def test_registrations(self):
        manager = DummyRegistryManager()
        options= {'reload_templates':True,
                  'debug_authorization':True}
        from repoze.bfg.tests import fixtureapp
        rootfactory = DummyRootFactory(None)
        app = self._callFUT(rootfactory, fixtureapp, options=options,
                            manager=manager)
        from repoze.bfg.interfaces import ISettings
        from repoze.bfg.interfaces import ILogger
        from repoze.bfg.interfaces import IRootFactory
        settings = app.registry.getUtility(ISettings)
        logger = app.registry.getUtility(ILogger, name='repoze.bfg.debug')
        rootfactory = app.registry.getUtility(IRootFactory)
        self.assertEqual(logger.name, 'repoze.bfg.debug')
        self.assertEqual(settings.reload_templates, True)
        self.assertEqual(settings.debug_authorization, True)
        self.assertEqual(rootfactory, rootfactory)
        self.failUnless(manager.pushed and manager.popped)

    def test_routes_in_config_with_rootfactory(self):
        manager = DummyRegistryManager()
        options= {'reload_templates':True,
                  'debug_authorization':True}
        from repoze.bfg.urldispatch import RoutesRootFactory
        from repoze.bfg.tests import routesapp
        rootfactory = DummyRootFactory(None)
        app = self._callFUT(rootfactory, routesapp, options=options,
                            manager=manager)
        from repoze.bfg.interfaces import ISettings
        from repoze.bfg.interfaces import ILogger
        from repoze.bfg.interfaces import IRootFactory
        settings = app.registry.getUtility(ISettings)
        logger = app.registry.getUtility(ILogger, name='repoze.bfg.debug')
        effective_rootfactory = app.registry.getUtility(IRootFactory)
        self.assertEqual(logger.name, 'repoze.bfg.debug')
        self.assertEqual(settings.reload_templates, True)
        self.assertEqual(settings.debug_authorization, True)
        self.failUnless(isinstance(effective_rootfactory, RoutesRootFactory))
        self.assertEqual(effective_rootfactory.default_root_factory,
                         rootfactory)
        self.failUnless(manager.pushed and manager.popped)

    def test_routes_in_config_no_rootfactory(self):
        manager = DummyRegistryManager()
        options= {'reload_templates':True,
                  'debug_authorization':True}
        from repoze.bfg.urldispatch import RoutesRootFactory
        from repoze.bfg.router import DefaultRootFactory
        from repoze.bfg.tests import routesapp
        app = self._callFUT(None, routesapp, options=options,
                            manager=manager)
        from repoze.bfg.interfaces import ISettings
        from repoze.bfg.interfaces import ILogger
        from repoze.bfg.interfaces import IRootFactory
        settings = app.registry.getUtility(ISettings)
        logger = app.registry.getUtility(ILogger, name='repoze.bfg.debug')
        rootfactory = app.registry.getUtility(IRootFactory)
        self.assertEqual(logger.name, 'repoze.bfg.debug')
        self.assertEqual(settings.reload_templates, True)
        self.assertEqual(settings.debug_authorization, True)
        self.failUnless(isinstance(rootfactory, RoutesRootFactory))
        self.assertEqual(rootfactory.default_root_factory, DefaultRootFactory)
        self.failUnless(manager.pushed and manager.popped)
        
    def test_no_routes_in_config_no_rootfactory(self):
        manager = DummyRegistryManager()
        from repoze.bfg.router import DefaultRootFactory
        from repoze.bfg.interfaces import IRootFactory
        options= {'reload_templates':True,
                  'debug_authorization':True}
        from repoze.bfg.tests import fixtureapp
        app = self._callFUT(None, fixtureapp, options=options,
                            manager=manager)
        rootfactory = app.registry.getUtility(IRootFactory)
        self.assertEqual(rootfactory, DefaultRootFactory)

    def test_authorization_policy_no_authentication_policy(self):
        manager = DummyRegistryManager()
        from repoze.bfg.interfaces import IAuthorizationPolicy
        authzpolicy = DummyContext()
        from repoze.bfg.tests import routesapp
        logger = DummyLogger()
        app = self._callFUT(None, routesapp, authorization_policy=authzpolicy,
                            debug_logger=logger, manager=manager)
        self.failIf(app.registry.queryUtility(IAuthorizationPolicy))
        self.assertEqual(logger.messages, [])
        
    def test_authentication_policy_no_authorization_policy(self):
        manager = DummyRegistryManager()
        from repoze.bfg.interfaces import IAuthorizationPolicy
        from repoze.bfg.interfaces import IAuthenticationPolicy
        from repoze.bfg.authorization import ACLAuthorizationPolicy
        authnpolicy = DummyContext()
        from repoze.bfg.tests import routesapp
        logger = DummyLogger()
        app = self._callFUT(None, routesapp, authentication_policy=authnpolicy,
                            debug_logger=logger, manager=manager)
        self.assertEqual(app.registry.getUtility(IAuthenticationPolicy),
                         authnpolicy)
        self.assertEqual(
            app.registry.getUtility(IAuthorizationPolicy).__class__,
            ACLAuthorizationPolicy)
        self.assertEqual(len(logger.messages), 1) # deprecation warning
                        
    def test_authentication_policy_and_authorization_policy(self):
        manager = DummyRegistryManager()
        from repoze.bfg.interfaces import IAuthorizationPolicy
        from repoze.bfg.interfaces import IAuthenticationPolicy
        authnpolicy = DummyContext()
        authzpolicy = DummyContext()
        from repoze.bfg.tests import routesapp
        logger = DummyLogger()
        app = self._callFUT(None, routesapp, authentication_policy=authnpolicy,
                            authorization_policy = authzpolicy,
                            debug_logger=logger, manager=manager)
        self.assertEqual(app.registry.getUtility(IAuthenticationPolicy),
                         authnpolicy)
        self.assertEqual(app.registry.getUtility(IAuthorizationPolicy),
                         authzpolicy)
        self.assertEqual(len(logger.messages), 1) # deprecation warning

class TestDefaultRootFactory(unittest.TestCase):
    def _getTargetClass(self):
        from repoze.bfg.router import DefaultRootFactory
        return DefaultRootFactory

    def _makeOne(self, environ):
        return self._getTargetClass()(environ)

    def test_no_matchdict(self):
        environ = {}
        root = self._makeOne(environ)
        self.assertEqual(root.__parent__, None)
        self.assertEqual(root.__name__, None)

    def test_matchdict(self):
        environ = {'bfg.routes.matchdict':{'a':1, 'b':2}}
        root = self._makeOne(environ)
        self.assertEqual(root.a, 1)
        self.assertEqual(root.b, 2)


class DummyRegistryManager:
    def push(self, registry):
        self.pushed = True

    def pop(self):
        self.popped = True

class DummyContext:
    pass

class DummyView:
    def __init__(self, response, raise_unauthorized=False,
                 raise_notfound=False):
        self.response = response
        self.raise_unauthorized = raise_unauthorized
        self.raise_notfound = raise_notfound

    def __call__(self, context, request):
        if self.raise_unauthorized:
            from repoze.bfg.exceptions import Forbidden
            raise Forbidden('unauthorized')
        if self.raise_notfound:
            from repoze.bfg.exceptions import NotFound
            raise NotFound('notfound')
        return self.response

class DummyRootFactory:
    def __init__(self, root):
        self.root = root

    def __call__(self, environ):
        return self.root

class DummyStartResponse:
    status = ()
    headers = ()
    def __call__(self, status, headers):
        self.status = status
        self.headers = headers
        
class DummyResponse:
    status = '200 OK'
    headerlist = ()
    app_iter = ()
    
class DummyThreadLocalManager:
    def __init__(self):
        self.pushed = []
        self.popped = []

    def push(self, val):
        self.pushed.append(val)

    def pop(self):
        self.popped.append(True)
    
class DummyAuthenticationPolicy:
    pass

class DummyLogger:
    def __init__(self):
        self.messages = []
    def info(self, msg):
        self.messages.append(msg)
    warn = info
    debug = info

