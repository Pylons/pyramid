import unittest

from zope.component.testing import PlacelessSetup

class TestViewDirective(unittest.TestCase, PlacelessSetup):
    def setUp(self):
        PlacelessSetup.setUp(self)

    def tearDown(self):
        PlacelessSetup.tearDown(self)

    def _getFUT(self):
        from repoze.bfg.zcml import view
        return view

    def test_no_view(self):
        f = self._getFUT()
        from zope.configuration.exceptions import ConfigurationError
        context = DummyContext()
        self.assertRaises(ConfigurationError, f, context, 'repoze.view', None)

    def test_only_view(self):
        f = self._getFUT()
        context = DummyContext()
        class IFoo:
            pass
        def view(context, request):
            pass
        f(context, 'repoze.view', IFoo, view=view)
        actions = context.actions
        from repoze.bfg.interfaces import IRequest
        from repoze.bfg.interfaces import IView
        from repoze.bfg.interfaces import IViewPermission
        from repoze.bfg.security import ViewPermissionFactory
        from zope.component.zcml import handler
        from zope.component.interface import provideInterface

        self.assertEqual(len(actions), 3)

        provide = actions[0]
        self.assertEqual(provide['discriminator'], None)
        self.assertEqual(provide['callable'], provideInterface)
        self.assertEqual(provide['args'][0], '')
        self.assertEqual(provide['args'][1], IFoo)

        permission = actions[1]
        permission_discriminator = ('permission', IFoo, '', IRequest,
                                    IViewPermission)
        self.assertEqual(permission['discriminator'], permission_discriminator)
        self.assertEqual(permission['callable'], handler)
        self.assertEqual(permission['args'][0], 'registerAdapter')
        self.failUnless(isinstance(permission['args'][1],ViewPermissionFactory))
        self.assertEqual(permission['args'][1].permission_name, 'repoze.view')
        self.assertEqual(permission['args'][2], (IFoo, IRequest))
        self.assertEqual(permission['args'][3], IViewPermission)
        self.assertEqual(permission['args'][4], '')
        self.assertEqual(permission['args'][5], None)
        
        regadapt = actions[2]
        regadapt_discriminator = ('view', IFoo, '', IRequest, IView)
        self.assertEqual(regadapt['discriminator'], regadapt_discriminator)
        self.assertEqual(regadapt['callable'], handler)
        self.assertEqual(regadapt['args'][0], 'registerAdapter')
        self.assertEqual(regadapt['args'][1], view)
        self.assertEqual(regadapt['args'][2], (IFoo, IRequest))
        self.assertEqual(regadapt['args'][3], IView)
        self.assertEqual(regadapt['args'][4], '')
        self.assertEqual(regadapt['args'][5], None)

    def test_request_type(self):
        f = self._getFUT()
        context = DummyContext()
        class IFoo:
            pass
        def view(context, request):
            pass
        f(context, 'repoze.view', IFoo, view=view, request_type=IDummy)
        actions = context.actions
        from repoze.bfg.interfaces import IView
        from repoze.bfg.interfaces import IViewPermission
        from repoze.bfg.security import ViewPermissionFactory
        from zope.component.zcml import handler
        from zope.component.interface import provideInterface

        self.assertEqual(len(actions), 3)

        provide = actions[0]
        self.assertEqual(provide['discriminator'], None)
        self.assertEqual(provide['callable'], provideInterface)
        self.assertEqual(provide['args'][0], '')
        self.assertEqual(provide['args'][1], IFoo)

        permission = actions[1]
        permission_discriminator = ('permission', IFoo, '', IDummy,
                                    IViewPermission)
        self.assertEqual(permission['discriminator'], permission_discriminator)
        self.assertEqual(permission['callable'], handler)
        self.assertEqual(permission['args'][0], 'registerAdapter')
        self.failUnless(isinstance(permission['args'][1],ViewPermissionFactory))
        self.assertEqual(permission['args'][1].permission_name, 'repoze.view')
        self.assertEqual(permission['args'][2], (IFoo, IDummy))
        self.assertEqual(permission['args'][3], IViewPermission)
        self.assertEqual(permission['args'][4], '')
        self.assertEqual(permission['args'][5], None)
        
        regadapt = actions[2]
        regadapt_discriminator = ('view', IFoo, '', IDummy, IView)
        self.assertEqual(regadapt['discriminator'], regadapt_discriminator)
        self.assertEqual(regadapt['callable'], handler)
        self.assertEqual(regadapt['args'][0], 'registerAdapter')
        self.assertEqual(regadapt['args'][1], view)
        self.assertEqual(regadapt['args'][2], (IFoo, IDummy))
        self.assertEqual(regadapt['args'][3], IView)
        self.assertEqual(regadapt['args'][4], '')
        self.assertEqual(regadapt['args'][5], None)

class TestSettingsDirective(unittest.TestCase, PlacelessSetup):
    def setUp(self):
        PlacelessSetup.setUp(self)

    def tearDown(self):
        PlacelessSetup.tearDown(self)

    def _getFUT(self):
        from repoze.bfg.zcml import settings
        return settings

    def test_defaults(self):
        context = DummyContext()
        settings = self._getFUT()
        settings(context)
        actions = context.actions
        from repoze.bfg.interfaces import ISettings
        from zope.component.zcml import handler
        self.assertEqual(len(actions), 1)
        action = actions[0]
        self.assertEqual(action['discriminator'], ('settings', ISettings))
        self.assertEqual(action['callable'], handler)
        self.assertEqual(len(action['args']), 5)
        self.assertEqual(action['args'][0], 'registerUtility')
        settings = action['args'][1]
        self.assertEqual(settings.reload_templates, False)
        self.failUnless(ISettings.providedBy(settings), settings)
        self.assertEqual(action['args'][2], ISettings)
        self.assertEqual(action['args'][3], '')
        self.assertEqual(action['args'][4], context.info)

class TestSampleApp(unittest.TestCase, PlacelessSetup):
    def setUp(self):
        PlacelessSetup.setUp(self)

    def tearDown(self):
        PlacelessSetup.tearDown(self)

    def test_registry_actions_can_be_pickled_and_unpickled(self):
        import repoze.bfg.sampleapp as package
        from zope.configuration import config
        from zope.configuration import xmlconfig
        context = config.ConfigurationMachine()
        xmlconfig.registerCommonDirectives(context)
        context.package = package
        xmlconfig.include(context, 'configure.zcml', package)
        context.execute_actions(clear=False)
        actions = context.actions
        import cPickle
        dumped = cPickle.dumps(actions, -1)
        new = cPickle.loads(dumped)
        self.assertEqual(len(actions), len(new))

class Dummy:
    pass

class DummyContext:
    def __init__(self):
        self.actions = []
        self.info = None

    def path(self, name):
        import os
        here = os.path.dirname(__file__)
        fixtures = os.path.join(here, 'fixtures')
        return os.path.join(fixtures, name)

    def action(self, discriminator, callable, args):
        self.actions.append(
            {'discriminator':discriminator,
             'callable':callable,
             'args':args}
            )

from zope.interface import Interface
class IDummy(Interface):
    pass

    
