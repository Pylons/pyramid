import unittest

from repoze.bfg.testing import cleanUp

class ConfiguratorTests(unittest.TestCase):
    def _makeOne(self, registry=None):
        from repoze.bfg.registry import Registry
        from repoze.bfg.configuration import Configurator
        if registry is None:
            registry = Registry()
        return Configurator(registry)

    def _registerRenderer(self, config, name='.txt'):
        from repoze.bfg.interfaces import IRendererFactory
        from repoze.bfg.interfaces import ITemplateRenderer
        from zope.interface import implements
        class Renderer:
            implements(ITemplateRenderer)
            def __init__(self, path):
                pass
            def __call__(self, *arg):
                return 'Hello!'
        config.reg.registerUtility(Renderer, IRendererFactory, name=name)

    def test__override_not_yet_registered(self):
        from repoze.bfg.interfaces import IPackageOverrides
        package = DummyPackage('package')
        opackage = DummyPackage('opackage')
        config = self._makeOne()
        config._override(package, 'path', opackage, 'oprefix',
                         PackageOverrides=DummyOverrides)
        overrides = config.reg.queryUtility(IPackageOverrides,
                                            name='package')
        self.assertEqual(overrides.inserted, [('path', 'opackage', 'oprefix')])
        self.assertEqual(overrides.package, package)

    def test__override_already_registered(self):
        from repoze.bfg.interfaces import IPackageOverrides
        package = DummyPackage('package')
        opackage = DummyPackage('opackage')
        overrides = DummyOverrides(package)
        config = self._makeOne()
        config.reg.registerUtility(overrides, IPackageOverrides,
                                   name='package')
        config._override(package, 'path', opackage, 'oprefix',
                         PackageOverrides=DummyOverrides)
        self.assertEqual(overrides.inserted, [('path', 'opackage', 'oprefix')])
        self.assertEqual(overrides.package, package)

    def test_map_view_as_function_context_and_request(self):
        def view(context, request):
            return 'OK'
        config = self._makeOne()
        result = config.map_view(view)
        self.failUnless(result is view)
        self.assertEqual(result(None, None), 'OK')

    def test_map_view_as_function_with_attr(self):
        def view(context, request):
            """ """
        config = self._makeOne()
        result = config.map_view(view, attr='__name__')
        self.failIf(result is view)
        self.assertRaises(TypeError, result, None, None)

    def test_map_view_as_function_with_attr_and_renderer(self):
        config = self._makeOne()
        self._registerRenderer(config)
        def view(context, request):
            """ """
        result = config.map_view(view, attr='__name__',
                                 renderer_name='fixtures/minimal.txt')
        self.failIf(result is view)
        self.assertRaises(TypeError, result, None, None)
        
    def test_map_view_as_function_requestonly(self):
        config = self._makeOne()
        def view(request):
            return 'OK'
        result = config.map_view(view)
        self.failIf(result is view)
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        self.assertEqual(view.__name__, result.__name__)
        self.assertEqual(result(None, None), 'OK')

    def test_map_view_as_function_requestonly_with_attr(self):
        config = self._makeOne()
        def view(request):
            """ """
        result = config.map_view(view, attr='__name__')
        self.failIf(result is view)
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        self.assertEqual(view.__name__, result.__name__)
        self.assertRaises(TypeError, result, None, None)

    def test_map_view_as_newstyle_class_context_and_request(self):
        config = self._makeOne()
        class view(object):
            def __init__(self, context, request):
                pass
            def __call__(self):
                return 'OK'
        result = config.map_view(view)
        self.failIf(result is view)
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        self.assertEqual(view.__name__, result.__name__)
        self.assertEqual(result(None, None), 'OK')

    def test_map_view_as_newstyle_class_context_and_request_with_attr(self):
        config = self._makeOne()
        class view(object):
            def __init__(self, context, request):
                pass
            def index(self):
                return 'OK'
        result = config.map_view(view, attr='index')
        self.failIf(result is view)
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        self.assertEqual(view.__name__, result.__name__)
        self.assertEqual(result(None, None), 'OK')

    def test_map_view_as_newstyle_class_context_and_request_attr_and_renderer(
        self):
        config = self._makeOne()
        self._registerRenderer(config)
        class view(object):
            def __init__(self, context, request):
                pass
            def index(self):
                return {'a':'1'}
        result = config.map_view(
            view, attr='index',
            renderer_name='repoze.bfg.tests:fixtures/minimal.txt')
        self.failIf(result is view)
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        self.assertEqual(view.__name__, result.__name__)
        request = DummyRequest()
        self.assertEqual(result(None, request).body, 'Hello!')
        
    def test_map_view_as_newstyle_class_requestonly(self):
        config = self._makeOne()
        class view(object):
            def __init__(self, request):
                pass
            def __call__(self):
                return 'OK'
        result = config.map_view(view)
        self.failIf(result is view)
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        self.assertEqual(view.__name__, result.__name__)
        self.assertEqual(result(None, None), 'OK')

    def test_map_view_as_newstyle_class_requestonly_with_attr(self):
        config = self._makeOne()
        class view(object):
            def __init__(self, request):
                pass
            def index(self):
                return 'OK'
        result = config.map_view(view, attr='index')
        self.failIf(result is view)
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        self.assertEqual(view.__name__, result.__name__)
        self.assertEqual(result(None, None), 'OK')

    def test_map_view_as_newstyle_class_requestonly_with_attr_and_renderer(
        self):
        config = self._makeOne()
        self._registerRenderer(config)
        class view(object):
            def __init__(self, request):
                pass
            def index(self):
                return {'a':'1'}
        result = config.map_view(
            view, attr='index',
            renderer_name='repoze.bfg.tests:fixtures/minimal.txt')
        self.failIf(result is view)
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        self.assertEqual(view.__name__, result.__name__)
        request = DummyRequest()
        self.assertEqual(result(None, request).body, 'Hello!')

    def test_map_view_as_oldstyle_class_context_and_request(self):
        config = self._makeOne()
        class view:
            def __init__(self, context, request):
                pass
            def __call__(self):
                return 'OK'
        result = config.map_view(view)
        self.failIf(result is view)
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        self.assertEqual(view.__name__, result.__name__)
        self.assertEqual(result(None, None), 'OK')

    def test_map_view_as_oldstyle_class_context_and_request_with_attr(self):
        config = self._makeOne()
        class view:
            def __init__(self, context, request):
                pass
            def index(self):
                return 'OK'
        result = config.map_view(view, attr='index')
        self.failIf(result is view)
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        self.assertEqual(view.__name__, result.__name__)
        self.assertEqual(result(None, None), 'OK')

    def test_map_view_as_oldstyle_class_context_and_request_attr_and_renderer(
        self):
        config = self._makeOne()
        self._registerRenderer(config)
        class view:
            def __init__(self, context, request):
                pass
            def index(self):
                return {'a':'1'}
        result = config.map_view(
            view, attr='index',
            renderer_name='repoze.bfg.tests:fixtures/minimal.txt')
        self.failIf(result is view)
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        self.assertEqual(view.__name__, result.__name__)
        request = DummyRequest()
        self.assertEqual(result(None, request).body, 'Hello!')

    def test_map_view_as_oldstyle_class_requestonly(self):
        config = self._makeOne()
        class view:
            def __init__(self, request):
                pass
            def __call__(self):
                return 'OK'
        result = config.map_view(view)
        self.failIf(result is view)
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        self.assertEqual(view.__name__, result.__name__)
        self.assertEqual(result(None, None), 'OK')

    def test_map_view_as_oldstyle_class_requestonly_with_attr(self):
        config = self._makeOne()
        class view:
            def __init__(self, request):
                pass
            def index(self):
                return 'OK'
        result = config.map_view(view, attr='index')
        self.failIf(result is view)
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        self.assertEqual(view.__name__, result.__name__)
        self.assertEqual(result(None, None), 'OK')

    def test_map_view_as_oldstyle_class_requestonly_attr_and_renderer(self):
        config = self._makeOne()
        self._registerRenderer(config)
        class view:
            def __init__(self, request):
                pass
            def index(self):
                return {'a':'1'}
        result = config.map_view(
            view, attr='index',
            renderer_name='repoze.bfg.tests:fixtures/minimal.txt')
        self.failIf(result is view)
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        self.assertEqual(view.__name__, result.__name__)
        request = DummyRequest()
        self.assertEqual(result(None, request).body, 'Hello!')

    def test_map_view_as_instance_context_and_request(self):
        config = self._makeOne()
        class View:
            def __call__(self, context, request):
                return 'OK'
        view = View()
        result = config.map_view(view)
        self.failUnless(result is view)
        self.assertEqual(result(None, None), 'OK')
        
    def test_map_view_as_instance_context_and_request_and_attr(self):
        config = self._makeOne()
        class View:
            def index(self, context, request):
                return 'OK'
        view = View()
        result = config.map_view(view, attr='index')
        self.failIf(result is view)
        self.assertEqual(result(None, None), 'OK')

    def test_map_view_as_instance_context_and_request_attr_and_renderer(self):
        config = self._makeOne()
        self._registerRenderer(config)
        class View:
            def index(self, context, request):
                return {'a':'1'}
        view = View()
        result = config.map_view(
            view, attr='index',
            renderer_name='repoze.bfg.tests:fixtures/minimal.txt')
        self.failIf(result is view)
        request = DummyRequest()
        self.assertEqual(result(None, request).body, 'Hello!')

    def test_map_view_as_instance_requestonly(self):
        config = self._makeOne()
        class View:
            def __call__(self, request):
                return 'OK'
        view = View()
        result = config.map_view(view)
        self.failIf(result is view)
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        self.failUnless('instance' in result.__name__)
        self.assertEqual(result(None, None), 'OK')

    def test_map_view_as_instance_requestonly_with_attr(self):
        config = self._makeOne()
        class View:
            def index(self, request):
                return 'OK'
        view = View()
        result = config.map_view(view, attr='index')
        self.failIf(result is view)
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        self.failUnless('instance' in result.__name__)
        self.assertEqual(result(None, None), 'OK')

    def test_map_view_as_instance_requestonly_with_attr_and_renderer(self):
        config = self._makeOne()
        self._registerRenderer(config)
        class View:
            def index(self, request):
                return {'a':'1'}
        view = View()
        result = config.map_view(
            view, attr='index',
            renderer_name='repoze.bfg.tests:fixtures/minimal.txt')
        self.failIf(result is view)
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        self.failUnless('instance' in result.__name__)
        request = DummyRequest()
        self.assertEqual(result(None, request).body, 'Hello!')

    def test_map_view_rendereronly(self):
        config = self._makeOne()
        self._registerRenderer(config)
        def view(context, request):
            return {'a':'1'}
        result = config.map_view(
            view,
            renderer_name='repoze.bfg.tests:fixtures/minimal.txt')
        self.failIf(result is view)
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        request = DummyRequest()
        self.assertEqual(result(None, request).body, 'Hello!')

    def test_map_view_defaultrendereronly(self):
        config = self._makeOne()
        self._registerRenderer(config, name='')
        def view(context, request):
            return {'a':'1'}
        result = config.map_view(view)
        self.failIf(result is view)
        self.assertEqual(view.__module__, result.__module__)
        self.assertEqual(view.__doc__, result.__doc__)
        request = DummyRequest()
        self.assertEqual(result(None, request).body, 'Hello!')

    def _callDefaultConfiguration(self, *arg, **kw):
        inst = self._makeOne()
        inst.default_configuration(*arg, **kw)
        return inst.reg

    def test_default_config_fixtureapp_default_filename_withpackage(self):
        manager = DummyRegistryManager()
        from repoze.bfg.tests import fixtureapp
        rootfactory = DummyRootFactory(None)
        registry = self._callDefaultConfiguration(rootfactory, fixtureapp)
        from repoze.bfg.tests.fixtureapp.models import IFixture
        self.failUnless(registry.queryUtility(IFixture)) # only in c.zcml

    def test_default_config_fixtureapp_explicit_filename(self):
        manager = DummyRegistryManager()
        from repoze.bfg.tests import fixtureapp
        rootfactory = DummyRootFactory(None)
        registry = self._callDefaultConfiguration(
            rootfactory, fixtureapp, filename='another.zcml',
            manager=manager)
        from repoze.bfg.tests.fixtureapp.models import IFixture
        self.failIf(registry.queryUtility(IFixture)) # only in c.zcml

    def test_default_config_fixtureapp_explicit_filename_in_settings(self):
        import os
        manager = DummyRegistryManager()
        rootfactory = DummyRootFactory(None)
        from repoze.bfg.tests import fixtureapp
        zcmlfile = os.path.join(os.path.dirname(fixtureapp.__file__),
                                'another.zcml')
        registry = self._callDefaultConfiguration(
            rootfactory, fixtureapp, filename='configure.zcml',
            settings={'configure_zcml':zcmlfile},
            manager=manager)
        from repoze.bfg.tests.fixtureapp.models import IFixture
        self.failIf(registry.queryUtility(IFixture)) # only in c.zcml

    def test_default_config_fixtureapp_explicit_specification_in_settings(self):
        manager = DummyRegistryManager()
        rootfactory = DummyRootFactory(None)
        from repoze.bfg.tests import fixtureapp
        zcmlfile = 'repoze.bfg.tests.fixtureapp.subpackage:yetanother.zcml'
        registry = self._callDefaultConfiguration(
            rootfactory, fixtureapp, filename='configure.zcml',
            settings={'configure_zcml':zcmlfile},
            manager=manager)
        from repoze.bfg.tests.fixtureapp.models import IFixture
        self.failIf(registry.queryUtility(IFixture)) # only in c.zcml

    def test_default_config_fixtureapp_filename_hascolon_isabs(self):
        manager = DummyRegistryManager()
        rootfactory = DummyRootFactory(None)
        from repoze.bfg.tests import fixtureapp
        zcmlfile = 'repoze.bfg.tests.fixtureapp.subpackage:yetanother.zcml'
        class Dummy:
            def isabs(self, name):
                return True
        os = Dummy()
        os.path = Dummy()
        self.assertRaises(IOError, self._callDefaultConfiguration,
                          rootfactory,
                          fixtureapp,
                          filename='configure.zcml',
                          settings={'configure_zcml':zcmlfile},
                          manager=manager,
                          os=os)
        
    def test_default_config_custom_settings(self):
        manager = DummyRegistryManager()
        settings = {'mysetting':True}
        from repoze.bfg.tests import fixtureapp
        rootfactory = DummyRootFactory(None)
        registry = self._callDefaultConfiguration(
            rootfactory, fixtureapp, settings=settings,
            manager=manager)
        from repoze.bfg.interfaces import ISettings
        settings = registry.getUtility(ISettings)
        self.assertEqual(settings.reload_templates, False)
        self.assertEqual(settings.debug_authorization, False)
        self.assertEqual(settings.mysetting, True)

    def test_default_config_registrations(self):
        manager = DummyRegistryManager()
        settings = {'reload_templates':True,
                    'debug_authorization':True}
        from repoze.bfg.tests import fixtureapp
        rootfactory = DummyRootFactory(None)
        registry = self._callDefaultConfiguration(
            rootfactory, fixtureapp, settings=settings,
            manager=manager)
        from repoze.bfg.interfaces import ISettings
        from repoze.bfg.interfaces import ILogger
        from repoze.bfg.interfaces import IRootFactory
        settings = registry.getUtility(ISettings)
        logger = registry.getUtility(ILogger, name='repoze.bfg.debug')
        rootfactory = registry.getUtility(IRootFactory)
        self.assertEqual(logger.name, 'repoze.bfg.debug')
        self.assertEqual(settings.reload_templates, True)
        self.assertEqual(settings.debug_authorization, True)
        self.assertEqual(rootfactory, rootfactory)
        self.failUnless(manager.pushed and manager.popped)

    def test_default_config_routes_in_config(self):
        from repoze.bfg.interfaces import ISettings
        from repoze.bfg.interfaces import ILogger
        from repoze.bfg.interfaces import IRootFactory
        from repoze.bfg.interfaces import IRoutesMapper
        settings = {'reload_templates':True,
                    'debug_authorization':True}
        from repoze.bfg.tests import routesapp
        rootfactory = DummyRootFactory(None)
        registry = self._callDefaultConfiguration(
            rootfactory, routesapp, settings=settings)
        settings = registry.getUtility(ISettings)
        logger = registry.getUtility(ILogger, name='repoze.bfg.debug')
        self.assertEqual(registry.getUtility(IRootFactory), rootfactory)
        self.failUnless(registry.getUtility(IRoutesMapper))

    def test_default_config_lock_and_unlock(self):
        from repoze.bfg.tests import fixtureapp
        rootfactory = DummyRootFactory(None)
        dummylock = DummyLock()
        registry = self._callDefaultConfiguration(
            rootfactory, fixtureapp, filename='configure.zcml',
            lock=dummylock)
        self.assertEqual(dummylock.acquired, True)
        self.assertEqual(dummylock.released, True)

class TestBFGViewGrokker(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _getTargetClass(self):
        from repoze.bfg.configuration import BFGViewGrokker
        return BFGViewGrokker

    def _makeOne(self, *arg, **kw):
        return self._getTargetClass()(*arg, **kw)

    def test_grok_is_bfg_view(self):
        from zope.component import getSiteManager
        from repoze.bfg.interfaces import IRequest
        from repoze.bfg.interfaces import IView
        from zope.interface import Interface
        from repoze.bfg.configuration import Configurator
        grokker = self._makeOne()
        class obj:
            def __init__(self, context, request):
                pass
            def __call__(self):
                return 'OK'
        settings = dict(permission='foo', for_=Interface, name='foo.html',
                        request_type=IRequest, route_name=None,
                        request_method=None, request_param=None,
                        containment=None, attr=None, renderer=None,
                        wrapper=None, xhr=False, header=None,
                        accept=None)
        obj.__bfg_view_settings__ = [settings]
        sm = getSiteManager()
        config = Configurator(sm)
        result = grokker.grok('name', obj, _info='', _configurator=config)
        self.assertEqual(result, True)
        wrapped = sm.adapters.lookup((Interface, IRequest), IView,
                                     name='foo.html')
        self.assertEqual(wrapped(None, None), 'OK')

    def test_grok_is_not_bfg_view(self):
        grokker = self._makeOne()
        class obj:
            pass
        context = DummyContext()
        result = grokker.grok('name', obj)
        self.assertEqual(result, False)

class TestDefaultRootFactory(unittest.TestCase):
    def _getTargetClass(self):
        from repoze.bfg.configuration import DefaultRootFactory
        return DefaultRootFactory

    def _makeOne(self, environ):
        return self._getTargetClass()(environ)

    def test_no_matchdict(self):
        environ = {}
        root = self._makeOne(environ)
        self.assertEqual(root.__parent__, None)
        self.assertEqual(root.__name__, None)

    def test_matchdict(self):
        class DummyRequest:
            pass
        request = DummyRequest()
        request.matchdict = {'a':1, 'b':2}
        root = self._makeOne(request)
        self.assertEqual(root.a, 1)
        self.assertEqual(root.b, 2)

    

class DummyRequest:
    pass

class DummyRegistryManager:
    def push(self, registry):
        from repoze.bfg.threadlocal import manager
        manager.push(registry)
        self.pushed = True

    def pop(self):
        from repoze.bfg.threadlocal import manager
        manager.pop()
        self.popped = True

class DummyRootFactory:
    def __init__(self, root):
        self.root = root

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

