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
        class IFoo:
            pass
        f(context, 'repoze.view', IFoo, template='minimal.pt')
        actions = context.actions
        from repoze.bfg.interfaces import IView
        from repoze.bfg.interfaces import IRequest
        from repoze.bfg.interfaces import IViewFactory
        from zope.component.zcml import handler
        from zope.component.interface import provideInterface

        self.assertEqual(len(actions), 3)

        regutil_discriminator = ('utility', IView, context.path('minimal.pt'))
        regutil = actions[0]
        self.assertEqual(regutil['discriminator'], regutil_discriminator)
        self.assertEqual(regutil['callable'], handler)
        self.assertEqual(regutil['args'][0], 'registerUtility')
        self.assertEqual(regutil['args'][1].template.filename,
                         context.path('minimal.pt'))
        self.assertEqual(regutil['args'][2], IView)
        self.assertEqual(regutil['args'][3], context.path('minimal.pt'))

        provide = actions[1]
        self.assertEqual(provide['discriminator'], None)
        self.assertEqual(provide['callable'], provideInterface)
        self.assertEqual(provide['args'][0], '')
        self.assertEqual(provide['args'][1], IFoo)
        
        regadapt = actions[2]
        regadapt_discriminator = ('view', IFoo, '', IRequest, IViewFactory)
        self.assertEqual(regadapt['discriminator'], regadapt_discriminator)
        self.assertEqual(regadapt['callable'], handler)
        self.assertEqual(regadapt['args'][0], 'registerAdapter')
        self.assertEqual(regadapt['args'][1].template,
                         context.path('minimal.pt'))
        self.assertEqual(regadapt['args'][2], (IFoo, IRequest))
        self.assertEqual(regadapt['args'][3], IViewFactory)
        self.assertEqual(regadapt['args'][4], '')
        self.assertEqual(regadapt['args'][5], None)

    def test_only_factory(self):
        f = self._getFUT()
        context = DummyContext()
        class IFoo:
            pass
        f(context, 'repoze.view', IFoo, factory=Dummy)
        actions = context.actions
        from repoze.bfg.interfaces import IRequest
        from repoze.bfg.interfaces import IViewFactory
        from zope.component.zcml import handler
        from zope.component.interface import provideInterface

        self.assertEqual(len(actions), 2)

        provide = actions[0]
        self.assertEqual(provide['discriminator'], None)
        self.assertEqual(provide['callable'], provideInterface)
        self.assertEqual(provide['args'][0], '')
        self.assertEqual(provide['args'][1], IFoo)
        
        regadapt = actions[1]
        regadapt_discriminator = ('view', IFoo, '', IRequest, IViewFactory)
        self.assertEqual(regadapt['discriminator'], regadapt_discriminator)
        self.assertEqual(regadapt['callable'], handler)
        self.assertEqual(regadapt['args'][0], 'registerAdapter')
        self.assertEqual(regadapt['args'][1], Dummy)
        self.assertEqual(regadapt['args'][2], (IFoo, IRequest))
        self.assertEqual(regadapt['args'][3], IViewFactory)
        self.assertEqual(regadapt['args'][4], '')
        self.assertEqual(regadapt['args'][5], None)

    def test_template_and_factory_raises(self):
        f = self._getFUT()
        context = DummyContext()
        from zope.configuration.exceptions import ConfigurationError
        self.assertRaises(ConfigurationError, f, context, 'repoze.view', None,
                          Dummy, 'minimal.html', 'minimal.pt')

class TestTemplateViewFactory(unittest.TestCase):
    def _getTargetClass(self):
        from repoze.bfg.zcml import TemplateViewFactory
        return TemplateViewFactory

    def _makeOne(self, template):
        return self._getTargetClass()(template)

    def test_instance_conforms_to_IViewFactory(self):
        from zope.interface.verify import verifyObject
        from repoze.bfg.interfaces import IViewFactory
        verifyObject(IViewFactory, self._makeOne('a'))

    def test_call(self):
        context = DummyContext()
        template = context.path('minimal.pt')
        factory = self._makeOne(template)
        view = factory(None, None)
        from repoze.bfg.view import TemplateView
        self.failUnless(isinstance(view, TemplateView))
        

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


    
