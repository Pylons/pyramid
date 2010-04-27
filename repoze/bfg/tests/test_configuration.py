import unittest

from repoze.bfg import testing

class ConfiguratorTests(unittest.TestCase):
    def _makeOne(self, *arg, **kw):
        from repoze.bfg.configuration import Configurator
        return Configurator(*arg, **kw)

    def _registerRenderer(self, config, name='.txt'):
        from repoze.bfg.interfaces import IRendererFactory
        from repoze.bfg.interfaces import ITemplateRenderer
        from zope.interface import implements
        class Renderer:
            implements(ITemplateRenderer)
            def __init__(self, path):
                self.__class__.path = path
            def __call__(self, *arg):
                return 'Hello!'
        config.registry.registerUtility(Renderer, IRendererFactory, name=name)
        return Renderer

    def _getViewCallable(self, config, ctx_iface=None, request_iface=None,
                         name='', exception_view=False):
        from zope.interface import Interface
        from repoze.bfg.interfaces import IRequest
        from repoze.bfg.interfaces import IView
        from repoze.bfg.interfaces import IViewClassifier
        from repoze.bfg.interfaces import IExceptionViewClassifier
        if exception_view:
            classifier = IExceptionViewClassifier
        else:
            classifier = IViewClassifier
        if ctx_iface is None:
            ctx_iface = Interface
        if request_iface is None:
            request_iface = IRequest
        return config.registry.adapters.lookup(
            (classifier, request_iface, ctx_iface), IView, name=name,
            default=None)

    def _getRouteRequestIface(self, config, name):
        from repoze.bfg.interfaces import IRouteRequest
        iface = config.registry.getUtility(IRouteRequest, name)
        return iface

    def _assertNotFound(self, wrapper, *arg):
        from repoze.bfg.exceptions import NotFound
        self.assertRaises(NotFound, wrapper, *arg)

    def _registerEventListener(self, config, event_iface=None):
        if event_iface is None: # pragma: no cover
            from zope.interface import Interface
            event_iface = Interface
        L = []
        def subscriber(*event):
            L.extend(event)
        config.registry.registerHandler(subscriber, (event_iface,))
        return L

    def _registerLogger(self, config):
        from repoze.bfg.interfaces import IDebugLogger
        logger = DummyLogger()
        config.registry.registerUtility(logger, IDebugLogger)
        return logger

    def _makeRequest(self, config):
        request = DummyRequest()
        request.registry = config.registry
        return request

    def _registerSecurityPolicy(self, config, permissive):
        from repoze.bfg.interfaces import IAuthenticationPolicy
        from repoze.bfg.interfaces import IAuthorizationPolicy
        policy = DummySecurityPolicy(permissive)
        config.registry.registerUtility(policy, IAuthenticationPolicy)
        config.registry.registerUtility(policy, IAuthorizationPolicy)

    def _registerSettings(self, config, **settings):
        from repoze.bfg.interfaces import ISettings
        config.registry.registerUtility(settings, ISettings)

    def test_ctor_no_registry(self):
        import sys
        from repoze.bfg.interfaces import ISettings
        from repoze.bfg.configuration import Configurator
        from repoze.bfg.interfaces import IRendererFactory
        config = Configurator()
        this_pkg = sys.modules['repoze.bfg.tests']
        self.failUnless(config.registry.getUtility(ISettings))
        self.assertEqual(config.package, this_pkg)
        self.failUnless(config.registry.getUtility(IRendererFactory, 'json'))
        self.failUnless(config.registry.getUtility(IRendererFactory, 'string'))
        self.failUnless(config.registry.getUtility(IRendererFactory, '.pt'))
        self.failUnless(config.registry.getUtility(IRendererFactory, '.txt'))

    def test_begin(self):
        from repoze.bfg.configuration import Configurator
        config = Configurator()
        manager = DummyThreadLocalManager()
        config.manager = manager
        config.begin()
        self.assertEqual(manager.pushed,
                         {'registry':config.registry, 'request':None})
        self.assertEqual(manager.popped, False)

    def test_begin_with_request(self):
        from repoze.bfg.configuration import Configurator
        config = Configurator()
        request = object()
        manager = DummyThreadLocalManager()
        config.manager = manager
        config.begin(request=request)
        self.assertEqual(manager.pushed,
                         {'registry':config.registry, 'request':request})
        self.assertEqual(manager.popped, False)

    def test_end(self):
        from repoze.bfg.configuration import Configurator
        config = Configurator()
        manager = DummyThreadLocalManager()
        config.manager = manager
        config.end()
        self.assertEqual(manager.pushed, None)
        self.assertEqual(manager.popped, True)

    def test_ctor_with_package_registry(self):
        import sys
        from repoze.bfg.configuration import Configurator
        bfg_pkg = sys.modules['repoze.bfg']
        config = Configurator(package=bfg_pkg)
        self.assertEqual(config.package, bfg_pkg)

    def test_ctor_noreg_custom_settings(self):
        from repoze.bfg.interfaces import ISettings
        settings = {'reload_templates':True,
                    'mysetting':True}
        config = self._makeOne(settings=settings)
        settings = config.registry.getUtility(ISettings)
        self.assertEqual(settings['reload_templates'], True)
        self.assertEqual(settings['debug_authorization'], False)
        self.assertEqual(settings['mysetting'], True)

    def test_ctor_noreg_debug_logger_None_default(self):
        from repoze.bfg.interfaces import IDebugLogger
        config = self._makeOne()
        logger = config.registry.getUtility(IDebugLogger)
        self.assertEqual(logger.name, 'repoze.bfg.debug')

    def test_ctor_noreg_debug_logger_non_None(self):
        from repoze.bfg.interfaces import IDebugLogger
        logger = object()
        config = self._makeOne(debug_logger=logger)
        result = config.registry.getUtility(IDebugLogger)
        self.assertEqual(logger, result)

    def test_ctor_authentication_policy(self):
        from repoze.bfg.interfaces import IAuthenticationPolicy
        policy = object()
        config = self._makeOne(authentication_policy=policy)
        result = config.registry.getUtility(IAuthenticationPolicy)
        self.assertEqual(policy, result)

    def test_ctor_authorization_policy_only(self):
        from repoze.bfg.exceptions import ConfigurationError
        policy = object()
        self.assertRaises(ConfigurationError,
                          self._makeOne, authorization_policy=policy)

    def test_ctor_no_root_factory(self):
        from repoze.bfg.interfaces import IRootFactory
        config = self._makeOne()
        self.failUnless(config.registry.getUtility(IRootFactory))

    def test_ctor_alternate_renderers(self):
        from repoze.bfg.interfaces import IRendererFactory
        renderer = object()
        config = self._makeOne(renderers=[('yeah', renderer)])
        self.assertEqual(config.registry.getUtility(IRendererFactory, 'yeah'),
                         renderer)

    def test_setup_registry_fixed(self):
        class DummyRegistry(object):
            def subscribers(self, events, name):
                self.events = events
                return events
            def registerUtility(self, *arg, **kw):
                pass
        reg = DummyRegistry()
        config = self._makeOne(reg)
        config.add_view = lambda *arg, **kw: False
        config.setup_registry()
        self.assertEqual(reg.has_listeners, True)
        self.assertEqual(reg.notify(1), None)
        self.assertEqual(reg.events, (1,))

    def test_setup_registry_registers_default_exception_views(self):
        from repoze.bfg.exceptions import NotFound
        from repoze.bfg.exceptions import Forbidden
        from repoze.bfg.view import default_notfound_view
        from repoze.bfg.view import default_forbidden_view
        class DummyRegistry(object):
            def registerUtility(self, *arg, **kw):
                pass
        reg = DummyRegistry()
        config = self._makeOne(reg)
        views = []
        config.add_view = lambda *arg, **kw: views.append((arg, kw))
        config.setup_registry()
        self.assertEqual(views[0], ((default_notfound_view,),
                                    {'context':NotFound}))
        self.assertEqual(views[1], ((default_forbidden_view,),
                                    {'context':Forbidden}))

    def test_setup_registry_custom_settings(self):
        from repoze.bfg.registry import Registry
        from repoze.bfg.interfaces import ISettings
        settings = {'reload_templates':True,
                    'mysetting':True}
        reg = Registry()
        config = self._makeOne(reg)
        config.setup_registry(settings=settings)
        settings = reg.getUtility(ISettings)
        self.assertEqual(settings['reload_templates'], True)
        self.assertEqual(settings['debug_authorization'], False)
        self.assertEqual(settings['mysetting'], True)

    def test_setup_registry_debug_logger_None_default(self):
        from repoze.bfg.registry import Registry
        from repoze.bfg.interfaces import IDebugLogger
        reg = Registry()
        config = self._makeOne(reg)
        config.setup_registry()
        logger = reg.getUtility(IDebugLogger)
        self.assertEqual(logger.name, 'repoze.bfg.debug')

    def test_setup_registry_debug_logger_non_None(self):
        from repoze.bfg.registry import Registry
        from repoze.bfg.interfaces import IDebugLogger
        logger = object()
        reg = Registry()
        config = self._makeOne(reg)
        config.setup_registry(debug_logger=logger)
        result = reg.getUtility(IDebugLogger)
        self.assertEqual(logger, result)

    def test_setup_registry_authentication_policy(self):
        from repoze.bfg.registry import Registry
        from repoze.bfg.interfaces import IAuthenticationPolicy
        policy = object()
        reg = Registry()
        config = self._makeOne(reg)
        config.setup_registry(authentication_policy=policy)
        result = reg.getUtility(IAuthenticationPolicy)
        self.assertEqual(policy, result)

    def test_setup_registry_authorization_policy_only(self):
        from repoze.bfg.registry import Registry
        from repoze.bfg.exceptions import ConfigurationError
        policy = object()
        reg = Registry()
        config = self._makeOne(reg)
        config = self.assertRaises(ConfigurationError,
                                   config.setup_registry,
                                   authorization_policy=policy)

    def test_setup_registry_default_root_factory(self):
        from repoze.bfg.registry import Registry
        from repoze.bfg.interfaces import IRootFactory
        reg = Registry()
        config = self._makeOne(reg)
        config.setup_registry()
        self.failUnless(reg.getUtility(IRootFactory))

    def test_setup_registry_locale_negotiator(self):
        from repoze.bfg.registry import Registry
        from repoze.bfg.interfaces import ILocaleNegotiator
        reg = Registry()
        config = self._makeOne(reg)
        config.setup_registry(locale_negotiator='abc')
        utility = reg.getUtility(ILocaleNegotiator)
        self.assertEqual(utility, 'abc')

    def test_setup_registry_alternate_renderers(self):
        from repoze.bfg.registry import Registry
        from repoze.bfg.interfaces import IRendererFactory
        renderer = object()
        reg = Registry()
        config = self._makeOne(reg)
        config.setup_registry(renderers=[('yeah', renderer)])
        self.assertEqual(reg.getUtility(IRendererFactory, 'yeah'),
                         renderer)

    def test_add_settings_settings_already_registered(self):
        from repoze.bfg.registry import Registry
        from repoze.bfg.interfaces import ISettings
        reg = Registry()
        config = self._makeOne(reg)
        config._set_settings({'a':1})
        config.add_settings({'b':2})
        settings = reg.getUtility(ISettings)
        self.assertEqual(settings['a'], 1)
        self.assertEqual(settings['b'], 2)

    def test_add_settings_settings_not_yet_registered(self):
        from repoze.bfg.registry import Registry
        from repoze.bfg.interfaces import ISettings
        reg = Registry()
        config = self._makeOne(reg)
        config.add_settings({'a':1})
        settings = reg.getUtility(ISettings)
        self.assertEqual(settings['a'], 1)

    def test_add_subscriber_defaults(self):
        from zope.interface import implements
        from zope.interface import Interface
        class IEvent(Interface):
            pass
        class Event:
            implements(IEvent)
        L = []
        def subscriber(event):
            L.append(event)
        config = self._makeOne()
        config.add_subscriber(subscriber)
        event = Event()
        config.registry.notify(event)
        self.assertEqual(len(L), 1)
        self.assertEqual(L[0], event)
        config.registry.notify(object())
        self.assertEqual(len(L), 2)

    def test_add_subscriber_iface_specified(self):
        from zope.interface import implements
        from zope.interface import Interface
        class IEvent(Interface):
            pass
        class Event:
            implements(IEvent)
        L = []
        def subscriber(event):
            L.append(event)
        config = self._makeOne()
        config.add_subscriber(subscriber, IEvent)
        event = Event()
        config.registry.notify(event)
        self.assertEqual(len(L), 1)
        self.assertEqual(L[0], event)
        config.registry.notify(object())
        self.assertEqual(len(L), 1)

    def test_add_object_event_subscriber(self):
        from zope.interface import implements
        from zope.interface import Interface
        class IEvent(Interface):
            pass
        class Event:
            object = 'foo'
            implements(IEvent)
        event = Event()
        L = []
        def subscriber(object, event):
            L.append(event)
        config = self._makeOne()
        config.add_subscriber(subscriber, (Interface, IEvent))
        config.registry.subscribers((event.object, event), None)
        self.assertEqual(len(L), 1)
        self.assertEqual(L[0], event)
        config.registry.subscribers((event.object, IDummy), None)
        self.assertEqual(len(L), 1)
        
    def test_make_wsgi_app(self):
        from repoze.bfg.router import Router
        from repoze.bfg.interfaces import IWSGIApplicationCreatedEvent
        manager = DummyThreadLocalManager()
        config = self._makeOne()
        subscriber = self._registerEventListener(config,
                                                 IWSGIApplicationCreatedEvent)
        config.manager = manager
        app = config.make_wsgi_app()
        self.assertEqual(app.__class__, Router)
        self.assertEqual(manager.pushed['registry'], config.registry)
        self.assertEqual(manager.pushed['request'], None)
        self.failUnless(manager.popped)
        self.assertEqual(len(subscriber), 1)
        self.failUnless(IWSGIApplicationCreatedEvent.providedBy(subscriber[0]))

    def test_load_zcml_default(self):
        import repoze.bfg.tests.fixtureapp
        config = self._makeOne(package=repoze.bfg.tests.fixtureapp)
        registry = config.load_zcml()
        from repoze.bfg.tests.fixtureapp.models import IFixture
        self.failUnless(registry.queryUtility(IFixture)) # only in c.zcml

    def test_load_zcml_routesapp(self):
        from repoze.bfg.interfaces import IRoutesMapper
        config = self._makeOne()
        config.load_zcml('repoze.bfg.tests.routesapp:configure.zcml')
        self.failUnless(config.registry.getUtility(IRoutesMapper))

    def test_load_zcml_fixtureapp(self):
        from repoze.bfg.tests.fixtureapp.models import IFixture
        config = self._makeOne()
        config.load_zcml('repoze.bfg.tests.fixtureapp:configure.zcml')
        self.failUnless(config.registry.queryUtility(IFixture)) # only in c.zcml

    def test_load_zcml_as_relative_filename(self):
        import repoze.bfg.tests.fixtureapp
        config = self._makeOne(package=repoze.bfg.tests.fixtureapp)
        registry = config.load_zcml('configure.zcml')
        from repoze.bfg.tests.fixtureapp.models import IFixture
        self.failUnless(registry.queryUtility(IFixture)) # only in c.zcml

    def test_load_zcml_as_absolute_filename(self):
        import os
        import repoze.bfg.tests.fixtureapp
        config = self._makeOne(package=repoze.bfg.tests.fixtureapp)
        dn = os.path.dirname(repoze.bfg.tests.fixtureapp.__file__)
        c_z = os.path.join(dn, 'configure.zcml')
        registry = config.load_zcml(c_z)
        from repoze.bfg.tests.fixtureapp.models import IFixture
        self.failUnless(registry.queryUtility(IFixture)) # only in c.zcml

    def test_load_zcml_lock_and_unlock(self):
        config = self._makeOne()
        dummylock = DummyLock()
        config.load_zcml(
            'repoze.bfg.tests.fixtureapp:configure.zcml',
            lock=dummylock)
        self.assertEqual(dummylock.acquired, True)
        self.assertEqual(dummylock.released, True)

    def test_add_view_view_callable_None_no_renderer(self):
        from repoze.bfg.exceptions import ConfigurationError
        config = self._makeOne()
        self.assertRaises(ConfigurationError, config.add_view)

    def test_add_view_with_request_type_and_route_name(self):
        from repoze.bfg.exceptions import ConfigurationError
        config = self._makeOne()
        view = lambda *arg: 'OK'
        self.assertRaises(ConfigurationError, config.add_view, view, '', None,
                          None, True, True)

    def test_add_view_with_request_type_string(self):
        view = lambda *arg: 'OK'
        config = self._makeOne()
        config.add_view(view=view, request_type='GET')
        wrapper = self._getViewCallable(config)
        request = DummyRequest()
        request.method = 'POST'
        self._assertNotFound(wrapper, None, request)
        request = DummyRequest()
        request.method = 'GET'
        result = wrapper(None, request)
        self.assertEqual(result, 'OK')

    def test_add_view_view_callable_None_with_renderer(self):
        config = self._makeOne()
        self._registerRenderer(config, name='dummy')
        config.add_view(renderer='dummy')
        view = self._getViewCallable(config)
        self.failUnless('Hello!' in view(None, None).body)

    def test_add_view_wrapped_view_is_decorated(self):
        def view(request): # request-only wrapper
            """ """
        config = self._makeOne()
        config.add_view(view=view)
        wrapper = self._getViewCallable(config)
        self.assertEqual(wrapper.__module__, view.__module__)
        self.assertEqual(wrapper.__name__, view.__name__)
        self.assertEqual(wrapper.__doc__, view.__doc__)

    def test_add_view_with_function_callable(self):
        view = lambda *arg: 'OK'
        config = self._makeOne()
        config.add_view(view=view)
        wrapper = self._getViewCallable(config)
        result = wrapper(None, None)
        self.assertEqual(result, 'OK')

    def test_add_view_with_function_callable_requestonly(self):
        def view(request):
            return 'OK'
        config = self._makeOne()
        config.add_view(view=view)
        wrapper = self._getViewCallable(config)
        result = wrapper(None, None)
        self.assertEqual(result, 'OK')

    def test_add_view_as_instance(self):
        class AView:
            def __call__(self, context, request):
                """ """
                return 'OK'
        view = AView()
        config = self._makeOne()
        config.add_view(view=view)
        wrapper = self._getViewCallable(config)
        result = wrapper(None, None)
        self.assertEqual(result, 'OK')

    def test_add_view_as_instance_requestonly(self):
        class AView:
            def __call__(self, request):
                """ """
                return 'OK'
        view = AView()
        config = self._makeOne()
        config.add_view(view=view)
        wrapper = self._getViewCallable(config)
        result = wrapper(None, None)
        self.assertEqual(result, 'OK')

    def test_add_view_as_oldstyle_class(self):
        class view:
            def __init__(self, context, request):
                self.context = context
                self.request = request

            def __call__(self):
                return 'OK'
        config = self._makeOne()
        config.add_view(view=view)
        wrapper = self._getViewCallable(config)
        result = wrapper(None, None)
        self.assertEqual(result, 'OK')

    def test_add_view_as_oldstyle_class_requestonly(self):
        class view:
            def __init__(self, request):
                self.request = request

            def __call__(self):
                return 'OK'
        config = self._makeOne()
        config.add_view(view=view)
        wrapper = self._getViewCallable(config)
        result = wrapper(None, None)
        self.assertEqual(result, 'OK')

    def test_add_view_context_as_class(self):
        from zope.interface import implementedBy
        view = lambda *arg: 'OK'
        class Foo:
            pass
        config = self._makeOne()
        config.add_view(context=Foo, view=view)
        foo = implementedBy(Foo)
        wrapper = self._getViewCallable(config, foo)
        self.assertEqual(wrapper, view)

    def test_add_view_context_as_iface(self):
        view = lambda *arg: 'OK'
        config = self._makeOne()
        config.add_view(context=IDummy, view=view)
        wrapper = self._getViewCallable(config, IDummy)
        self.assertEqual(wrapper, view)

    def test_add_view_for_as_class(self):
        # ``for_`` is older spelling for ``context``
        from zope.interface import implementedBy
        view = lambda *arg: 'OK'
        class Foo:
            pass
        config = self._makeOne()
        config.add_view(for_=Foo, view=view)
        foo = implementedBy(Foo)
        wrapper = self._getViewCallable(config, foo)
        self.assertEqual(wrapper, view)

    def test_add_view_for_as_iface(self):
        # ``for_`` is older spelling for ``context``
        view = lambda *arg: 'OK'
        config = self._makeOne()
        config.add_view(for_=IDummy, view=view)
        wrapper = self._getViewCallable(config, IDummy)
        self.assertEqual(wrapper, view)

    def test_add_view_context_trumps_for(self):
        # ``for_`` is older spelling for ``context``
        view = lambda *arg: 'OK'
        config = self._makeOne()
        class Foo:
            pass
        config.add_view(context=IDummy, for_=Foo, view=view)
        wrapper = self._getViewCallable(config, IDummy)
        self.assertEqual(wrapper, view)

    def test_add_view_register_secured_view(self):
        from zope.interface import Interface
        from repoze.bfg.interfaces import IRequest
        from repoze.bfg.interfaces import ISecuredView
        from repoze.bfg.interfaces import IViewClassifier
        view = lambda *arg: 'OK'
        view.__call_permissive__ = view
        config = self._makeOne()
        config.add_view(view=view)
        wrapper = config.registry.adapters.lookup(
            (IViewClassifier, IRequest, Interface),
            ISecuredView, name='', default=None)
        self.assertEqual(wrapper, view)

    def test_add_view_exception_register_secured_view(self):
        from zope.interface import implementedBy
        from repoze.bfg.interfaces import IRequest
        from repoze.bfg.interfaces import IView
        from repoze.bfg.interfaces import IExceptionViewClassifier
        view = lambda *arg: 'OK'
        view.__call_permissive__ = view
        config = self._makeOne()
        config.add_view(view=view, context=RuntimeError)
        wrapper = config.registry.adapters.lookup(
            (IExceptionViewClassifier, IRequest, implementedBy(RuntimeError)),
            IView, name='', default=None)
        self.assertEqual(wrapper, view)

    def test_add_view_same_phash_overrides_existing_single_view(self):
        from repoze.bfg.compat import md5
        from zope.interface import Interface
        from repoze.bfg.interfaces import IRequest
        from repoze.bfg.interfaces import IView
        from repoze.bfg.interfaces import IViewClassifier
        from repoze.bfg.interfaces import IMultiView
        phash = md5()
        phash.update('xhr:True')
        view = lambda *arg: 'NOT OK'
        view.__phash__ = phash.hexdigest()
        config = self._makeOne()
        config.registry.registerAdapter(
            view, (IViewClassifier, IRequest, Interface), IView, name='')
        def newview(context, request):
            return 'OK'
        config.add_view(view=newview, xhr=True)
        wrapper = self._getViewCallable(config)
        self.failIf(IMultiView.providedBy(wrapper))
        request = DummyRequest()
        request.is_xhr = True
        self.assertEqual(wrapper(None, request), 'OK')

    def test_add_view_exc_same_phash_overrides_existing_single_view(self):
        from repoze.bfg.compat import md5
        from zope.interface import implementedBy
        from repoze.bfg.interfaces import IRequest
        from repoze.bfg.interfaces import IView
        from repoze.bfg.interfaces import IExceptionViewClassifier
        from repoze.bfg.interfaces import IMultiView
        phash = md5()
        phash.update('xhr:True')
        view = lambda *arg: 'NOT OK'
        view.__phash__ = phash.hexdigest()
        config = self._makeOne()
        config.registry.registerAdapter(
            view,
            (IExceptionViewClassifier, IRequest, implementedBy(RuntimeError)),
            IView, name='')
        def newview(context, request):
            return 'OK'
        config.add_view(view=newview, xhr=True,
                        context=RuntimeError)
        wrapper = self._getViewCallable(
            config, ctx_iface=implementedBy(RuntimeError), exception_view=True)
        self.failIf(IMultiView.providedBy(wrapper))
        request = DummyRequest()
        request.is_xhr = True
        self.assertEqual(wrapper(None, request), 'OK')

    def test_add_view_default_phash_overrides_no_phash(self):
        from zope.interface import Interface
        from repoze.bfg.interfaces import IRequest
        from repoze.bfg.interfaces import IView
        from repoze.bfg.interfaces import IViewClassifier
        from repoze.bfg.interfaces import IMultiView
        view = lambda *arg: 'NOT OK'
        config = self._makeOne()
        config.registry.registerAdapter(
            view, (IViewClassifier, IRequest, Interface), IView, name='')
        def newview(context, request):
            return 'OK'
        config.add_view(view=newview)
        wrapper = self._getViewCallable(config)
        self.failIf(IMultiView.providedBy(wrapper))
        request = DummyRequest()
        request.is_xhr = True
        self.assertEqual(wrapper(None, request), 'OK')

    def test_add_view_exc_default_phash_overrides_no_phash(self):
        from zope.interface import implementedBy
        from repoze.bfg.interfaces import IRequest
        from repoze.bfg.interfaces import IView
        from repoze.bfg.interfaces import IExceptionViewClassifier
        from repoze.bfg.interfaces import IMultiView
        view = lambda *arg: 'NOT OK'
        config = self._makeOne()
        config.registry.registerAdapter(
            view,
            (IExceptionViewClassifier, IRequest, implementedBy(RuntimeError)),
            IView, name='')
        def newview(context, request):
            return 'OK'
        config.add_view(view=newview, context=RuntimeError)
        wrapper = self._getViewCallable(
            config, ctx_iface=implementedBy(RuntimeError), exception_view=True)
        self.failIf(IMultiView.providedBy(wrapper))
        request = DummyRequest()
        request.is_xhr = True
        self.assertEqual(wrapper(None, request), 'OK')

    def test_add_view_default_phash_overrides_default_phash(self):
        from repoze.bfg.configuration import DEFAULT_PHASH
        from zope.interface import Interface
        from repoze.bfg.interfaces import IRequest
        from repoze.bfg.interfaces import IView
        from repoze.bfg.interfaces import IViewClassifier
        from repoze.bfg.interfaces import IMultiView
        view = lambda *arg: 'NOT OK'
        view.__phash__ = DEFAULT_PHASH
        config = self._makeOne()
        config.registry.registerAdapter(
            view, (IViewClassifier, IRequest, Interface), IView, name='')
        def newview(context, request):
            return 'OK'
        config.add_view(view=newview)
        wrapper = self._getViewCallable(config)
        self.failIf(IMultiView.providedBy(wrapper))
        request = DummyRequest()
        request.is_xhr = True
        self.assertEqual(wrapper(None, request), 'OK')

    def test_add_view_exc_default_phash_overrides_default_phash(self):
        from repoze.bfg.configuration import DEFAULT_PHASH
        from zope.interface import implementedBy
        from repoze.bfg.interfaces import IRequest
        from repoze.bfg.interfaces import IView
        from repoze.bfg.interfaces import IExceptionViewClassifier
        from repoze.bfg.interfaces import IMultiView
        view = lambda *arg: 'NOT OK'
        view.__phash__ = DEFAULT_PHASH
        config = self._makeOne()
        config.registry.registerAdapter(
            view,
            (IExceptionViewClassifier, IRequest, implementedBy(RuntimeError)),
            IView, name='')
        def newview(context, request):
            return 'OK'
        config.add_view(view=newview, context=RuntimeError)
        wrapper = self._getViewCallable(
            config, ctx_iface=implementedBy(RuntimeError), exception_view=True)
        self.failIf(IMultiView.providedBy(wrapper))
        request = DummyRequest()
        request.is_xhr = True
        self.assertEqual(wrapper(None, request), 'OK')

    def test_add_view_multiview_replaces_existing_view(self):
        from zope.interface import Interface
        from repoze.bfg.interfaces import IRequest
        from repoze.bfg.interfaces import IView
        from repoze.bfg.interfaces import IViewClassifier
        from repoze.bfg.interfaces import IMultiView
        view = lambda *arg: 'OK'
        view.__phash__ = 'abc'
        config = self._makeOne()
        config.registry.registerAdapter(
            view, (IViewClassifier, IRequest, Interface), IView, name='')
        config.add_view(view=view)
        wrapper = self._getViewCallable(config)
        self.failUnless(IMultiView.providedBy(wrapper))
        self.assertEqual(wrapper(None, None), 'OK')

    def test_add_view_exc_multiview_replaces_existing_view(self):
        from zope.interface import implementedBy
        from repoze.bfg.interfaces import IRequest
        from repoze.bfg.interfaces import IView
        from repoze.bfg.interfaces import IExceptionViewClassifier
        from repoze.bfg.interfaces import IViewClassifier
        from repoze.bfg.interfaces import IMultiView
        view = lambda *arg: 'OK'
        view.__phash__ = 'abc'
        config = self._makeOne()
        config.registry.registerAdapter(
            view,
            (IViewClassifier, IRequest, implementedBy(RuntimeError)),
            IView, name='')
        config.registry.registerAdapter(
            view,
            (IExceptionViewClassifier, IRequest, implementedBy(RuntimeError)),
            IView, name='')
        config.add_view(view=view, context=RuntimeError)
        wrapper = self._getViewCallable(
            config, ctx_iface=implementedBy(RuntimeError), exception_view=True)
        self.failUnless(IMultiView.providedBy(wrapper))
        self.assertEqual(wrapper(None, None), 'OK')

    def test_add_view_multiview_replaces_existing_securedview(self):
        from zope.interface import Interface
        from repoze.bfg.interfaces import IRequest
        from repoze.bfg.interfaces import ISecuredView
        from repoze.bfg.interfaces import IMultiView
        from repoze.bfg.interfaces import IViewClassifier
        view = lambda *arg: 'OK'
        view.__phash__ = 'abc'
        config = self._makeOne()
        config.registry.registerAdapter(
            view, (IViewClassifier, IRequest, Interface),
            ISecuredView, name='')
        config.add_view(view=view)
        wrapper = self._getViewCallable(config)
        self.failUnless(IMultiView.providedBy(wrapper))
        self.assertEqual(wrapper(None, None), 'OK')

    def test_add_view_exc_multiview_replaces_existing_securedview(self):
        from zope.interface import implementedBy
        from repoze.bfg.interfaces import IRequest
        from repoze.bfg.interfaces import ISecuredView
        from repoze.bfg.interfaces import IMultiView
        from repoze.bfg.interfaces import IViewClassifier
        from repoze.bfg.interfaces import IExceptionViewClassifier
        view = lambda *arg: 'OK'
        view.__phash__ = 'abc'
        config = self._makeOne()
        config.registry.registerAdapter(
            view,
            (IViewClassifier, IRequest, implementedBy(RuntimeError)),
            ISecuredView, name='')
        config.registry.registerAdapter(
            view,
            (IExceptionViewClassifier, IRequest, implementedBy(RuntimeError)),
            ISecuredView, name='')
        config.add_view(view=view, context=RuntimeError)
        wrapper = self._getViewCallable(
            config, ctx_iface=implementedBy(RuntimeError), exception_view=True)
        self.failUnless(IMultiView.providedBy(wrapper))
        self.assertEqual(wrapper(None, None), 'OK')

    def test_add_view_with_accept_multiview_replaces_existing_view(self):
        from zope.interface import Interface
        from repoze.bfg.interfaces import IRequest
        from repoze.bfg.interfaces import IView
        from repoze.bfg.interfaces import IMultiView
        from repoze.bfg.interfaces import IViewClassifier
        def view(context, request):
            return 'OK'
        def view2(context, request):
            return 'OK2'
        config = self._makeOne()
        config.registry.registerAdapter(
            view, (IViewClassifier, IRequest, Interface), IView, name='')
        config.add_view(view=view2, accept='text/html')
        wrapper = self._getViewCallable(config)
        self.failUnless(IMultiView.providedBy(wrapper))
        self.assertEqual(len(wrapper.views), 1)
        self.assertEqual(len(wrapper.media_views), 1)
        self.assertEqual(wrapper(None, None), 'OK')
        request = DummyRequest()
        request.accept = DummyAccept('text/html', 'text/html')
        self.assertEqual(wrapper(None, request), 'OK2')

    def test_add_view_exc_with_accept_multiview_replaces_existing_view(self):
        from zope.interface import implementedBy
        from repoze.bfg.interfaces import IRequest
        from repoze.bfg.interfaces import IView
        from repoze.bfg.interfaces import IMultiView
        from repoze.bfg.interfaces import IViewClassifier
        from repoze.bfg.interfaces import IExceptionViewClassifier
        def view(context, request):
            return 'OK'
        def view2(context, request):
            return 'OK2'
        config = self._makeOne()
        config.registry.registerAdapter(
            view,
            (IViewClassifier, IRequest, implementedBy(RuntimeError)),
            IView, name='')
        config.registry.registerAdapter(
            view,
            (IExceptionViewClassifier, IRequest, implementedBy(RuntimeError)),
            IView, name='')
        config.add_view(view=view2, accept='text/html', context=RuntimeError)
        wrapper = self._getViewCallable(
            config, ctx_iface=implementedBy(RuntimeError), exception_view=True)
        self.failUnless(IMultiView.providedBy(wrapper))
        self.assertEqual(len(wrapper.views), 1)
        self.assertEqual(len(wrapper.media_views), 1)
        self.assertEqual(wrapper(None, None), 'OK')
        request = DummyRequest()
        request.accept = DummyAccept('text/html', 'text/html')
        self.assertEqual(wrapper(None, request), 'OK2')

    def test_add_view_multiview_replaces_existing_view_with___accept__(self):
        from zope.interface import Interface
        from repoze.bfg.interfaces import IRequest
        from repoze.bfg.interfaces import IView
        from repoze.bfg.interfaces import IMultiView
        from repoze.bfg.interfaces import IViewClassifier
        def view(context, request):
            return 'OK'
        def view2(context, request):
            return 'OK2'
        view.__accept__ = 'text/html'
        view.__phash__ = 'abc'
        config = self._makeOne()
        config.registry.registerAdapter(
            view, (IViewClassifier, IRequest, Interface), IView, name='')
        config.add_view(view=view2)
        wrapper = self._getViewCallable(config)
        self.failUnless(IMultiView.providedBy(wrapper))
        self.assertEqual(len(wrapper.views), 1)
        self.assertEqual(len(wrapper.media_views), 1)
        self.assertEqual(wrapper(None, None), 'OK2')
        request = DummyRequest()
        request.accept = DummyAccept('text/html')
        self.assertEqual(wrapper(None, request), 'OK')

    def test_add_view_exc_mulview_replaces_existing_view_with___accept__(self):
        from zope.interface import implementedBy
        from repoze.bfg.interfaces import IRequest
        from repoze.bfg.interfaces import IView
        from repoze.bfg.interfaces import IMultiView
        from repoze.bfg.interfaces import IViewClassifier
        from repoze.bfg.interfaces import IExceptionViewClassifier
        def view(context, request):
            return 'OK'
        def view2(context, request):
            return 'OK2'
        view.__accept__ = 'text/html'
        view.__phash__ = 'abc'
        config = self._makeOne()
        config.registry.registerAdapter(
            view,
            (IViewClassifier, IRequest, implementedBy(RuntimeError)),
            IView, name='')
        config.registry.registerAdapter(
            view,
            (IExceptionViewClassifier, IRequest, implementedBy(RuntimeError)),
            IView, name='')
        config.add_view(view=view2, context=RuntimeError)
        wrapper = self._getViewCallable(
            config, ctx_iface=implementedBy(RuntimeError), exception_view=True)
        self.failUnless(IMultiView.providedBy(wrapper))
        self.assertEqual(len(wrapper.views), 1)
        self.assertEqual(len(wrapper.media_views), 1)
        self.assertEqual(wrapper(None, None), 'OK2')
        request = DummyRequest()
        request.accept = DummyAccept('text/html')
        self.assertEqual(wrapper(None, request), 'OK')

    def test_add_view_multiview_replaces_multiview(self):
        from zope.interface import Interface
        from repoze.bfg.interfaces import IRequest
        from repoze.bfg.interfaces import IMultiView
        from repoze.bfg.interfaces import IViewClassifier
        view = DummyMultiView()
        config = self._makeOne()
        config.registry.registerAdapter(
            view, (IViewClassifier, IRequest, Interface),
            IMultiView, name='')
        view2 = lambda *arg: 'OK2'
        config.add_view(view=view2)
        wrapper = self._getViewCallable(config)
        self.failUnless(IMultiView.providedBy(wrapper))
        self.assertEqual([x[:2] for x in wrapper.views], [(view2, None)])
        self.assertEqual(wrapper(None, None), 'OK1')

    def test_add_view_exc_multiview_replaces_multiview(self):
        from zope.interface import implementedBy
        from repoze.bfg.interfaces import IRequest
        from repoze.bfg.interfaces import IMultiView
        from repoze.bfg.interfaces import IViewClassifier
        from repoze.bfg.interfaces import IExceptionViewClassifier
        view = DummyMultiView()
        config = self._makeOne()
        config.registry.registerAdapter(
            view,
            (IViewClassifier, IRequest, implementedBy(RuntimeError)),
            IMultiView, name='')
        config.registry.registerAdapter(
            view,
            (IExceptionViewClassifier, IRequest, implementedBy(RuntimeError)),
            IMultiView, name='')
        view2 = lambda *arg: 'OK2'
        config.add_view(view=view2, context=RuntimeError)
        wrapper = self._getViewCallable(
            config, ctx_iface=implementedBy(RuntimeError), exception_view=True)
        self.failUnless(IMultiView.providedBy(wrapper))
        self.assertEqual([x[:2] for x in wrapper.views], [(view2, None)])
        self.assertEqual(wrapper(None, None), 'OK1')

    def test_add_view_multiview_context_superclass_then_subclass(self):
        from zope.interface import Interface
        from repoze.bfg.interfaces import IRequest
        from repoze.bfg.interfaces import IView
        from repoze.bfg.interfaces import IMultiView
        from repoze.bfg.interfaces import IViewClassifier
        class ISuper(Interface):
            pass
        class ISub(ISuper):
            pass
        view = lambda *arg: 'OK'
        view2 = lambda *arg: 'OK2'
        config = self._makeOne()
        config.registry.registerAdapter(
            view, (IViewClassifier, IRequest, ISuper), IView, name='')
        config.add_view(view=view2, for_=ISub)
        wrapper = self._getViewCallable(config, ISuper, IRequest)
        self.failIf(IMultiView.providedBy(wrapper))
        self.assertEqual(wrapper(None, None), 'OK')
        wrapper = self._getViewCallable(config, ISub, IRequest)
        self.failIf(IMultiView.providedBy(wrapper))
        self.assertEqual(wrapper(None, None), 'OK2')

    def test_add_view_multiview_exception_superclass_then_subclass(self):
        from zope.interface import implementedBy
        from repoze.bfg.interfaces import IRequest
        from repoze.bfg.interfaces import IView
        from repoze.bfg.interfaces import IMultiView
        from repoze.bfg.interfaces import IViewClassifier
        from repoze.bfg.interfaces import IExceptionViewClassifier
        class Super(Exception):
            pass
        class Sub(Super):
            pass
        view = lambda *arg: 'OK'
        view2 = lambda *arg: 'OK2'
        config = self._makeOne()
        config.registry.registerAdapter(
            view, (IViewClassifier, IRequest, Super), IView, name='')
        config.registry.registerAdapter(
            view, (IExceptionViewClassifier, IRequest, Super), IView, name='')
        config.add_view(view=view2, for_=Sub)
        wrapper = self._getViewCallable(
            config, implementedBy(Super), IRequest)
        wrapper_exc_view = self._getViewCallable(
            config, implementedBy(Super), IRequest, exception_view=True)
        self.assertEqual(wrapper_exc_view, wrapper)
        self.failIf(IMultiView.providedBy(wrapper_exc_view))
        self.assertEqual(wrapper_exc_view(None, None), 'OK')
        wrapper = self._getViewCallable(
            config, implementedBy(Sub), IRequest)
        wrapper_exc_view = self._getViewCallable(
            config, implementedBy(Sub), IRequest, exception_view=True)
        self.assertEqual(wrapper_exc_view, wrapper)
        self.failIf(IMultiView.providedBy(wrapper_exc_view))
        self.assertEqual(wrapper_exc_view(None, None), 'OK2')

    def test_add_view_multiview_call_ordering(self):
        from zope.interface import directlyProvides
        def view1(context, request): return 'view1'
        def view2(context, request): return 'view2'
        def view3(context, request): return 'view3'
        def view4(context, request): return 'view4'
        def view5(context, request): return 'view5'
        def view6(context, request): return 'view6'
        def view7(context, request): return 'view7'
        def view8(context, request): return 'view8'
        config = self._makeOne()
        config.add_view(view=view1)
        config.add_view(view=view2, request_method='POST')
        config.add_view(view=view3,request_param='param')
        config.add_view(view=view4, containment=IDummy)
        config.add_view(view=view5, request_method='POST',request_param='param')
        config.add_view(view=view6, request_method='POST', containment=IDummy)
        config.add_view(view=view7, request_param='param', containment=IDummy)
        config.add_view(view=view8, request_method='POST',request_param='param',
                        containment=IDummy)

        wrapper = self._getViewCallable(config)

        ctx = DummyContext()
        request = self._makeRequest(config)
        request.method = 'GET'
        request.params = {}
        self.assertEqual(wrapper(ctx, request), 'view1')

        ctx = DummyContext()
        request = self._makeRequest(config)
        request.params = {}
        request.method = 'POST'
        self.assertEqual(wrapper(ctx, request), 'view2')

        ctx = DummyContext()
        request = self._makeRequest(config)
        request.params = {'param':'1'}
        request.method = 'GET'
        self.assertEqual(wrapper(ctx, request), 'view3')

        ctx = DummyContext()
        directlyProvides(ctx, IDummy)
        request = self._makeRequest(config)
        request.method = 'GET'
        request.params = {}
        self.assertEqual(wrapper(ctx, request), 'view4')

        ctx = DummyContext()
        request = self._makeRequest(config)
        request.method = 'POST'
        request.params = {'param':'1'}
        self.assertEqual(wrapper(ctx, request), 'view5')

        ctx = DummyContext()
        directlyProvides(ctx, IDummy)
        request = self._makeRequest(config)
        request.params = {}
        request.method = 'POST'
        self.assertEqual(wrapper(ctx, request), 'view6')

        ctx = DummyContext()
        directlyProvides(ctx, IDummy)
        request = self._makeRequest(config)
        request.method = 'GET'
        request.params = {'param':'1'}
        self.assertEqual(wrapper(ctx, request), 'view7')

        ctx = DummyContext()
        directlyProvides(ctx, IDummy)
        request = self._makeRequest(config)
        request.method = 'POST'
        request.params = {'param':'1'}
        self.assertEqual(wrapper(ctx, request), 'view8')

    def test_add_view_with_template_renderer(self):
        class view(object):
            def __init__(self, context, request):
                self.request = request
                self.context = context

            def __call__(self):
                return {'a':'1'}
        config = self._makeOne()
        renderer = self._registerRenderer(config)
        fixture = 'repoze.bfg.tests:fixtures/minimal.txt'
        config.add_view(view=view, renderer=fixture)
        wrapper = self._getViewCallable(config)
        request = self._makeRequest(config)
        result = wrapper(None, request)
        self.assertEqual(result.body, 'Hello!')
        self.assertEqual(renderer.path, 'repoze.bfg.tests:fixtures/minimal.txt')

    def test_add_view_with_template_renderer_no_callable(self):
        config = self._makeOne()
        renderer = self._registerRenderer(config)
        fixture = 'repoze.bfg.tests:fixtures/minimal.txt'
        config.add_view(view=None, renderer=fixture)
        wrapper = self._getViewCallable(config)
        request = self._makeRequest(config)
        result = wrapper(None, request)
        self.assertEqual(result.body, 'Hello!')
        self.assertEqual(renderer.path, 'repoze.bfg.tests:fixtures/minimal.txt')

    def test_add_view_with_request_type_as_iface(self):
        from zope.interface import directlyProvides
        def view(context, request):
            return 'OK'
        config = self._makeOne()
        config.add_view(request_type=IDummy, view=view)
        wrapper = self._getViewCallable(config, None)
        request = self._makeRequest(config)
        directlyProvides(request, IDummy)
        result = wrapper(None, request)
        self.assertEqual(result, 'OK')

    def test_add_view_with_request_type_as_noniface(self):
        from repoze.bfg.exceptions import ConfigurationError
        view = lambda *arg: 'OK'
        config = self._makeOne()
        self.assertRaises(ConfigurationError,
                          config.add_view, view, '', None, None, object)

    def test_add_view_with_route_name(self):
        from zope.component import ComponentLookupError
        view = lambda *arg: 'OK'
        config = self._makeOne()
        config.add_view(view=view, route_name='foo')
        self.assertEqual(len(config.registry.deferred_route_views), 1)
        infos = config.registry.deferred_route_views['foo']
        self.assertEqual(len(infos), 1)
        info = infos[0]
        self.assertEqual(info['route_name'], 'foo')
        self.assertEqual(info['view'], view)
        self.assertRaises(ComponentLookupError,
                          self._getRouteRequestIface, config, 'foo')
        wrapper = self._getViewCallable(config, None)
        self.assertEqual(wrapper, None)
        config.add_route('foo', '/a/b')
        request_iface = self._getRouteRequestIface(config, 'foo')
        self.failIfEqual(request_iface, None)
        wrapper = self._getViewCallable(config, request_iface=request_iface)
        self.failIfEqual(wrapper, None)
        self.assertEqual(wrapper(None, None), 'OK')

    def test_add_view_with_route_name_exception(self):
        from zope.interface import implementedBy
        from zope.component import ComponentLookupError
        view = lambda *arg: 'OK'
        config = self._makeOne()
        config.add_view(view=view, route_name='foo', context=RuntimeError)
        self.assertEqual(len(config.registry.deferred_route_views), 1)
        infos = config.registry.deferred_route_views['foo']
        self.assertEqual(len(infos), 1)
        info = infos[0]
        self.assertEqual(info['route_name'], 'foo')
        self.assertEqual(info['view'], view)
        self.assertRaises(ComponentLookupError,
                          self._getRouteRequestIface, config, 'foo')
        wrapper_exc_view = self._getViewCallable(
            config, ctx_iface=implementedBy(RuntimeError),
            exception_view=True)
        self.assertEqual(wrapper_exc_view, None)
        config.add_route('foo', '/a/b')
        request_iface = self._getRouteRequestIface(config, 'foo')
        self.failIfEqual(request_iface, None)
        wrapper_exc_view = self._getViewCallable(
            config, ctx_iface=implementedBy(RuntimeError),
            request_iface=request_iface, exception_view=True)
        self.failIfEqual(wrapper_exc_view, None)
        wrapper = self._getViewCallable(
            config, ctx_iface=implementedBy(RuntimeError),
            request_iface=request_iface)
        self.assertEqual(wrapper_exc_view, wrapper)
        self.assertEqual(wrapper_exc_view(None, None), 'OK')

    def test_add_view_with_request_method_true(self):
        view = lambda *arg: 'OK'
        config = self._makeOne()
        config.add_view(view=view, request_method='POST')
        wrapper = self._getViewCallable(config)
        request = self._makeRequest(config)
        request.method = 'POST'
        self.assertEqual(wrapper(None, request), 'OK')

    def test_add_view_with_request_method_false(self):
        view = lambda *arg: 'OK'
        config = self._makeOne()
        config.add_view(view=view, request_method='POST')
        wrapper = self._getViewCallable(config)
        request = self._makeRequest(config)
        request.method = 'GET'
        self._assertNotFound(wrapper, None, request)

    def test_add_view_with_request_param_noval_true(self):
        view = lambda *arg: 'OK'
        config = self._makeOne()
        config.add_view(view=view, request_param='abc')
        wrapper = self._getViewCallable(config)
        request = self._makeRequest(config)
        request.params = {'abc':''}
        self.assertEqual(wrapper(None, request), 'OK')

    def test_add_view_with_request_param_noval_false(self):
        view = lambda *arg: 'OK'
        config = self._makeOne()
        config.add_view(view=view, request_param='abc')
        wrapper = self._getViewCallable(config)
        request = self._makeRequest(config)
        request.params = {}
        self._assertNotFound(wrapper, None, request)

    def test_add_view_with_request_param_val_true(self):
        view = lambda *arg: 'OK'
        config = self._makeOne()
        config.add_view(view=view, request_param='abc=123')
        wrapper = self._getViewCallable(config)
        request = self._makeRequest(config)
        request.params = {'abc':'123'}
        self.assertEqual(wrapper(None, request), 'OK')

    def test_add_view_with_request_param_val_false(self):
        view = lambda *arg: 'OK'
        config = self._makeOne()
        config.add_view(view=view, request_param='abc=123')
        wrapper = self._getViewCallable(config)
        request = self._makeRequest(config)
        request.params = {'abc':''}
        self._assertNotFound(wrapper, None, request)

    def test_add_view_with_xhr_true(self):
        view = lambda *arg: 'OK'
        config = self._makeOne()
        config.add_view(view=view, xhr=True)
        wrapper = self._getViewCallable(config)
        request = self._makeRequest(config)
        request.is_xhr = True
        self.assertEqual(wrapper(None, request), 'OK')

    def test_add_view_with_xhr_false(self):
        view = lambda *arg: 'OK'
        config = self._makeOne()
        config.add_view(view=view, xhr=True)
        wrapper = self._getViewCallable(config)
        request = self._makeRequest(config)
        request.is_xhr = False
        self._assertNotFound(wrapper, None, request)

    def test_add_view_with_header_badregex(self):
        from repoze.bfg.exceptions import ConfigurationError
        view = lambda *arg: 'OK'
        config = self._makeOne()
        self.assertRaises(ConfigurationError,
                          config.add_view, view=view, header='Host:a\\')

    def test_add_view_with_header_noval_match(self):
        view = lambda *arg: 'OK'
        config = self._makeOne()
        config.add_view(view=view, header='Host')
        wrapper = self._getViewCallable(config)
        request = self._makeRequest(config)
        request.headers = {'Host':'whatever'}
        self.assertEqual(wrapper(None, request), 'OK')

    def test_add_view_with_header_noval_nomatch(self):
        view = lambda *arg: 'OK'
        config = self._makeOne()
        config.add_view(view=view, header='Host')
        wrapper = self._getViewCallable(config)
        request = self._makeRequest(config)
        request.headers = {'NotHost':'whatever'}
        self._assertNotFound(wrapper, None, request)

    def test_add_view_with_header_val_match(self):
        view = lambda *arg: 'OK'
        config = self._makeOne()
        config.add_view(view=view, header=r'Host:\d')
        wrapper = self._getViewCallable(config)
        request = self._makeRequest(config)
        request.headers = {'Host':'1'}
        self.assertEqual(wrapper(None, request), 'OK')

    def test_add_view_with_header_val_nomatch(self):
        view = lambda *arg: 'OK'
        config = self._makeOne()
        config.add_view(view=view, header=r'Host:\d')
        wrapper = self._getViewCallable(config)
        request = self._makeRequest(config)
        request.headers = {'Host':'abc'}
        self._assertNotFound(wrapper, None, request)

    def test_add_view_with_accept_match(self):
        view = lambda *arg: 'OK'
        config = self._makeOne()
        config.add_view(view=view, accept='text/xml')
        wrapper = self._getViewCallable(config)
        request = self._makeRequest(config)
        request.accept = ['text/xml']
        self.assertEqual(wrapper(None, request), 'OK')

    def test_add_view_with_accept_nomatch(self):
        view = lambda *arg: 'OK'
        config = self._makeOne()
        config.add_view(view=view, accept='text/xml')
        wrapper = self._getViewCallable(config)
        request = self._makeRequest(config)
        request.accept = ['text/html']
        self._assertNotFound(wrapper, None, request)

    def test_add_view_with_containment_true(self):
        from zope.interface import directlyProvides
        view = lambda *arg: 'OK'
        config = self._makeOne()
        config.add_view(view=view, containment=IDummy)
        wrapper = self._getViewCallable(config)
        context = DummyContext()
        directlyProvides(context, IDummy)
        self.assertEqual(wrapper(context, None), 'OK')

    def test_add_view_with_containment_false(self):
        view = lambda *arg: 'OK'
        config = self._makeOne()
        config.add_view(view=view, containment=IDummy)
        wrapper = self._getViewCallable(config)
        context = DummyContext()
        self._assertNotFound(wrapper, context, None)

    def test_add_view_with_path_info_badregex(self):
        from repoze.bfg.exceptions import ConfigurationError
        view = lambda *arg: 'OK'
        config = self._makeOne()
        self.assertRaises(ConfigurationError,
                          config.add_view, view=view, path_info='\\')

    def test_add_view_with_path_info_match(self):
        view = lambda *arg: 'OK'
        config = self._makeOne()
        config.add_view(view=view, path_info='/foo')
        wrapper = self._getViewCallable(config)
        request = self._makeRequest(config)
        request.path_info = '/foo'
        self.assertEqual(wrapper(None, request), 'OK')

    def test_add_view_with_path_info_nomatch(self):
        view = lambda *arg: 'OK'
        config = self._makeOne()
        config.add_view(view=view, path_info='/foo')
        wrapper = self._getViewCallable(config)
        request = self._makeRequest(config)
        request.path_info = '/'
        self._assertNotFound(wrapper, None, request)

    def test_add_view_with_custom_predicates_match(self):
        view = lambda *arg: 'OK'
        config = self._makeOne()
        def pred1(context, request):
            return True
        def pred2(context, request):
            return True
        predicates = (pred1, pred2)
        config.add_view(view=view, custom_predicates=predicates)
        wrapper = self._getViewCallable(config)
        request = self._makeRequest(config)
        self.assertEqual(wrapper(None, request), 'OK')

    def test_add_view_with_custom_predicates_nomatch(self):
        view = lambda *arg: 'OK'
        config = self._makeOne()
        def pred1(context, request):
            return True
        def pred2(context, request):
            return False
        predicates = (pred1, pred2)
        config.add_view(view=view, custom_predicates=predicates)
        wrapper = self._getViewCallable(config)
        request = self._makeRequest(config)
        self._assertNotFound(wrapper, None, request)

    def test_add_view_custom_predicate_bests_standard_predicate(self):
        view = lambda *arg: 'OK'
        view2 = lambda *arg: 'NOT OK'
        config = self._makeOne()
        def pred1(context, request):
            return True
        config.add_view(view=view, custom_predicates=(pred1,))
        config.add_view(view=view2, request_method='GET')
        wrapper = self._getViewCallable(config)
        request = self._makeRequest(config)
        request.method = 'GET'
        self.assertEqual(wrapper(None, request), 'OK')

    def test_add_view_custom_more_preds_first_bests_fewer_preds_last(self):
        view = lambda *arg: 'OK'
        view2 = lambda *arg: 'NOT OK'
        config = self._makeOne()
        config.add_view(view=view, request_method='GET', xhr=True)
        config.add_view(view=view2, request_method='GET')
        wrapper = self._getViewCallable(config)
        request = self._makeRequest(config)
        request.method = 'GET'
        request.is_xhr = True
        self.assertEqual(wrapper(None, request), 'OK')

    def test_add_view_same_predicates(self):
        view2 = lambda *arg: 'second'
        view1 = lambda *arg: 'first'
        config = self._makeOne()
        config.add_view(view=view1)
        config.add_view(view=view2)
        view = self._getViewCallable(config)
        request = self._makeRequest(config)
        self.assertEqual(view(None, request), 'second')

    def _assertRoute(self, config, name, path, num_predicates=0):
        from repoze.bfg.interfaces import IRoutesMapper
        mapper = config.registry.getUtility(IRoutesMapper)
        routes = mapper.get_routes()
        route = routes[0]
        self.assertEqual(len(routes), 1)
        self.assertEqual(route.name, name)
        self.assertEqual(route.path, path)
        self.assertEqual(len(routes[0].predicates), num_predicates)
        return route

    def test_add_route_defaults(self):
        config = self._makeOne()
        config.add_route('name', 'path')
        self._assertRoute(config, 'name', 'path')

    def test_add_route_with_xhr(self):
        config = self._makeOne()
        config.add_route('name', 'path', xhr=True)
        route = self._assertRoute(config, 'name', 'path', 1)
        predicate = route.predicates[0]
        request = self._makeRequest(config)
        request.is_xhr = True
        self.assertEqual(predicate(None, request), True)
        request = self._makeRequest(config)
        request.is_xhr = False
        self.assertEqual(predicate(None, request), False)

    def test_add_route_with_request_method(self):
        config = self._makeOne()
        config.add_route('name', 'path', request_method='GET')
        route = self._assertRoute(config, 'name', 'path', 1)
        predicate = route.predicates[0]
        request = self._makeRequest(config)
        request.method = 'GET'
        self.assertEqual(predicate(None, request), True)
        request = self._makeRequest(config)
        request.method = 'POST'
        self.assertEqual(predicate(None, request), False)

    def test_add_route_with_path_info(self):
        config = self._makeOne()
        config.add_route('name', 'path', path_info='/foo')
        route = self._assertRoute(config, 'name', 'path', 1)
        predicate = route.predicates[0]
        request = self._makeRequest(config)
        request.path_info = '/foo'
        self.assertEqual(predicate(None, request), True)
        request = self._makeRequest(config)
        request.path_info = '/'
        self.assertEqual(predicate(None, request), False)

    def test_add_route_with_request_param(self):
        config = self._makeOne()
        config.add_route('name', 'path', request_param='abc')
        route = self._assertRoute(config, 'name', 'path', 1)
        predicate = route.predicates[0]
        request = self._makeRequest(config)
        request.params = {'abc':'123'}
        self.assertEqual(predicate(None, request), True)
        request = self._makeRequest(config)
        request.params = {}
        self.assertEqual(predicate(None, request), False)

    def test_add_route_with_custom_predicates(self):
        config = self._makeOne()
        def pred1(context, request): pass
        def pred2(context, request): pass
        config.add_route('name', 'path', custom_predicates=(pred1, pred2))
        route = self._assertRoute(config, 'name', 'path', 2)
        self.assertEqual(route.predicates, [pred1, pred2])

    def test_add_route_with_header(self):
        config = self._makeOne()
        config.add_route('name', 'path', header='Host')
        route = self._assertRoute(config, 'name', 'path', 1)
        predicate = route.predicates[0]
        request = self._makeRequest(config)
        request.headers = {'Host':'example.com'}
        self.assertEqual(predicate(None, request), True)
        request = self._makeRequest(config)
        request.headers = {}
        self.assertEqual(predicate(None, request), False)

    def test_add_route_with_accept(self):
        config = self._makeOne()
        config.add_route('name', 'path', accept='text/xml')
        route = self._assertRoute(config, 'name', 'path', 1)
        predicate = route.predicates[0]
        request = self._makeRequest(config)
        request.accept = ['text/xml']
        self.assertEqual(predicate(None, request), True)
        request = self._makeRequest(config)
        request.accept = ['text/html']
        self.assertEqual(predicate(None, request), False)

    def test_add_route_with_view(self):
        config = self._makeOne()
        view = lambda *arg: 'OK'
        config.add_route('name', 'path', view=view)
        request_type = self._getRouteRequestIface(config, 'name')
        wrapper = self._getViewCallable(config, None, request_type)
        self.assertEqual(wrapper(None, None), 'OK')
        self._assertRoute(config, 'name', 'path')

    def test_add_route_with_view_context(self):
        config = self._makeOne()
        view = lambda *arg: 'OK'
        config.add_route('name', 'path', view=view, view_context=IDummy)
        request_type = self._getRouteRequestIface(config, 'name')
        wrapper = self._getViewCallable(config, IDummy, request_type)
        self.assertEqual(wrapper(None, None), 'OK')
        self._assertRoute(config, 'name', 'path')
        wrapper = self._getViewCallable(config, IOther, request_type)
        self.assertEqual(wrapper, None)

    def test_add_route_with_view_exception(self):
        from zope.interface import implementedBy
        config = self._makeOne()
        view = lambda *arg: 'OK'
        config.add_route('name', 'path', view=view, view_context=RuntimeError)
        request_type = self._getRouteRequestIface(config, 'name')
        wrapper = self._getViewCallable(
            config, ctx_iface=implementedBy(RuntimeError),
            request_iface=request_type, exception_view=True)
        self.assertEqual(wrapper(None, None), 'OK')
        self._assertRoute(config, 'name', 'path')
        wrapper = self._getViewCallable(
            config, ctx_iface=IOther,
            request_iface=request_type, exception_view=True)
        self.assertEqual(wrapper, None)

    def test_add_route_with_view_for(self):
        config = self._makeOne()
        view = lambda *arg: 'OK'
        config.add_route('name', 'path', view=view, view_for=IDummy)
        request_type = self._getRouteRequestIface(config, 'name')
        wrapper = self._getViewCallable(config, IDummy, request_type)
        self.assertEqual(wrapper(None, None), 'OK')
        self._assertRoute(config, 'name', 'path')
        wrapper = self._getViewCallable(config, IOther, request_type)
        self.assertEqual(wrapper, None)

    def test_add_route_with_for_(self):
        config = self._makeOne()
        view = lambda *arg: 'OK'
        config.add_route('name', 'path', view=view, for_=IDummy)
        request_type = self._getRouteRequestIface(config, 'name')
        wrapper = self._getViewCallable(config, IDummy, request_type)
        self.assertEqual(wrapper(None, None), 'OK')
        self._assertRoute(config, 'name', 'path')
        wrapper = self._getViewCallable(config, IOther, request_type)
        self.assertEqual(wrapper, None)

    def test_add_route_with_view_renderer(self):
        config = self._makeOne()
        self._registerRenderer(config)
        view = lambda *arg: 'OK'
        config.add_route('name', 'path', view=view,
                         view_renderer='fixtures/minimal.txt')
        request_type = self._getRouteRequestIface(config, 'name')
        wrapper = self._getViewCallable(config, None, request_type)
        self._assertRoute(config, 'name', 'path')
        self.assertEqual(wrapper(None, None).body, 'Hello!')

    def test_add_route_with_view_attr(self):
        config = self._makeOne()
        self._registerRenderer(config)
        class View(object):
            def __init__(self, context, request):
                pass
            def alt(self):
                return 'OK'
        config.add_route('name', 'path', view=View, view_attr='alt')
        request_type = self._getRouteRequestIface(config, 'name')
        wrapper = self._getViewCallable(config, None, request_type)
        self._assertRoute(config, 'name', 'path')
        self.assertEqual(wrapper(None, None), 'OK')

    def test_add_route_with_view_renderer_alias(self):
        config = self._makeOne()
        self._registerRenderer(config)
        view = lambda *arg: 'OK'
        config.add_route('name', 'path', view=view,
                         renderer='fixtures/minimal.txt')
        request_type = self._getRouteRequestIface(config, 'name')
        wrapper = self._getViewCallable(config, None, request_type)
        self._assertRoute(config, 'name', 'path')
        self.assertEqual(wrapper(None, None).body, 'Hello!')

    def test_add_route_with_view_permission(self):
        from repoze.bfg.interfaces import IAuthenticationPolicy
        from repoze.bfg.interfaces import IAuthorizationPolicy
        config = self._makeOne()
        policy = lambda *arg: None
        config.registry.registerUtility(policy, IAuthenticationPolicy)
        config.registry.registerUtility(policy, IAuthorizationPolicy)
        view = lambda *arg: 'OK'
        config.add_route('name', 'path', view=view, view_permission='edit')
        request_type = self._getRouteRequestIface(config, 'name')
        wrapper = self._getViewCallable(config, None, request_type)
        self._assertRoute(config, 'name', 'path')
        self.failUnless(hasattr(wrapper, '__call_permissive__'))

    def test_add_route_with_view_permission_alias(self):
        from repoze.bfg.interfaces import IAuthenticationPolicy
        from repoze.bfg.interfaces import IAuthorizationPolicy
        config = self._makeOne()
        policy = lambda *arg: None
        config.registry.registerUtility(policy, IAuthenticationPolicy)
        config.registry.registerUtility(policy, IAuthorizationPolicy)
        view = lambda *arg: 'OK'
        config.add_route('name', 'path', view=view, permission='edit')
        request_type = self._getRouteRequestIface(config, 'name')
        wrapper = self._getViewCallable(config, None, request_type)
        self._assertRoute(config, 'name', 'path')
        self.failUnless(hasattr(wrapper, '__call_permissive__'))

    def test__override_not_yet_registered(self):
        from repoze.bfg.interfaces import IPackageOverrides
        package = DummyPackage('package')
        opackage = DummyPackage('opackage')
        config = self._makeOne()
        config._override(package, 'path', opackage, 'oprefix',
                         PackageOverrides=DummyOverrides)
        overrides = config.registry.queryUtility(IPackageOverrides,
                                                 name='package')
        self.assertEqual(overrides.inserted, [('path', 'opackage', 'oprefix')])
        self.assertEqual(overrides.package, package)

    def test__override_already_registered(self):
        from repoze.bfg.interfaces import IPackageOverrides
        package = DummyPackage('package')
        opackage = DummyPackage('opackage')
        overrides = DummyOverrides(package)
        config = self._makeOne()
        config.registry.registerUtility(overrides, IPackageOverrides,
                                        name='package')
        config._override(package, 'path', opackage, 'oprefix',
                         PackageOverrides=DummyOverrides)
        self.assertEqual(overrides.inserted, [('path', 'opackage', 'oprefix')])
        self.assertEqual(overrides.package, package)

    def test_add_static_view_here_relative(self):
        from repoze.bfg.static import PackageURLParser
        from zope.interface import implementedBy
        from repoze.bfg.static import StaticRootFactory
        from repoze.bfg.interfaces import IView
        from repoze.bfg.interfaces import IViewClassifier
        config = self._makeOne()
        config.add_static_view('static', 'fixtures/static')
        request_type = self._getRouteRequestIface(config, 'static')
        route = self._assertRoute(config, 'static', 'static*subpath')
        self.assertEqual(route.factory.__class__, StaticRootFactory)
        iface = implementedBy(StaticRootFactory)
        wrapped = config.registry.adapters.lookup(
            (IViewClassifier, request_type, iface), IView, name='')
        request = self._makeRequest(config)
        self.assertEqual(wrapped(None, request).__class__, PackageURLParser)

    def test_add_static_view_package_relative(self):
        from repoze.bfg.static import PackageURLParser
        from zope.interface import implementedBy
        from repoze.bfg.static import StaticRootFactory
        from repoze.bfg.interfaces import IView
        from repoze.bfg.interfaces import IViewClassifier
        config = self._makeOne()
        config.add_static_view('static', 'repoze.bfg.tests:fixtures/static')
        request_type = self._getRouteRequestIface(config, 'static')
        route = self._assertRoute(config, 'static', 'static*subpath')
        self.assertEqual(route.factory.__class__, StaticRootFactory)
        iface = implementedBy(StaticRootFactory)
        wrapped = config.registry.adapters.lookup(
            (IViewClassifier, request_type, iface), IView, name='')
        request = self._makeRequest(config)
        self.assertEqual(wrapped(None, request).__class__, PackageURLParser)

    def test_add_static_view_absolute(self):
        from paste.urlparser import StaticURLParser
        import os
        from zope.interface import implementedBy
        from repoze.bfg.static import StaticRootFactory
        from repoze.bfg.interfaces import IView
        from repoze.bfg.interfaces import IViewClassifier
        config = self._makeOne()
        here = os.path.dirname(__file__)
        static_path = os.path.join(here, 'fixtures', 'static')
        config.add_static_view('static', static_path)
        request_type = self._getRouteRequestIface(config, 'static')
        route = self._assertRoute(config, 'static', 'static*subpath')
        self.assertEqual(route.factory.__class__, StaticRootFactory)
        iface = implementedBy(StaticRootFactory)
        wrapped = config.registry.adapters.lookup(
            (IViewClassifier, request_type, iface), IView, name='')
        request = self._makeRequest(config)
        self.assertEqual(wrapped(None, request).__class__, StaticURLParser)

    def test_set_notfound_view(self):
        from zope.interface import implementedBy
        from repoze.bfg.interfaces import IRequest
        from repoze.bfg.exceptions import NotFound
        config = self._makeOne()
        view = lambda *arg: arg
        config.set_notfound_view(view)
        request = self._makeRequest(config)
        view = self._getViewCallable(config, ctx_iface=implementedBy(NotFound),
                                     request_iface=IRequest)
        result = view(None, request)
        self.assertEqual(result, (None, request))

    def test_set_notfound_view_request_has_context(self):
        from zope.interface import implementedBy
        from repoze.bfg.interfaces import IRequest
        from repoze.bfg.exceptions import NotFound
        config = self._makeOne()
        view = lambda *arg: arg
        config.set_notfound_view(view)
        request = self._makeRequest(config)
        request.context = 'abc'
        view = self._getViewCallable(config, ctx_iface=implementedBy(NotFound),
                                     request_iface=IRequest)
        result = view(None, request)
        self.assertEqual(result, ('abc', request))

    def test_set_forbidden_view(self):
        from zope.interface import implementedBy
        from repoze.bfg.interfaces import IRequest
        from repoze.bfg.exceptions import Forbidden
        config = self._makeOne()
        view = lambda *arg: 'OK'
        config.set_forbidden_view(view)
        request = self._makeRequest(config)
        view = self._getViewCallable(config, ctx_iface=implementedBy(Forbidden),
                                     request_iface=IRequest)
        result = view(None, request)
        self.assertEqual(result, 'OK')

    def test_set_forbidden_view_request_has_context(self):
        from zope.interface import implementedBy
        from repoze.bfg.interfaces import IRequest
        from repoze.bfg.exceptions import Forbidden
        config = self._makeOne()
        view = lambda *arg: arg
        config.set_forbidden_view(view)
        request = self._makeRequest(config)
        request.context = 'abc'
        view = self._getViewCallable(config, ctx_iface=implementedBy(Forbidden),
                                     request_iface=IRequest)
        result = view(None, request)
        self.assertEqual(result, ('abc', request))

    def test__set_authentication_policy(self):
        from repoze.bfg.interfaces import IAuthenticationPolicy
        config = self._makeOne()
        policy = object()
        config._set_authentication_policy(policy)
        self.assertEqual(
            config.registry.getUtility(IAuthenticationPolicy), policy)

    def test__set_authorization_policy(self):
        from repoze.bfg.interfaces import IAuthorizationPolicy
        config = self._makeOne()
        policy = object()
        config._set_authorization_policy(policy)
        self.assertEqual(
            config.registry.getUtility(IAuthorizationPolicy), policy)

    def test_set_locale_negotiator(self):
        from repoze.bfg.interfaces import ILocaleNegotiator
        config = self._makeOne()
        def negotiator(request): pass
        config.set_locale_negotiator(negotiator)
        self.assertEqual(config.registry.getUtility(ILocaleNegotiator),
                         negotiator)

    def test_add_translation_dirs_missing_dir(self):
        from repoze.bfg.exceptions import ConfigurationError
        config = self._makeOne()
        self.assertRaises(ConfigurationError,
                          config.add_translation_dirs,
                          '/wont/exist/on/my/system')

    def test_add_translation_dirs_resource_spec(self):
        import os
        from repoze.bfg.interfaces import ITranslationDirectories
        config = self._makeOne()
        config.add_translation_dirs('repoze.bfg.tests.localeapp:locale')
        here = os.path.dirname(__file__)
        locale = os.path.join(here, 'localeapp', 'locale')
        self.assertEqual(config.registry.getUtility(ITranslationDirectories),
                         [locale])

    def test_add_translation_dirs_registers_chameleon_translate(self):
        from repoze.bfg.interfaces import IChameleonTranslate
        from repoze.bfg.threadlocal import manager
        request = DummyRequest()
        config = self._makeOne()
        manager.push({'request':request, 'registry':config.registry})
        try:
            config.add_translation_dirs('repoze.bfg.tests.localeapp:locale')
            translate = config.registry.getUtility(IChameleonTranslate)
            self.assertEqual(translate('Approve'), u'Approve')
        finally:
            manager.pop()

    def test_add_translation_dirs_abspath(self):
        import os
        from repoze.bfg.interfaces import ITranslationDirectories
        config = self._makeOne()
        here = os.path.dirname(__file__)
        locale = os.path.join(here, 'localeapp', 'locale')
        config.add_translation_dirs(locale)
        self.assertEqual(config.registry.getUtility(ITranslationDirectories),
                         [locale])

    def test__renderer_from_name_default_renderer(self):
        from repoze.bfg.interfaces import IRendererFactory
        config = self._makeOne()
        factory = lambda *arg: 'OK'
        config.registry.registerUtility(factory, IRendererFactory)
        result = config._renderer_from_name(None)
        self.assertEqual(result, 'OK')

    def test_derive_view_function(self):
        def view(request):
            return 'OK'
        config = self._makeOne()
        result = config.derive_view(view)
        self.failIf(result is view)
        self.assertEqual(result(None, None), 'OK')

    def test_derive_view_with_renderer(self):
        def view(request):
            return 'OK'
        config = self._makeOne()
        class moo(object):
            def __init__(self, *arg, **kw):
                pass
            def __call__(self, *arg, **kw):
                return 'moo'
        config.add_renderer('moo', moo)
        result = config.derive_view(view, renderer='moo')
        self.failIf(result is view)
        self.assertEqual(result(None, None).body, 'moo')

    def test_derive_view_class_without_attr(self):
        class View(object):
            def __init__(self, request):
                pass
            def __call__(self):
                return 'OK'
        config = self._makeOne()
        result = config.derive_view(View)
        self.assertEqual(result(None, None), 'OK')

    def test_derive_view_class_with_attr(self):
        class View(object):
            def __init__(self, request):
                pass
            def another(self):
                return 'OK'
        config = self._makeOne()
        result = config.derive_view(View, attr='another')
        self.assertEqual(result(None, None), 'OK')

    def test__derive_view_as_function_context_and_request(self):
        def view(context, request):
            return 'OK'
        config = self._makeOne()
        result = config._derive_view(view)
        self.failUnless(result is view)
        self.failIf(hasattr(result, '__call_permissive__'))
        self.assertEqual(view(None, None), 'OK')
        
    def test__derive_view_as_function_requestonly(self):
        def view(request):
            return 'OK'
        config = self._makeOne()
        result = config._derive_view(view)
        self.failIf(result is view)
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        self.assertEqual(view.__name__, result.__name__)
        self.failIf(hasattr(result, '__call_permissive__'))
        self.assertEqual(result(None, None), 'OK')

    def test__derive_view_as_newstyle_class_context_and_request(self):
        class view(object):
            def __init__(self, context, request):
                pass
            def __call__(self):
                return 'OK'
        config = self._makeOne()
        result = config._derive_view(view)
        self.failIf(result is view)
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        self.assertEqual(view.__name__, result.__name__)
        self.failIf(hasattr(result, '__call_permissive__'))
        self.assertEqual(result(None, None), 'OK')
        
    def test__derive_view_as_newstyle_class_requestonly(self):
        class view(object):
            def __init__(self, context, request):
                pass
            def __call__(self):
                return 'OK'
        config = self._makeOne()
        result = config._derive_view(view)
        self.failIf(result is view)
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        self.assertEqual(view.__name__, result.__name__)
        self.failIf(hasattr(result, '__call_permissive__'))
        self.assertEqual(result(None, None), 'OK')

    def test__derive_view_as_oldstyle_class_context_and_request(self):
        class view:
            def __init__(self, context, request):
                pass
            def __call__(self):
                return 'OK'
        config = self._makeOne()
        result = config._derive_view(view)
        self.failIf(result is view)
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        self.assertEqual(view.__name__, result.__name__)
        self.failIf(hasattr(result, '__call_permissive__'))
        self.assertEqual(result(None, None), 'OK')
        
    def test__derive_view_as_oldstyle_class_requestonly(self):
        class view:
            def __init__(self, context, request):
                pass
            def __call__(self):
                return 'OK'
        config = self._makeOne()
        result = config._derive_view(view)
        self.failIf(result is view)
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        self.assertEqual(view.__name__, result.__name__)
        self.failIf(hasattr(result, '__call_permissive__'))
        self.assertEqual(result(None, None), 'OK')

    def test__derive_view_as_instance_context_and_request(self):
        class View:
            def __call__(self, context, request):
                return 'OK'
        view = View()
        config = self._makeOne()
        result = config._derive_view(view)
        self.failUnless(result is view)
        self.failIf(hasattr(result, '__call_permissive__'))
        self.assertEqual(result(None, None), 'OK')
        
    def test__derive_view_as_instance_requestonly(self):
        class View:
            def __call__(self, request):
                return 'OK'
        view = View()
        config = self._makeOne()
        result = config._derive_view(view)
        self.failIf(result is view)
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        self.failUnless('instance' in result.__name__)
        self.failIf(hasattr(result, '__call_permissive__'))
        self.assertEqual(result(None, None), 'OK')

    def test__derive_view_with_debug_authorization_no_authpol(self):
        view = lambda *arg: 'OK'
        config = self._makeOne()
        self._registerSettings(config,
                               debug_authorization=True, reload_templates=True)
        logger = self._registerLogger(config)
        result = config._derive_view(view, permission='view')
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        self.assertEqual(view.__name__, result.__name__)
        self.failIf(hasattr(result, '__call_permissive__'))
        request = self._makeRequest(config)
        request.view_name = 'view_name'
        request.url = 'url'
        self.assertEqual(result(None, request), 'OK')
        self.assertEqual(len(logger.messages), 1)
        self.assertEqual(logger.messages[0],
                         "debug_authorization of url url (view name "
                         "'view_name' against context None): Allowed "
                         "(no authorization policy in use)")

    def test__derive_view_with_debug_authorization_no_permission(self):
        view = lambda *arg: 'OK'
        config = self._makeOne()
        self._registerSettings(config,
                               debug_authorization=True, reload_templates=True)
        self._registerSecurityPolicy(config, True)
        logger = self._registerLogger(config)
        result = config._derive_view(view)
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        self.assertEqual(view.__name__, result.__name__)
        self.failIf(hasattr(result, '__call_permissive__'))
        request = self._makeRequest(config)
        request.view_name = 'view_name'
        request.url = 'url'
        self.assertEqual(result(None, request), 'OK')
        self.assertEqual(len(logger.messages), 1)
        self.assertEqual(logger.messages[0],
                         "debug_authorization of url url (view name "
                         "'view_name' against context None): Allowed ("
                         "no permission registered)")

    def test__derive_view_debug_auth_permission_authpol_permitted(self):
        view = lambda *arg: 'OK'
        config = self._makeOne()
        self._registerSettings(config, debug_authorization=True,
                               reload_templates=True)
        logger = self._registerLogger(config)
        self._registerSecurityPolicy(config, True)
        result = config._derive_view(view, permission='view')
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        self.assertEqual(view.__name__, result.__name__)
        self.assertEqual(result.__call_permissive__, view)
        request = self._makeRequest(config)
        request.view_name = 'view_name'
        request.url = 'url'
        self.assertEqual(result(None, request), 'OK')
        self.assertEqual(len(logger.messages), 1)
        self.assertEqual(logger.messages[0],
                         "debug_authorization of url url (view name "
                         "'view_name' against context None): True")
        
    def test__derive_view_debug_auth_permission_authpol_denied(self):
        from repoze.bfg.exceptions import Forbidden
        view = lambda *arg: 'OK'
        config = self._makeOne()
        self._registerSettings(config,
                               debug_authorization=True, reload_templates=True)
        logger = self._registerLogger(config)
        self._registerSecurityPolicy(config, False)
        result = config._derive_view(view, permission='view')
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        self.assertEqual(view.__name__, result.__name__)
        self.assertEqual(result.__call_permissive__, view)
        request = self._makeRequest(config)
        request.view_name = 'view_name'
        request.url = 'url'
        self.assertRaises(Forbidden, result, None, request)
        self.assertEqual(len(logger.messages), 1)
        self.assertEqual(logger.messages[0],
                         "debug_authorization of url url (view name "
                         "'view_name' against context None): False")

    def test__derive_view_debug_auth_permission_authpol_denied2(self):
        view = lambda *arg: 'OK'
        config = self._makeOne()
        self._registerSettings(config,
                               debug_authorization=True, reload_templates=True)
        self._registerLogger(config)
        self._registerSecurityPolicy(config, False)
        result = config._derive_view(view, permission='view')
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        self.assertEqual(view.__name__, result.__name__)
        request = self._makeRequest(config)
        request.view_name = 'view_name'
        request.url = 'url'
        permitted = result.__permitted__(None, None)
        self.assertEqual(permitted, False)

    def test__derive_view_with_predicates_all(self):
        view = lambda *arg: 'OK'
        predicates = []
        def predicate1(context, request):
            predicates.append(True)
            return True
        def predicate2(context, request):
            predicates.append(True)
            return True
        config = self._makeOne()
        result = config._derive_view(view, predicates=[predicate1, predicate2])
        request = self._makeRequest(config)
        request.method = 'POST'
        next = result(None, None)
        self.assertEqual(next, 'OK')
        self.assertEqual(predicates, [True, True])

    def test__derive_view_with_predicates_checker(self):
        view = lambda *arg: 'OK'
        predicates = []
        def predicate1(context, request):
            predicates.append(True)
            return True
        def predicate2(context, request):
            predicates.append(True)
            return True
        config = self._makeOne()
        result = config._derive_view(view, predicates=[predicate1, predicate2])
        request = self._makeRequest(config)
        request.method = 'POST'
        next = result.__predicated__(None, None)
        self.assertEqual(next, True)
        self.assertEqual(predicates, [True, True])

    def test__derive_view_with_predicates_notall(self):
        from repoze.bfg.exceptions import NotFound
        view = lambda *arg: 'OK'
        predicates = []
        def predicate1(context, request):
            predicates.append(True)
            return True
        def predicate2(context, request):
            predicates.append(True)
            return False
        config = self._makeOne()
        result = config._derive_view(view, predicates=[predicate1, predicate2])
        request = self._makeRequest(config)
        request.method = 'POST'
        self.assertRaises(NotFound, result, None, None)
        self.assertEqual(predicates, [True, True])

    def test__derive_view_with_wrapper_viewname(self):
        from webob import Response
        from repoze.bfg.interfaces import IView
        from repoze.bfg.interfaces import IViewClassifier
        inner_response = Response('OK')
        def inner_view(context, request):
            return inner_response
        def outer_view(context, request):
            self.assertEqual(request.wrapped_response, inner_response)
            self.assertEqual(request.wrapped_body, inner_response.body)
            self.assertEqual(request.wrapped_view, inner_view)
            return Response('outer ' + request.wrapped_body)
        config = self._makeOne()
        config.registry.registerAdapter(
            outer_view, (IViewClassifier, None, None), IView, 'owrap')
        result = config._derive_view(inner_view, viewname='inner',
                                    wrapper_viewname='owrap')
        self.failIf(result is inner_view)
        self.assertEqual(inner_view.__module__, result.__module__)
        self.assertEqual(inner_view.__doc__, result.__doc__)
        request = self._makeRequest(config)
        request.registry = config.registry
        response = result(None, request)
        self.assertEqual(response.body, 'outer OK')

    def test__derive_view_with_wrapper_viewname_notfound(self):
        from webob import Response
        inner_response = Response('OK')
        def inner_view(context, request):
            return inner_response
        config = self._makeOne()
        request = self._makeRequest(config)
        request.registry = config.registry
        wrapped = config._derive_view(
            inner_view, viewname='inner', wrapper_viewname='owrap')
        self.assertRaises(ValueError, wrapped, None, request)

    def test_override_resource_samename(self):
        from repoze.bfg.exceptions import ConfigurationError
        config = self._makeOne()
        self.assertRaises(ConfigurationError, config.override_resource,'a', 'a')

    def test_override_resource_directory_with_file(self):
        from repoze.bfg.exceptions import ConfigurationError
        config = self._makeOne()
        self.assertRaises(ConfigurationError, config.override_resource,
                          'a:foo/', 'a:foo.pt')

    def test_override_resource_file_with_directory(self):
        from repoze.bfg.exceptions import ConfigurationError
        config = self._makeOne()
        self.assertRaises(ConfigurationError, config.override_resource,
                          'a:foo.pt', 'a:foo/')

    def test_override_resource_success(self):
        config = self._makeOne()
        override = DummyUnderOverride()
        config.override_resource(
            'repoze.bfg.tests.fixtureapp:templates/foo.pt',
            'repoze.bfg.tests.fixtureapp.subpackage:templates/bar.pt',
            _override=override)
        from repoze.bfg.tests import fixtureapp
        from repoze.bfg.tests.fixtureapp import subpackage
        self.assertEqual(override.package, fixtureapp)
        self.assertEqual(override.path, 'templates/foo.pt')
        self.assertEqual(override.override_package, subpackage)
        self.assertEqual(override.override_prefix, 'templates/bar.pt')

    def test_add_renderer(self):
        from repoze.bfg.interfaces import IRendererFactory
        config = self._makeOne()
        renderer = object()
        config.add_renderer('name', renderer)
        self.assertEqual(config.registry.getUtility(IRendererFactory, 'name'),
                         renderer)

    def test_scan_integration(self):
        from zope.interface import alsoProvides
        from repoze.bfg.interfaces import IRequest
        from repoze.bfg.view import render_view_to_response
        import repoze.bfg.tests.grokkedapp as package
        config = self._makeOne()
        config.scan(package)

        ctx = DummyContext()
        req = DummyRequest()
        alsoProvides(req, IRequest)
        req.registry = config.registry

        req.method = 'GET'
        result = render_view_to_response(ctx, req, '')
        self.assertEqual(result, 'grokked')

        req.method = 'POST'
        result = render_view_to_response(ctx, req, '')
        self.assertEqual(result, 'grokked_post')

        result= render_view_to_response(ctx, req, 'grokked_class')
        self.assertEqual(result, 'grokked_class')

        result= render_view_to_response(ctx, req, 'grokked_instance')
        self.assertEqual(result, 'grokked_instance')

        result= render_view_to_response(ctx, req, 'oldstyle_grokked_class')
        self.assertEqual(result, 'oldstyle_grokked_class')

        req.method = 'GET'
        result = render_view_to_response(ctx, req, 'another')
        self.assertEqual(result, 'another_grokked')

        req.method = 'POST'
        result = render_view_to_response(ctx, req, 'another')
        self.assertEqual(result, 'another_grokked_post')

        result= render_view_to_response(ctx, req, 'another_grokked_class')
        self.assertEqual(result, 'another_grokked_class')

        result= render_view_to_response(ctx, req, 'another_grokked_instance')
        self.assertEqual(result, 'another_grokked_instance')

        result= render_view_to_response(ctx, req,
                                        'another_oldstyle_grokked_class')
        self.assertEqual(result, 'another_oldstyle_grokked_class')

        result = render_view_to_response(ctx, req, 'stacked1')
        self.assertEqual(result, 'stacked')

        result = render_view_to_response(ctx, req, 'stacked2')
        self.assertEqual(result, 'stacked')

        result = render_view_to_response(ctx, req, 'another_stacked1')
        self.assertEqual(result, 'another_stacked')

        result = render_view_to_response(ctx, req, 'another_stacked2')
        self.assertEqual(result, 'another_stacked')

        result = render_view_to_response(ctx, req, 'stacked_class1')
        self.assertEqual(result, 'stacked_class')

        result = render_view_to_response(ctx, req, 'stacked_class2')
        self.assertEqual(result, 'stacked_class')

        result = render_view_to_response(ctx, req, 'another_stacked_class1')
        self.assertEqual(result, 'another_stacked_class')

        result = render_view_to_response(ctx, req, 'another_stacked_class2')
        self.assertEqual(result, 'another_stacked_class')

        self.assertRaises(TypeError,
                          render_view_to_response, ctx, req, 'basemethod')

        result = render_view_to_response(ctx, req, 'method1')
        self.assertEqual(result, 'method1')

        result = render_view_to_response(ctx, req, 'method2')
        self.assertEqual(result, 'method2')

        result = render_view_to_response(ctx, req, 'stacked_method1')
        self.assertEqual(result, 'stacked_method')

        result = render_view_to_response(ctx, req, 'stacked_method2')
        self.assertEqual(result, 'stacked_method')
        
        result = render_view_to_response(ctx, req, 'subpackage_init')
        self.assertEqual(result, 'subpackage_init')
        
        result = render_view_to_response(ctx, req, 'subpackage_notinit')
        self.assertEqual(result, 'subpackage_notinit')

        result = render_view_to_response(ctx, req, 'subsubpackage_init')
        self.assertEqual(result, 'subsubpackage_init')

        result = render_view_to_response(ctx, req, 'pod_notinit')
        self.assertEqual(result, None)

    def test_testing_securitypolicy(self):
        from repoze.bfg.testing import DummySecurityPolicy
        config = self._makeOne()
        config.testing_securitypolicy('user', ('group1', 'group2'),
                                      permissive=False)
        from repoze.bfg.interfaces import IAuthenticationPolicy
        from repoze.bfg.interfaces import IAuthorizationPolicy
        ut = config.registry.getUtility(IAuthenticationPolicy)
        self.failUnless(isinstance(ut, DummySecurityPolicy))
        ut = config.registry.getUtility(IAuthorizationPolicy)
        self.assertEqual(ut.userid, 'user')
        self.assertEqual(ut.groupids, ('group1', 'group2'))
        self.assertEqual(ut.permissive, False)

    def test_testing_models(self):
        from repoze.bfg.traversal import find_model
        from repoze.bfg.interfaces import ITraverser
        ob1 = object()
        ob2 = object()
        models = {'/ob1':ob1, '/ob2':ob2}
        config = self._makeOne()
        config.testing_models(models)
        adapter = config.registry.getAdapter(None, ITraverser)
        result = adapter({'PATH_INFO':'/ob1'})
        self.assertEqual(result['context'], ob1)
        self.assertEqual(result['view_name'], '')
        self.assertEqual(result['subpath'], ())
        self.assertEqual(result['traversed'], (u'ob1',))
        self.assertEqual(result['virtual_root'], ob1)
        self.assertEqual(result['virtual_root_path'], ())
        result = adapter({'PATH_INFO':'/ob2'})
        self.assertEqual(result['context'], ob2)
        self.assertEqual(result['view_name'], '')
        self.assertEqual(result['subpath'], ())
        self.assertEqual(result['traversed'], (u'ob2',))
        self.assertEqual(result['virtual_root'], ob2)
        self.assertEqual(result['virtual_root_path'], ())
        self.assertRaises(KeyError, adapter, {'PATH_INFO':'/ob3'})
        try:
            config.begin()
            self.assertEqual(find_model(None, '/ob1'), ob1)
        finally:
            config.end()

    def test_testing_add_subscriber_single(self):
        config = self._makeOne()
        L = config.testing_add_subscriber(IDummy)
        event = DummyEvent()
        config.registry.notify(event)
        self.assertEqual(len(L), 1)
        self.assertEqual(L[0], event)
        config.registry.notify(object())
        self.assertEqual(len(L), 1)

    def test_testing_add_subscriber_multiple(self):
        config = self._makeOne()
        L = config.testing_add_subscriber((Interface, IDummy))
        event = DummyEvent()
        event.object = 'foo'
        # the below is the equivalent of z.c.event.objectEventNotify(event)
        config.registry.subscribers((event.object, event), None)
        self.assertEqual(len(L), 2)
        self.assertEqual(L[0], 'foo')
        self.assertEqual(L[1], event)
        
    def test_testing_add_subscriber_defaults(self):
        config = self._makeOne()
        L = config.testing_add_subscriber()
        event = object()
        config.registry.notify(event)
        self.assertEqual(L[-1], event)
        event2 = object()
        config.registry.notify(event2)
        self.assertEqual(L[-1], event2)

    def test_hook_zca(self):
        from repoze.bfg.threadlocal import get_current_registry
        gsm = DummyGetSiteManager()
        config = self._makeOne()
        config.hook_zca(getSiteManager=gsm)
        self.assertEqual(gsm.hook, get_current_registry)
        
    def test_unhook_zca(self):
        gsm = DummyGetSiteManager()
        config = self._makeOne()
        config.unhook_zca(getSiteManager=gsm)
        self.assertEqual(gsm.unhooked, True)



class Test__map_view(unittest.TestCase):
    def setUp(self):
        from repoze.bfg.registry import Registry
        self.registry = Registry()

    def tearDown(self):
        del self.registry
        
    def _registerRenderer(self, name='.txt'):
        from repoze.bfg.interfaces import IRendererFactory
        from repoze.bfg.interfaces import ITemplateRenderer
        from zope.interface import implements
        class Renderer:
            implements(ITemplateRenderer)
            def __init__(self, path):
                self.__class__.path = path
            def __call__(self, *arg):
                return 'Hello!'
        self.registry.registerUtility(Renderer, IRendererFactory, name=name)
        return Renderer(name)

    def _makeRequest(self):
        request = DummyRequest()
        request.registry = self.registry
        return request

    def _callFUT(self, *arg, **kw):
        from repoze.bfg.configuration import _map_view
        return _map_view(*arg, **kw)
    
    def test__map_view_as_function_context_and_request(self):
        def view(context, request):
            return 'OK'
        result = self._callFUT(view)
        self.failUnless(result is view)
        self.assertEqual(result(None, None), 'OK')

    def test__map_view_as_function_with_attr(self):
        def view(context, request):
            """ """
        result = self._callFUT(view, attr='__name__')
        self.failIf(result is view)
        self.assertRaises(TypeError, result, None, None)

    def test__map_view_as_function_with_attr_and_renderer(self):
        renderer = self._registerRenderer()
        view = lambda *arg: 'OK'
        result = self._callFUT(view, attr='__name__', renderer=renderer)
        self.failIf(result is view)
        self.assertRaises(TypeError, result, None, None)
        
    def test__map_view_as_function_requestonly(self):
        def view(request):
            return 'OK'
        result = self._callFUT(view)
        self.failIf(result is view)
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        self.assertEqual(view.__name__, result.__name__)
        self.assertEqual(result(None, None), 'OK')

    def test__map_view_as_function_requestonly_with_attr(self):
        def view(request):
            """ """
        result = self._callFUT(view, attr='__name__')
        self.failIf(result is view)
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        self.assertEqual(view.__name__, result.__name__)
        self.assertRaises(TypeError, result, None, None)

    def test__map_view_as_newstyle_class_context_and_request(self):
        class view(object):
            def __init__(self, context, request):
                pass
            def __call__(self):
                return 'OK'
        result = self._callFUT(view)
        self.failIf(result is view)
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        self.assertEqual(view.__name__, result.__name__)
        self.assertEqual(result(None, None), 'OK')

    def test__map_view_as_newstyle_class_context_and_request_with_attr(self):
        class view(object):
            def __init__(self, context, request):
                pass
            def index(self):
                return 'OK'
        result = self._callFUT(view, attr='index')
        self.failIf(result is view)
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        self.assertEqual(view.__name__, result.__name__)
        self.assertEqual(result(None, None), 'OK')

    def test__map_view_as_newstyle_class_context_and_request_attr_and_renderer(
        self):
        renderer = self._registerRenderer()
        class view(object):
            def __init__(self, context, request):
                pass
            def index(self):
                return {'a':'1'}
        result = self._callFUT(view, attr='index', renderer = renderer)
        self.failIf(result is view)
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        self.assertEqual(view.__name__, result.__name__)
        request = self._makeRequest()
        self.assertEqual(result(None, request).body, 'Hello!')
        
    def test__map_view_as_newstyle_class_requestonly(self):
        class view(object):
            def __init__(self, request):
                pass
            def __call__(self):
                return 'OK'
        result = self._callFUT(view)
        self.failIf(result is view)
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        self.assertEqual(view.__name__, result.__name__)
        self.assertEqual(result(None, None), 'OK')

    def test__map_view_as_newstyle_class_requestonly_with_attr(self):
        class view(object):
            def __init__(self, request):
                pass
            def index(self):
                return 'OK'
        result = self._callFUT(view, attr='index')
        self.failIf(result is view)
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        self.assertEqual(view.__name__, result.__name__)
        self.assertEqual(result(None, None), 'OK')

    def test__map_view_as_newstyle_class_requestonly_attr_and_renderer(self):
        renderer = self._registerRenderer()
        class view(object):
            def __init__(self, request):
                pass
            def index(self):
                return {'a':'1'}
        result = self._callFUT(view, attr='index', renderer = renderer)
        self.failIf(result is view)
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        self.assertEqual(view.__name__, result.__name__)
        request = self._makeRequest()
        self.assertEqual(result(None, request).body, 'Hello!')

    def test__map_view_as_oldstyle_class_context_and_request(self):
        class view:
            def __init__(self, context, request):
                pass
            def __call__(self):
                return 'OK'
        result = self._callFUT(view)
        self.failIf(result is view)
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        self.assertEqual(view.__name__, result.__name__)
        self.assertEqual(result(None, None), 'OK')

    def test__map_view_as_oldstyle_class_context_and_request_with_attr(self):
        class view:
            def __init__(self, context, request):
                pass
            def index(self):
                return 'OK'
        result = self._callFUT(view, attr='index')
        self.failIf(result is view)
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        self.assertEqual(view.__name__, result.__name__)
        self.assertEqual(result(None, None), 'OK')

    def test__map_view_as_oldstyle_cls_context_request_attr_and_renderer(self):
        renderer = self._registerRenderer()
        class view:
            def __init__(self, context, request):
                pass
            def index(self):
                return {'a':'1'}
        result = self._callFUT(view, attr='index', renderer = renderer)
        self.failIf(result is view)
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        self.assertEqual(view.__name__, result.__name__)
        request = self._makeRequest()
        self.assertEqual(result(None, request).body, 'Hello!')

    def test__map_view_as_oldstyle_class_requestonly(self):
        class view:
            def __init__(self, request):
                pass
            def __call__(self):
                return 'OK'
        result = self._callFUT(view)
        self.failIf(result is view)
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        self.assertEqual(view.__name__, result.__name__)
        self.assertEqual(result(None, None), 'OK')

    def test__map_view_as_oldstyle_class_requestonly_with_attr(self):
        class view:
            def __init__(self, request):
                pass
            def index(self):
                return 'OK'
        result = self._callFUT(view, attr='index')
        self.failIf(result is view)
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        self.assertEqual(view.__name__, result.__name__)
        self.assertEqual(result(None, None), 'OK')

    def test__map_view_as_oldstyle_class_requestonly_attr_and_renderer(self):
        renderer = self._registerRenderer()
        class view:
            def __init__(self, request):
                pass
            def index(self):
                return {'a':'1'}
        result = self._callFUT(view, attr='index', renderer = renderer)
        self.failIf(result is view)
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        self.assertEqual(view.__name__, result.__name__)
        request = self._makeRequest()
        self.assertEqual(result(None, request).body, 'Hello!')

    def test__map_view_as_instance_context_and_request(self):
        class View:
            def __call__(self, context, request):
                return 'OK'
        view = View()
        result = self._callFUT(view)
        self.failUnless(result is view)
        self.assertEqual(result(None, None), 'OK')
        
    def test__map_view_as_instance_context_and_request_and_attr(self):
        class View:
            def index(self, context, request):
                return 'OK'
        view = View()
        result = self._callFUT(view, attr='index')
        self.failIf(result is view)
        self.assertEqual(result(None, None), 'OK')

    def test__map_view_as_instance_context_and_request_attr_and_renderer(self):
        renderer = self._registerRenderer()
        class View:
            def index(self, context, request):
                return {'a':'1'}
        view = View()
        result = self._callFUT(view, attr='index', renderer=renderer)
        self.failIf(result is view)
        request = self._makeRequest()
        self.assertEqual(result(None, request).body, 'Hello!')

    def test__map_view_as_instance_requestonly(self):
        class View:
            def __call__(self, request):
                return 'OK'
        view = View()
        result = self._callFUT(view)
        self.failIf(result is view)
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        self.failUnless('instance' in result.__name__)
        self.assertEqual(result(None, None), 'OK')

    def test__map_view_as_instance_requestonly_with_attr(self):
        class View:
            def index(self, request):
                return 'OK'
        view = View()
        result = self._callFUT(view, attr='index')
        self.failIf(result is view)
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        self.failUnless('instance' in result.__name__)
        self.assertEqual(result(None, None), 'OK')

    def test__map_view_as_instance_requestonly_with_attr_and_renderer(self):
        renderer = self._registerRenderer()
        class View:
            def index(self, request):
                return {'a':'1'}
        view = View()
        result = self._callFUT(view, attr='index', renderer = renderer)
        self.failIf(result is view)
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        self.failUnless('instance' in result.__name__)
        request = self._makeRequest()
        self.assertEqual(result(None, request).body, 'Hello!')

    def test__map_view_rendereronly(self):
        renderer = self._registerRenderer()
        def view(context, request):
            return {'a':'1'}
        result = self._callFUT(view, renderer=renderer)
        self.failIf(result is view)
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        request = self._makeRequest()
        self.assertEqual(result(None, request).body, 'Hello!')

class Test_rendered_response(unittest.TestCase):
    def setUp(self):
        testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _callFUT(self, renderer, response, view=None,
                 context=None, request=None, renderer_name=None):
        from repoze.bfg.configuration import rendered_response
        if request is None:
            request = DummyRequest()
        return rendered_response(renderer, response, view,
                                 context, request, renderer_name)

    def _makeRenderer(self):
        def renderer(*arg):
            return 'Hello!'
        return renderer

    def test_is_response(self):
        renderer = self._makeRenderer()
        response = DummyResponse()
        result = self._callFUT(renderer, response)
        self.assertEqual(result, response)

    def test_calls_renderer(self):
        renderer = self._makeRenderer()
        response = {'a':'1'}
        result = self._callFUT(renderer, response)
        self.assertEqual(result.body, 'Hello!')

    def test_with_content_type(self):
        renderer = self._makeRenderer()
        response = {'a':'1'}
        request = DummyRequest()
        attrs = {'response_content_type':'text/nonsense'}
        request.__dict__.update(attrs)
        result = self._callFUT(renderer, response, request=request)
        self.assertEqual(result.content_type, 'text/nonsense')

    def test_with_headerlist(self):
        renderer = self._makeRenderer()
        response = {'a':'1'}
        request = DummyRequest()
        attrs = {'response_headerlist':[('a', '1'), ('b', '2')]}
        request.__dict__.update(attrs)
        result = self._callFUT(renderer, response, request=request)
        self.assertEqual(result.headerlist,
                         [('Content-Type', 'text/html; charset=UTF-8'),
                          ('Content-Length', '6'),
                          ('a', '1'),
                          ('b', '2')])

    def test_with_status(self):
        renderer = self._makeRenderer()
        response = {'a':'1'}
        request = DummyRequest()
        attrs = {'response_status':'406 You Lose'}
        request.__dict__.update(attrs)
        result = self._callFUT(renderer, response, request=request)
        self.assertEqual(result.status, '406 You Lose')

    def test_with_charset(self):
        renderer = self._makeRenderer()
        response = {'a':'1'}
        request = DummyRequest()
        attrs = {'response_charset':'UTF-16'}
        request.__dict__.update(attrs)
        result = self._callFUT(renderer, response, request=request)
        self.assertEqual(result.charset, 'UTF-16')

    def test_with_cache_for(self):
        renderer = self._makeRenderer()
        response = {'a':'1'}
        request = DummyRequest()
        attrs = {'response_cache_for':100}
        request.__dict__.update(attrs)
        result = self._callFUT(renderer, response, request=request)
        self.assertEqual(result.cache_control.max_age, 100)

    def test_with_real_request(self):
        # functional
        from repoze.bfg.request import Request
        renderer = self._makeRenderer()
        response = {'a':'1'}
        request = Request({})
        request.response_status = '406 You Lose'
        result = self._callFUT(renderer, response, request=request)
        self.assertEqual(result.status, '406 You Lose')

class Test_decorate_view(unittest.TestCase):
    def _callFUT(self, wrapped, original):
        from repoze.bfg.configuration import decorate_view
        return decorate_view(wrapped, original)
    
    def test_it_same(self):
        def view(context, request):
            """ """
        result = self._callFUT(view, view)
        self.assertEqual(result, False)

    def test_it_different(self):
        class DummyView1:
            """ 1 """
            __name__ = '1'
            __module__ = '1'
            def __call__(self, context, request):
                """ """
            def __call_permissive__(self, context, reuqest):
                """ """
            def __predicated__(self, context, reuqest):
                """ """
            def __permitted__(self, context, request):
                """ """
        class DummyView2:
            """ 2 """
            __name__ = '2'
            __module__ = '2'
            def __call__(self, context, request):
                """ """
            def __call_permissive__(self, context, reuqest):
                """ """
            def __predicated__(self, context, reuqest):
                """ """
            def __permitted__(self, context, request):
                """ """
        view1 = DummyView1()
        view2 = DummyView2()
        result = self._callFUT(view1, view2)
        self.assertEqual(result, True)
        self.failUnless(view1.__doc__ is view2.__doc__)
        self.failUnless(view1.__module__ is view2.__module__)
        self.failUnless(view1.__name__ is view2.__name__)
        self.failUnless(view1.__call_permissive__.im_func is
                        view2.__call_permissive__.im_func)
        self.failUnless(view1.__permitted__.im_func is
                        view2.__permitted__.im_func)
        self.failUnless(view1.__predicated__.im_func is
                        view2.__predicated__.im_func)

class Test__make_predicates(unittest.TestCase):
    def _callFUT(self, **kw):
        from repoze.bfg.configuration import _make_predicates
        return _make_predicates(**kw)

    def test_ordering_xhr_and_request_method_trump_only_containment(self):
        order1, _, _ = self._callFUT(xhr=True, request_method='GET')
        order2, _, _ = self._callFUT(containment=True)
        self.failUnless(order1 < order2)

    def test_ordering_number_of_predicates(self):
        order1, _, _ = self._callFUT(
            xhr='xhr',
            request_method='request_method',
            path_info='path_info',
            request_param='param',
            header='header',
            accept='accept',
            containment='containment',
            request_type='request_type',
            custom=('a',)
            )
        order2, _, _ = self._callFUT(
            xhr='xhr',
            request_method='request_method',
            path_info='path_info',
            request_param='param',
            header='header',
            accept='accept',
            containment='containment',
            request_type='request_type',
            custom=('a',)
            )
        order3, _, _ = self._callFUT(
            xhr='xhr',
            request_method='request_method',
            path_info='path_info',
            request_param='param',
            header='header',
            accept='accept',
            containment='containment',
            request_type='request_type',
            ) 
        order4, _, _ = self._callFUT(
            xhr='xhr',
            request_method='request_method',
            path_info='path_info',
            request_param='param',
            header='header',
            accept='accept',
            containment='containment',
            )
        order5, _, _ = self._callFUT(
            xhr='xhr',
            request_method='request_method',
            path_info='path_info',
            request_param='param',
            header='header',
            accept='accept',
            )
        order6, _, _ = self._callFUT(
            xhr='xhr',
            request_method='request_method',
            path_info='path_info',
            request_param='param',
            header='header',
            )
        order7, _, _ = self._callFUT(
            xhr='xhr',
            request_method='request_method',
            path_info='path_info',
            request_param='param',
            )
        order8, _, _ = self._callFUT(
            xhr='xhr',
            request_method='request_method',
            path_info='path_info',
            )
        order9, _, _ = self._callFUT(
            xhr='xhr',
            request_method='request_method',
            )
        order10, _, _ = self._callFUT(
            xhr='xhr',
            )
        order11, _, _ = self._callFUT(
            )
        self.assertEqual(order1, order2)
        self.failUnless(order3 > order2)
        self.failUnless(order4 > order3)
        self.failUnless(order5 > order4)
        self.failUnless(order6 > order5)
        self.failUnless(order7 > order6)
        self.failUnless(order8 > order7)
        self.failUnless(order9 > order8)
        self.failUnless(order10 > order9)
        self.failUnless(order11 > order10)

    def test_ordering_importance_of_predicates(self):
        order1, _, _ = self._callFUT(
            xhr='xhr',
            )
        order2, _, _ = self._callFUT(
            request_method='request_method',
            )
        order3, _, _ = self._callFUT(
            path_info='path_info',
            ) 
        order4, _, _ = self._callFUT(
            request_param='param',
            )
        order5, _, _ = self._callFUT(
            header='header',
            )
        order6, _, _ = self._callFUT(
            accept='accept',
            )
        order7, _, _ = self._callFUT(
            containment='containment',
            )
        order8, _, _ = self._callFUT(
            request_type='request_type',
            )
        order9, _, _ = self._callFUT(
            custom=('a',),
            )
        self.failUnless(order1 > order2)
        self.failUnless(order2 > order3)
        self.failUnless(order3 > order4)
        self.failUnless(order4 > order5)
        self.failUnless(order5 > order6)
        self.failUnless(order6 > order7)
        self.failUnless(order7 > order8)
        self.failUnless(order8 > order9)

    def test_ordering_importance_and_number(self):
        order1, _, _ = self._callFUT(
            xhr='xhr',
            request_method='request_method',
            )
        order2, _, _ = self._callFUT(
            custom=('a',),
            )
        self.failUnless(order1 < order2)

        order1, _, _ = self._callFUT(
            xhr='xhr',
            request_method='request_method',
            )
        order2, _, _ = self._callFUT(
            request_method='request_method',
            custom=('a',),
            )
        self.failUnless(order1 > order2)

        order1, _, _ = self._callFUT(
            xhr='xhr',
            request_method='request_method',
            path_info='path_info',
            )
        order2, _, _ = self._callFUT(
            request_method='request_method',
            custom=('a',),
            )
        self.failUnless(order1 < order2)

        order1, _, _ = self._callFUT(
            xhr='xhr',
            request_method='request_method',
            path_info='path_info',
            )
        order2, _, _ = self._callFUT(
            xhr='xhr',
            request_method='request_method',
            custom=('a',),
            )
        self.failUnless(order1 > order2)

class TestMultiView(unittest.TestCase):
    def _getTargetClass(self):
        from repoze.bfg.configuration import MultiView
        return MultiView

    def _makeOne(self, name='name'):
        return self._getTargetClass()(name)
    
    def test_class_implements_ISecuredView(self):
        from zope.interface.verify import verifyClass
        from repoze.bfg.interfaces import ISecuredView
        verifyClass(ISecuredView, self._getTargetClass())

    def test_instance_implements_ISecuredView(self):
        from zope.interface.verify import verifyObject
        from repoze.bfg.interfaces import ISecuredView
        verifyObject(ISecuredView, self._makeOne())

    def test_add(self):
        mv = self._makeOne()
        mv.add('view', 100)
        self.assertEqual(mv.views, [(100, 'view', None)])
        mv.add('view2', 99)
        self.assertEqual(mv.views, [(99, 'view2', None), (100, 'view', None)])
        mv.add('view3', 100, 'text/html')
        self.assertEqual(mv.media_views['text/html'], [(100, 'view3', None)])
        mv.add('view4', 99, 'text/html')
        self.assertEqual(mv.media_views['text/html'],
                         [(99, 'view4', None), (100, 'view3', None)])
        mv.add('view5', 100, 'text/xml')
        self.assertEqual(mv.media_views['text/xml'], [(100, 'view5', None)])
        self.assertEqual(set(mv.accepts), set(['text/xml', 'text/html']))
        self.assertEqual(mv.views, [(99, 'view2', None), (100, 'view', None)])
        mv.add('view6', 98, 'text/*')
        self.assertEqual(mv.views, [(98, 'view6', None),
                                    (99, 'view2', None),
                                    (100, 'view', None)])

    def test_add_with_phash(self):
        mv = self._makeOne()
        mv.add('view', 100, phash='abc')
        self.assertEqual(mv.views, [(100, 'view', 'abc')])
        mv.add('view', 100, phash='abc')
        self.assertEqual(mv.views, [(100, 'view', 'abc')])
        mv.add('view', 100, phash='def')
        self.assertEqual(mv.views, [(100, 'view', 'abc'), (100, 'view', 'def')])
        mv.add('view', 100, phash='abc')
        self.assertEqual(mv.views, [(100, 'view', 'abc'), (100, 'view', 'def')])

    def test_get_views_request_has_no_accept(self):
        request = DummyRequest()
        mv = self._makeOne()
        mv.views = [(99, lambda *arg: None)]
        self.assertEqual(mv.get_views(request), mv.views)

    def test_get_views_no_self_accepts(self):
        request = DummyRequest()
        request.accept = True
        mv = self._makeOne()
        mv.accepts = []
        mv.views = [(99, lambda *arg: None)]
        self.assertEqual(mv.get_views(request), mv.views)

    def test_get_views(self):
        request = DummyRequest()
        request.accept = DummyAccept('text/html')
        mv = self._makeOne()
        mv.accepts = ['text/html']
        mv.views = [(99, lambda *arg: None)]
        html_views = [(98, lambda *arg: None)]
        mv.media_views['text/html'] = html_views
        self.assertEqual(mv.get_views(request), html_views + mv.views)

    def test_get_views_best_match_returns_None(self):
        request = DummyRequest()
        request.accept = DummyAccept(None)
        mv = self._makeOne()
        mv.accepts = ['text/html']
        mv.views = [(99, lambda *arg: None)]
        self.assertEqual(mv.get_views(request), mv.views)

    def test_match_not_found(self):
        from repoze.bfg.exceptions import NotFound
        mv = self._makeOne()
        context = DummyContext()
        request = DummyRequest()
        self.assertRaises(NotFound, mv.match, context, request)

    def test_match_predicate_fails(self):
        from repoze.bfg.exceptions import NotFound
        mv = self._makeOne()
        def view(context, request):
            """ """
        view.__predicated__ = lambda *arg: False
        mv.views = [(100, view, None)]
        context = DummyContext()
        request = DummyRequest()
        self.assertRaises(NotFound, mv.match, context, request)

    def test_match_predicate_succeeds(self):
        mv = self._makeOne()
        def view(context, request):
            """ """
        view.__predicated__ = lambda *arg: True
        mv.views = [(100, view, None)]
        context = DummyContext()
        request = DummyRequest()
        result = mv.match(context, request)
        self.assertEqual(result, view)

    def test_permitted_no_views(self):
        from repoze.bfg.exceptions import NotFound
        mv = self._makeOne()
        context = DummyContext()
        request = DummyRequest()
        self.assertRaises(NotFound, mv.__permitted__, context, request)

    def test_permitted_no_match_with__permitted__(self):
        mv = self._makeOne()
        def view(context, request):
            """ """
        mv.views = [(100, view, None)]
        self.assertEqual(mv.__permitted__(None, None), True)
        
    def test_permitted(self):
        mv = self._makeOne()
        def view(context, request):
            """ """
        def permitted(context, request):
            return False
        view.__permitted__ = permitted
        mv.views = [(100, view, None)]
        context = DummyContext()
        request = DummyRequest()
        result = mv.__permitted__(context, request)
        self.assertEqual(result, False)

    def test__call__not_found(self):
        from repoze.bfg.exceptions import NotFound
        mv = self._makeOne()
        context = DummyContext()
        request = DummyRequest()
        self.assertRaises(NotFound, mv, context, request)

    def test___call__intermediate_not_found(self):
        from repoze.bfg.exceptions import NotFound
        mv = self._makeOne()
        context = DummyContext()
        request = DummyRequest()
        request.view_name = ''
        expected_response = DummyResponse()
        def view1(context, request):
            raise NotFound
        def view2(context, request):
            return expected_response
        mv.views = [(100, view1, None), (99, view2, None)]
        response = mv(context, request)
        self.assertEqual(response, expected_response)

    def test___call__(self):
        mv = self._makeOne()
        context = DummyContext()
        request = DummyRequest()
        request.view_name = ''
        expected_response = DummyResponse()
        def view(context, request):
            return expected_response
        mv.views = [(100, view, None)]
        response = mv(context, request)
        self.assertEqual(response, expected_response)

    def test__call_permissive__not_found(self):
        from repoze.bfg.exceptions import NotFound
        mv = self._makeOne()
        context = DummyContext()
        request = DummyRequest()
        self.assertRaises(NotFound, mv, context, request)

    def test___call_permissive_has_call_permissive(self):
        mv = self._makeOne()
        context = DummyContext()
        request = DummyRequest()
        request.view_name = ''
        expected_response = DummyResponse()
        def view(context, request):
            """ """
        def permissive(context, request):
            return expected_response
        view.__call_permissive__ = permissive
        mv.views = [(100, view, None)]
        response = mv.__call_permissive__(context, request)
        self.assertEqual(response, expected_response)

    def test___call_permissive_has_no_call_permissive(self):
        mv = self._makeOne()
        context = DummyContext()
        request = DummyRequest()
        request.view_name = ''
        expected_response = DummyResponse()
        def view(context, request):
            return expected_response
        mv.views = [(100, view, None)]
        response = mv.__call_permissive__(context, request)
        self.assertEqual(response, expected_response)

    def test__call__with_accept_match(self):
        mv = self._makeOne()
        context = DummyContext()
        request = DummyRequest()
        request.accept = DummyAccept('text/html', 'text/xml')
        expected_response = DummyResponse()
        def view(context, request):
            return expected_response
        mv.views = [(100, None)]
        mv.media_views['text/xml'] = [(100, view, None)]
        mv.accepts = ['text/xml']
        response = mv(context, request)
        self.assertEqual(response, expected_response)

    def test__call__with_accept_miss(self):
        mv = self._makeOne()
        context = DummyContext()
        request = DummyRequest()
        request.accept = DummyAccept('text/plain', 'text/html')
        expected_response = DummyResponse()
        def view(context, request):
            return expected_response
        mv.views = [(100, view, None)]
        mv.media_views['text/xml'] = [(100, None, None)]
        mv.accepts = ['text/xml']
        response = mv(context, request)
        self.assertEqual(response, expected_response)
        

class TestRequestOnly(unittest.TestCase):
    def _callFUT(self, arg):
        from repoze.bfg.configuration import requestonly
        return requestonly(arg)
    
    def test_newstyle_class_no_init(self):
        class foo(object):
            """ """
        self.assertFalse(self._callFUT(foo))

    def test_newstyle_class_init_toomanyargs(self):
        class foo(object):
            def __init__(self, context, request):
                """ """
        self.assertFalse(self._callFUT(foo))
        
    def test_newstyle_class_init_onearg_named_request(self):
        class foo(object):
            def __init__(self, request):
                """ """
        self.assertTrue(self._callFUT(foo))

    def test_newstyle_class_init_onearg_named_somethingelse(self):
        class foo(object):
            def __init__(self, req):
                """ """
        self.assertTrue(self._callFUT(foo))

    def test_newstyle_class_init_defaultargs_firstname_not_request(self):
        class foo(object):
            def __init__(self, context, request=None):
                """ """
        self.assertFalse(self._callFUT(foo))

    def test_newstyle_class_init_defaultargs_firstname_request(self):
        class foo(object):
            def __init__(self, request, foo=1, bar=2):
                """ """
        self.assertTrue(self._callFUT(foo))

    def test_newstyle_class_init_noargs(self):
        class foo(object):
            def __init__():
                """ """
        self.assertFalse(self._callFUT(foo))

    def test_oldstyle_class_no_init(self):
        class foo:
            """ """
        self.assertFalse(self._callFUT(foo))

    def test_oldstyle_class_init_toomanyargs(self):
        class foo:
            def __init__(self, context, request):
                """ """
        self.assertFalse(self._callFUT(foo))
        
    def test_oldstyle_class_init_onearg_named_request(self):
        class foo:
            def __init__(self, request):
                """ """
        self.assertTrue(self._callFUT(foo))

    def test_oldstyle_class_init_onearg_named_somethingelse(self):
        class foo:
            def __init__(self, req):
                """ """
        self.assertTrue(self._callFUT(foo))

    def test_oldstyle_class_init_defaultargs_firstname_not_request(self):
        class foo:
            def __init__(self, context, request=None):
                """ """
        self.assertFalse(self._callFUT(foo))

    def test_oldstyle_class_init_defaultargs_firstname_request(self):
        class foo:
            def __init__(self, request, foo=1, bar=2):
                """ """
        self.assertTrue(self._callFUT(foo), True)

    def test_oldstyle_class_init_noargs(self):
        class foo:
            def __init__():
                """ """
        self.assertFalse(self._callFUT(foo))

    def test_function_toomanyargs(self):
        def foo(context, request):
            """ """
        self.assertFalse(self._callFUT(foo))
        
    def test_function_onearg_named_request(self):
        def foo(request):
            """ """
        self.assertTrue(self._callFUT(foo))

    def test_function_onearg_named_somethingelse(self):
        def foo(req):
            """ """
        self.assertTrue(self._callFUT(foo))

    def test_function_defaultargs_firstname_not_request(self):
        def foo(context, request=None):
            """ """
        self.assertFalse(self._callFUT(foo))

    def test_function_defaultargs_firstname_request(self):
        def foo(request, foo=1, bar=2):
            """ """
        self.assertTrue(self._callFUT(foo))

    def test_function_noargs(self):
        def foo():
            """ """
        self.assertFalse(self._callFUT(foo))

    def test_instance_toomanyargs(self):
        class Foo:
            def __call__(self, context, request):
                """ """
        foo = Foo()
        self.assertFalse(self._callFUT(foo))
        
    def test_instance_defaultargs_onearg_named_request(self):
        class Foo:
            def __call__(self, request):
                """ """
        foo = Foo()
        self.assertTrue(self._callFUT(foo))

    def test_instance_defaultargs_onearg_named_somethingelse(self):
        class Foo:
            def __call__(self, req):
                """ """
        foo = Foo()
        self.assertTrue(self._callFUT(foo))

    def test_instance_defaultargs_firstname_not_request(self):
        class Foo:
            def __call__(self, context, request=None):
                """ """
        foo = Foo()
        self.assertFalse(self._callFUT(foo))

    def test_instance_defaultargs_firstname_request(self):
        class Foo:
            def __call__(self, request, foo=1, bar=2):
                """ """
        foo = Foo()
        self.assertTrue(self._callFUT(foo), True)

    def test_instance_nocall(self):
        class Foo: pass
        foo = Foo()
        self.assertFalse(self._callFUT(foo))

class TestMakeApp(unittest.TestCase):
    def setUp(self):
        testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _callFUT(self, *arg, **kw):
        from repoze.bfg.configuration import make_app
        return make_app(*arg, **kw)

    def test_it(self):
        settings = {'a':1}
        rootfactory = object()
        app = self._callFUT(rootfactory, settings=settings,
                            Configurator=DummyConfigurator)
        self.assertEqual(app.root_factory, rootfactory)
        self.assertEqual(app.settings, settings)
        self.assertEqual(app.zcml_file, 'configure.zcml')
        self.assertEqual(app.zca_hooked, True)

    def test_it_options_means_settings(self):
        settings = {'a':1}
        rootfactory = object()
        app = self._callFUT(rootfactory, options=settings,
                            Configurator=DummyConfigurator)
        self.assertEqual(app.root_factory, rootfactory)
        self.assertEqual(app.settings, settings)
        self.assertEqual(app.zcml_file, 'configure.zcml')

    def test_it_with_package(self):
        package = object()
        rootfactory = object()
        app = self._callFUT(rootfactory, package=package,
                            Configurator=DummyConfigurator)
        self.assertEqual(app.package, package)

    def test_it_with_custom_configure_zcml(self):
        rootfactory = object()
        settings = {'configure_zcml':'2.zcml'}
        app = self._callFUT(rootfactory, filename='1.zcml', settings=settings,
                            Configurator=DummyConfigurator)
        self.assertEqual(app.zcml_file, '2.zcml')

class DummyRequest:
    subpath = ()
    def __init__(self):
        self.environ = {'PATH_INFO':'/static'}
        self.params = {}
        self.cookies = {}
    def copy(self):
        return self
    def get_response(self, app):
        return app

class DummyContext:
    pass

class DummyLock:
    def acquire(self):
        self.acquired = True

    def release(self):
        self.released = True
        
class DummyPackage:
    def __init__(self, name):
        self.__name__ = name

class DummyOverrides:
    def __init__(self, package):
        self.package = package
        self.inserted = []

    def insert(self, path, package, prefix):
        self.inserted.append((path, package, prefix))

class DummyUnderOverride:
    def __call__(self, package, path, override_package, override_prefix,
                 _info=u''):
        self.package = package
        self.path = path
        self.override_package = override_package
        self.override_prefix = override_prefix

from zope.interface import Interface
class IDummy(Interface):
    pass

class IOther(Interface):
    pass

class DummyResponse:
    status = '200 OK'
    headerlist = ()
    app_iter = ()
    body = ''

class DummyLogger:
    def __init__(self):
        self.messages = []
    def info(self, msg):
        self.messages.append(msg)
    warn = info
    debug = info

class DummySecurityPolicy:
    def __init__(self, permitted=True):
        self.permitted = permitted

    def effective_principals(self, request):
        return []

    def permits(self, context, principals, permission):
        return self.permitted

class DummyConfigurator(object):
    def __init__(self, registry=None, package=None, root_factory=None,
                 settings=None):
        self.root_factory = root_factory
        self.package = package
        self.settings = settings

    def begin(self, request=None):
        self.begun = True
        self.request = request

    def end(self):
        self.ended = True

    def load_zcml(self, filename):
        self.zcml_file = filename
    
    def make_wsgi_app(self):
        return self

    def hook_zca(self):
        self.zca_hooked = True
    
class DummyAccept(object):
    def __init__(self, *matches):
        self.matches = list(matches)

    def best_match(self, offered):
        if self.matches:
            for match in self.matches:
                if match in offered:
                    self.matches.remove(match)
                    return match
    def __contains__(self, val):
        return val in self.matches

from zope.interface import implements
from repoze.bfg.interfaces import IMultiView
class DummyMultiView:
    implements(IMultiView)
    def __init__(self):
        self.views = []
        self.name = 'name'
    def add(self, view, order, accept=None, phash=None):
        self.views.append((view, accept, phash))
    def __call__(self, context, request):
        return 'OK1'
    def __permitted__(self, context, request):
        """ """

class DummyGetSiteManager(object):
    def sethook(self, hook):
        self.hook = hook
    def reset(self):
        self.unhooked = True
    
class DummyThreadLocalManager(object):
    pushed = None
    popped = False
    def push(self, d):
        self.pushed = d
    def pop(self):
        self.popped = True

class IFactory(Interface):
    pass

class DummyFactory(object):
    implements(IFactory)
    def __call__(self):
        """ """
        
class DummyEvent:
    implements(IDummy)

