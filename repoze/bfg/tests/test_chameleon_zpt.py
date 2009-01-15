import unittest

from zope.testing.cleanup import cleanUp

class Base(object):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _zcmlConfigure(self):
        import repoze.bfg.includes
        import zope.configuration.xmlconfig
        zope.configuration.xmlconfig.file('configure.zcml',
                                          package=repoze.bfg.includes)

    def _getTemplatePath(self, name):
        import os
        here = os.path.abspath(os.path.dirname(__file__))
        return os.path.join(here, 'fixtures', name)
        
class ZPTTemplateRendererTests(Base, unittest.TestCase):
    def _getTargetClass(self):
        from repoze.bfg.chameleon_zpt import ZPTTemplateRenderer
        return ZPTTemplateRenderer

    def _makeOne(self, *arg, **kw):
        klass = self._getTargetClass()
        return klass(*arg, **kw)

    def test_instance_implements_ITemplate(self):
        from zope.interface.verify import verifyObject
        from repoze.bfg.interfaces import ITemplateRenderer
        path = self._getTemplatePath('minimal.pt')
        verifyObject(ITemplateRenderer, self._makeOne(path))

    def test_class_implements_ITemplate(self):
        from zope.interface.verify import verifyClass
        from repoze.bfg.interfaces import ITemplateRenderer
        verifyClass(ITemplateRenderer, self._getTargetClass())

    def test_call(self):
        self._zcmlConfigure()
        minimal = self._getTemplatePath('minimal.pt')
        instance = self._makeOne(minimal)
        result = instance()
        self.failUnless(isinstance(result, str))
        self.assertEqual(result,
                     '<div xmlns="http://www.w3.org/1999/xhtml">\n</div>')

    def test_implementation(self):
        self._zcmlConfigure()
        minimal = self._getTemplatePath('minimal.pt')
        instance = self._makeOne(minimal)
        result = instance.implementation()()
        self.failUnless(isinstance(result, str))
        self.assertEqual(result,
                     '<div xmlns="http://www.w3.org/1999/xhtml">\n</div>')
        

class RenderTemplateTests(Base, unittest.TestCase):
    def _getFUT(self):
        from repoze.bfg.chameleon_zpt import render_template
        return render_template

    def test_it(self):
        self._zcmlConfigure()
        minimal = self._getTemplatePath('minimal.pt')
        render = self._getFUT()
        result = render(minimal)
        self.failUnless(isinstance(result, str))
        self.assertEqual(result,
                     '<div xmlns="http://www.w3.org/1999/xhtml">\n</div>')

class RenderTemplateToResponseTests(Base, unittest.TestCase):
    def _getFUT(self):
        from repoze.bfg.chameleon_zpt import render_template_to_response
        return render_template_to_response

    def test_it(self):
        self._zcmlConfigure()
        minimal = self._getTemplatePath('minimal.pt')
        render = self._getFUT()
        result = render(minimal)
        from webob import Response
        self.failUnless(isinstance(result, Response))
        self.assertEqual(result.app_iter,
                     ['<div xmlns="http://www.w3.org/1999/xhtml">\n</div>'])
        self.assertEqual(result.status, '200 OK')
        self.assertEqual(len(result.headerlist), 2)

    def test_iresponsefactory_override(self):
        from zope.component import getGlobalSiteManager
        gsm = getGlobalSiteManager()
        from webob import Response
        class Response2(Response):
            pass
        from repoze.bfg.interfaces import IResponseFactory
        gsm.registerUtility(Response2, IResponseFactory)
        minimal = self._getTemplatePath('minimal.pt')
        render = self._getFUT()
        result = render(minimal)
        self.failUnless(isinstance(result, Response2))

class GetRendererTests(Base, unittest.TestCase):
    def _getFUT(self):
        from repoze.bfg.chameleon_zpt import get_renderer
        return get_renderer

    def test_nonabs_registered(self):
        from zope.component import getGlobalSiteManager
        from zope.component import queryUtility
        from repoze.bfg.chameleon_zpt import ZPTTemplateRenderer
        from repoze.bfg.interfaces import ITemplateRenderer
        minimal = self._getTemplatePath('minimal.pt')
        utility = ZPTTemplateRenderer(minimal)
        gsm = getGlobalSiteManager()
        gsm.registerUtility(utility, ITemplateRenderer, name=minimal)
        get = self._getFUT()
        result = get(minimal)
        self.assertEqual(result, utility)
        self.assertEqual(queryUtility(ITemplateRenderer, minimal), utility)
        
    def test_nonabs_unregistered(self):
        from zope.component import getGlobalSiteManager
        from zope.component import queryUtility
        from repoze.bfg.chameleon_zpt import ZPTTemplateRenderer
        from repoze.bfg.interfaces import ITemplateRenderer
        minimal = self._getTemplatePath('minimal.pt')
        self.assertEqual(queryUtility(ITemplateRenderer, minimal), None)
        utility = ZPTTemplateRenderer(minimal)
        gsm = getGlobalSiteManager()
        gsm.registerUtility(utility, ITemplateRenderer, name=minimal)
        get = self._getFUT()
        result = get(minimal)
        self.assertEqual(result, utility)
        self.assertEqual(queryUtility(ITemplateRenderer, minimal), utility)

    def test_explicit_registration(self):
        from zope.component import getGlobalSiteManager
        from repoze.bfg.interfaces import ITemplateRenderer
        class Dummy:
            template = object()
        gsm = getGlobalSiteManager()
        utility = Dummy()
        gsm.registerUtility(utility, ITemplateRenderer, name='foo')
        get = self._getFUT()
        result = get('foo')
        self.failUnless(result is utility)

class GetTemplateTests(Base, unittest.TestCase):
    def _getFUT(self):
        from repoze.bfg.chameleon_zpt import get_template
        return get_template

    def test_nonabs_registered(self):
        self._zcmlConfigure()
        from zope.component import getGlobalSiteManager
        from zope.component import queryUtility
        from repoze.bfg.chameleon_zpt import ZPTTemplateRenderer
        from repoze.bfg.interfaces import ITemplateRenderer
        minimal = self._getTemplatePath('minimal.pt')
        utility = ZPTTemplateRenderer(minimal)
        gsm = getGlobalSiteManager()
        gsm.registerUtility(utility, ITemplateRenderer, name=minimal)
        get = self._getFUT()
        result = get(minimal)
        self.assertEqual(result.filename, minimal)
        self.assertEqual(queryUtility(ITemplateRenderer, minimal), utility)
        
    def test_nonabs_unregistered(self):
        self._zcmlConfigure()
        from zope.component import getGlobalSiteManager
        from zope.component import queryUtility
        from repoze.bfg.chameleon_zpt import ZPTTemplateRenderer
        from repoze.bfg.interfaces import ITemplateRenderer
        minimal = self._getTemplatePath('minimal.pt')
        self.assertEqual(queryUtility(ITemplateRenderer, minimal), None)
        utility = ZPTTemplateRenderer(minimal)
        gsm = getGlobalSiteManager()
        gsm.registerUtility(utility, ITemplateRenderer, name=minimal)
        get = self._getFUT()
        result = get(minimal)
        self.assertEqual(result.filename, minimal)
        self.assertEqual(queryUtility(ITemplateRenderer, minimal), utility)

    def test_explicit_registration(self):
        from zope.component import getGlobalSiteManager
        from repoze.bfg.interfaces import ITemplateRenderer
        class Dummy:
            template = object()
            def implementation(self):
                return self.template
        gsm = getGlobalSiteManager()
        utility = Dummy()
        gsm.registerUtility(utility, ITemplateRenderer, name='foo')
        get = self._getFUT()
        result = get('foo')
        self.failUnless(result is utility.template)
        
        
        


