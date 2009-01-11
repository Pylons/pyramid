import unittest

from zope.testing.cleanup import cleanUp

class Base(object):
    def setUp(self):
        cleanUp()
        import warnings
        warnings.simplefilter('ignore')

    def tearDown(self):
        cleanUp()
        import warnings
        warnings.resetwarnings()
        
    def _zcmlConfigure(self):
        import repoze.bfg.includes
        import zope.configuration.xmlconfig
        zope.configuration.xmlconfig.file('configure.zcml',
                                          package=repoze.bfg.includes)

    def _getTemplatePath(self, name):
        import os
        here = os.path.abspath(os.path.dirname(__file__))
        return os.path.join(here, 'fixtures', name)
        
class RenderTemplateTests(Base, unittest.TestCase):
    def _callFUT(self, *arg, **kw):
        from repoze.bfg.template import render_template
        return render_template(*arg, **kw)

    def test_it(self):
        self._zcmlConfigure()
        minimal = self._getTemplatePath('minimal.pt')
        result = self._callFUT(minimal)
        self.failUnless(isinstance(result, str))
        self.assertEqual(result,
                     '<div xmlns="http://www.w3.org/1999/xhtml">\n</div>')

class RenderTemplateToResponseTests(Base, unittest.TestCase):
    def _callFUT(self, *arg, **kw):
        from repoze.bfg.template import render_template_to_response
        return render_template_to_response(*arg, **kw)

    def test_it(self):
        self._zcmlConfigure()
        minimal = self._getTemplatePath('minimal.pt')
        result = self._callFUT(minimal)
        from webob import Response
        self.failUnless(isinstance(result, Response))
        self.assertEqual(result.app_iter,
                     ['<div xmlns="http://www.w3.org/1999/xhtml">\n</div>'])
        self.assertEqual(result.status, '200 OK')
        self.assertEqual(len(result.headerlist), 2)

class GetTemplateTests(Base, unittest.TestCase):
    def _callFUT(self, *arg, **kw):
        from repoze.bfg.template import get_template
        return get_template(*arg, **kw)

    def test_nonabs_registered(self):
        self._zcmlConfigure()
        from zope.component import getGlobalSiteManager
        from zope.component import queryUtility
        from repoze.bfg.chameleon_zpt import ZPTTemplateFactory
        from repoze.bfg.interfaces import ITemplateRenderer
        minimal = self._getTemplatePath('minimal.pt')
        utility = ZPTTemplateFactory(minimal)
        gsm = getGlobalSiteManager()
        gsm.registerUtility(utility, ITemplateRenderer, name=minimal)
        result = self._callFUT(minimal)
        self.assertEqual(result.filename, minimal)
        self.assertEqual(queryUtility(ITemplateRenderer, minimal), utility)
        
    def test_nonabs_unregistered(self):
        self._zcmlConfigure()
        from zope.component import getGlobalSiteManager
        from zope.component import queryUtility
        from repoze.bfg.chameleon_zpt import ZPTTemplateFactory
        from repoze.bfg.interfaces import ITemplateRenderer
        minimal = self._getTemplatePath('minimal.pt')
        self.assertEqual(queryUtility(ITemplateRenderer, minimal), None)
        utility = ZPTTemplateFactory(minimal)
        gsm = getGlobalSiteManager()
        gsm.registerUtility(utility, ITemplateRenderer, name=minimal)
        result = self._callFUT(minimal)
        self.assertEqual(result.filename, minimal)
        self.assertEqual(queryUtility(ITemplateRenderer, minimal), utility)

