import unittest

from zope.component.testing import PlacelessSetup

class Base(PlacelessSetup):
    def setUp(self):
        PlacelessSetup.setUp(self)

    def tearDown(self):
        PlacelessSetup.tearDown(self)

    def _zcmlConfigure(self):
        import repoze.bfg
        import zope.configuration.xmlconfig
        zope.configuration.xmlconfig.file('configure.zcml', package=repoze.bfg)

    def _getTemplatePath(self, name):
        import os
        here = os.path.abspath(os.path.dirname(__file__))
        return os.path.join(here, 'fixtures', name)
        
class Z3CPTTemplateFactoryTests(unittest.TestCase, Base):
    def setUp(self):
        Base.setUp(self)

    def tearDown(self):
        Base.tearDown(self)

    def _getTargetClass(self):
        from repoze.bfg.template import Z3CPTTemplateFactory
        return Z3CPTTemplateFactory

    def _makeOne(self, *arg, **kw):
        klass = self._getTargetClass()
        return klass(*arg, **kw)

    def test_instance_implements_ITemplate(self):
        from zope.interface.verify import verifyObject
        from repoze.bfg.interfaces import ITemplate
        path = self._getTemplatePath('minimal.pt')
        verifyObject(ITemplate, self._makeOne(path))

    def test_class_implements_ITemplate(self):
        from zope.interface.verify import verifyClass
        from repoze.bfg.interfaces import ITemplate
        verifyClass(ITemplate, self._getTargetClass())

    def test_call(self):
        self._zcmlConfigure()
        minimal = self._getTemplatePath('minimal.pt')
        instance = self._makeOne(minimal)
        result = instance()
        self.failUnless(isinstance(result, str))
        self.assertEqual(result, '<div>\n</div>')

class RenderTemplateTests(unittest.TestCase, Base):
    def setUp(self):
        Base.setUp(self)

    def tearDown(self):
        Base.tearDown(self)

    def _getFUT(self):
        from repoze.bfg.template import render_template
        return render_template

    def test_nonabs_unregistered(self):
        self._zcmlConfigure()
        from zope.component import queryUtility
        from repoze.bfg.interfaces import ITemplate
        minimal = self._getTemplatePath('minimal.pt')
        self.assertEqual(queryUtility(ITemplate, minimal), None)
        render = self._getFUT()
        result = render(minimal)
        self.failUnless(isinstance(result, str))
        self.assertEqual(result, '<div>\n</div>')
        from repoze.bfg.template import Z3CPTTemplateFactory
        self.failUnless(isinstance(queryUtility(ITemplate, minimal),
                                   Z3CPTTemplateFactory))

    def test_nonabs_registered(self):
        self._zcmlConfigure()
        from zope.component import getGlobalSiteManager
        from zope.component import queryUtility
        from repoze.bfg.template import Z3CPTTemplateFactory
        from repoze.bfg.interfaces import ITemplate
        minimal = self._getTemplatePath('minimal.pt')
        utility = Z3CPTTemplateFactory(minimal)
        gsm = getGlobalSiteManager()
        gsm.registerUtility(utility, ITemplate, name=minimal)
        render = self._getFUT()
        result = render(minimal)
        self.failUnless(isinstance(result, str))
        self.assertEqual(result, '<div>\n</div>')
        self.assertEqual(queryUtility(ITemplate, minimal), utility)

class RenderTemplateToResponseTests(unittest.TestCase, Base):
    def setUp(self):
        Base.setUp(self)

    def tearDown(self):
        Base.tearDown(self)

    def _getFUT(self):
        from repoze.bfg.template import render_template_to_response
        return render_template_to_response

    def test_nonabs_unregistered(self):
        self._zcmlConfigure()
        from zope.component import queryUtility
        from repoze.bfg.interfaces import ITemplate
        minimal = self._getTemplatePath('minimal.pt')
        self.assertEqual(queryUtility(ITemplate, minimal), None)
        render = self._getFUT()
        result = render(minimal)
        from webob import Response
        self.failUnless(isinstance(result, Response))
        self.assertEqual(result.app_iter, ['<div>\n</div>'])
        self.assertEqual(result.status, '200 OK')
        self.assertEqual(len(result.headerlist), 2)
        from repoze.bfg.template import Z3CPTTemplateFactory
        self.failUnless(isinstance(queryUtility(ITemplate, minimal),
                                   Z3CPTTemplateFactory))

    def test_nonabs_registered(self):
        self._zcmlConfigure()
        from zope.component import getGlobalSiteManager
        from zope.component import queryUtility
        from repoze.bfg.template import Z3CPTTemplateFactory
        from repoze.bfg.interfaces import ITemplate
        minimal = self._getTemplatePath('minimal.pt')
        utility = Z3CPTTemplateFactory(minimal)
        gsm = getGlobalSiteManager()
        gsm.registerUtility(utility, ITemplate, name=minimal)
        render = self._getFUT()
        result = render(minimal)
        from webob import Response
        self.failUnless(isinstance(result, Response))
        self.assertEqual(result.app_iter, ['<div>\n</div>'])
        self.assertEqual(result.status, '200 OK')
        self.assertEqual(len(result.headerlist), 2)
        self.assertEqual(queryUtility(ITemplate, minimal), utility)
        
        
