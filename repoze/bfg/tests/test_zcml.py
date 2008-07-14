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

    def test_template_and_factory(self):
        f = self._getFUT()
        context = DummyContext()
        from zope.configuration.exceptions import ConfigurationError
        self.assertRaises(ConfigurationError, f, context, 'repoze.view',
                          None, factory=object, template='minimal.pt')

class TestTemplateOnlyViewFactory(unittest.TestCase):
    def _getTargetClass(self):
        from repoze.bfg.zcml import TemplateOnlyViewFactory
        return TemplateOnlyViewFactory

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
        from repoze.bfg.zcml import TemplateOnlyView
        self.failUnless(isinstance(view, TemplateOnlyView))
        self.assertEqual(view.template, template)

class TemplateOnlyViewTests(unittest.TestCase, PlacelessSetup):
    def setUp(self):
        PlacelessSetup.setUp(self)

    def tearDown(self):
        PlacelessSetup.tearDown(self)

    def _getTargetClass(self):
        from repoze.bfg.zcml import TemplateOnlyView
        return TemplateOnlyView

    def _zcmlConfigure(self):
        import repoze.bfg
        import zope.configuration.xmlconfig
        zope.configuration.xmlconfig.file('configure.zcml', package=repoze.bfg)

    def _getTemplatePath(self, name):
        import os
        here = os.path.abspath(os.path.dirname(__file__))
        return os.path.join(here, 'fixtures', name)

    def _makeOne(self, *arg, **kw):
        klass = self._getTargetClass()
        return klass(*arg, **kw)

    def test_call(self):
        self._zcmlConfigure()
        view = self._makeOne(None, None)
        view.template = self._getTemplatePath('minimal.pt')
        result = view(foo='foo')
        from webob import Response
        self.failUnless(isinstance(result, Response))
        self.assertEqual(result.app_iter, ['<div>\n</div>'])
        self.assertEqual(result.status, '200 OK')
        self.assertEqual(len(result.headerlist), 2)
        
    def test_call_no_template(self):
        self._zcmlConfigure()
        view = self._makeOne(None, None)
        self.assertRaises(ValueError, view)

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


    
