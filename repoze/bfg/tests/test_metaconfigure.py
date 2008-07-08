import unittest

from zope.component.testing import PlacelessSetup

class TestPageDirective(unittest.TestCase, PlacelessSetup):
    def setUp(self):
        PlacelessSetup.setUp(self)

    def tearDown(self):
        PlacelessSetup.tearDown(self)

    def _getFUT(self):
        from repoze.bfg.metaconfigure import page
        return page

    def test_no_class_or_template(self):
        f = self._getFUT()
        from zope.configuration.exceptions import ConfigurationError
        context = DummyContext()
        self.assertRaises(ConfigurationError, f, context, 'repoze.view', None)

    def test_no_such_file(self):
        f = self._getFUT()
        from zope.configuration.exceptions import ConfigurationError
        context = DummyContext()
        self.assertRaises(ConfigurationError, f, context, 'repoze.view', None,
                          template='notthere.pt')

    def test_only_template(self):
        f = self._getFUT()
        context = DummyContext()
        f(context, 'repoze.view', None, template='minimal.pt')
        actions = context.actions
        from repoze.bfg.interfaces import IRequest
        from repoze.bfg.interfaces import IViewFactory
        from zope.component.zcml import handler
        expected0 = ('view', None, '', IRequest, IViewFactory)
        expected1 = handler
        self.assertEqual(actions[0]['discriminator'], expected0)
        self.assertEqual(actions[0]['callable'], expected1)
        self.assertEqual(actions[0]['args'][0], 'registerAdapter')
        import types
        self.failUnless(isinstance(actions[0]['args'][1], types.FunctionType))
        self.assertEqual(actions[0]['args'][2], (None, IRequest))
        self.assertEqual(actions[0]['args'][3], IViewFactory)
        self.assertEqual(actions[0]['args'][4], '')
        self.assertEqual(actions[0]['args'][5], None)

    def test_template_and_class(self):
        f = self._getFUT()
        context = DummyContext()
        f(context, 'repoze.view', None, template='minimal.pt',
          class_=DummyViewClass)
        actions = context.actions
        from repoze.bfg.interfaces import IRequest
        from repoze.bfg.interfaces import IViewFactory
        from zope.component.zcml import handler
        expected0 = ('view', None, '', IRequest, IViewFactory)
        expected1 = handler
        self.assertEqual(actions[0]['discriminator'], expected0)
        self.assertEqual(actions[0]['callable'], expected1)
        self.assertEqual(actions[0]['args'][0], 'registerAdapter')
        import types
        self.failUnless(isinstance(actions[0]['args'][1], types.FunctionType))
        self.assertEqual(actions[0]['args'][2], (None, IRequest))
        self.assertEqual(actions[0]['args'][3], IViewFactory)
        self.assertEqual(actions[0]['args'][4], '')
        self.assertEqual(actions[0]['args'][5], None)

class DummyViewClass:
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


    
