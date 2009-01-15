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
        
class XSLTemplateRendererTests(Base, unittest.TestCase):
    def _getTargetClass(self):
        from repoze.bfg.xslt import XSLTemplateRenderer
        return XSLTemplateRenderer

    def _makeOne(self, *arg, **kw):
        klass = self._getTargetClass()
        return klass(*arg, **kw)

    def test_instance_implements_INodeTemplate(self):
        from zope.interface.verify import verifyObject
        from repoze.bfg.interfaces import INodeTemplateRenderer
        path = self._getTemplatePath('minimal.xsl')
        verifyObject(INodeTemplateRenderer, self._makeOne(path))

    def test_class_implements_INodeTemplate(self):
        from zope.interface.verify import verifyClass
        from repoze.bfg.interfaces import INodeTemplateRenderer
        verifyClass(INodeTemplateRenderer, self._getTargetClass())

    def test_call(self):
        self._zcmlConfigure()
        minimal = self._getTemplatePath('minimal.xsl')
        instance = self._makeOne(minimal)
        from lxml import etree
        info = etree.Element("info")
        result = instance(node=info)
        self.failUnless(isinstance(result, str))
        resultstr = """<?xml version="1.0"?>\n<div/>\n"""
        self.assertEqual(result, resultstr)

class GetTransformTests(Base, unittest.TestCase):
    def _callFUT(self, path, node):
        from repoze.bfg.xslt import get_transform
        return get_transform(path, node)

    def test_nonabs_registered(self):
        from zope.component import getGlobalSiteManager
        from repoze.bfg.interfaces import INodeTemplateRenderer
        renderer = {}
        gsm = getGlobalSiteManager()
        minimal = self._getTemplatePath('minimal.xsl')
        gsm.registerUtility(renderer, INodeTemplateRenderer, name=minimal)
        result = self._callFUT('fixtures/minimal.xsl', None)
        self.failUnless(result is renderer)
        
    def test_abs_registered(self):
        from zope.component import getGlobalSiteManager
        from repoze.bfg.interfaces import INodeTemplateRenderer
        renderer = {}
        gsm = getGlobalSiteManager()
        minimal = self._getTemplatePath('minimal.xsl')
        gsm.registerUtility(renderer, INodeTemplateRenderer, name=minimal)
        result = self._callFUT(minimal, None)
        self.failUnless(result is renderer)

    def test_unregistered(self):
        from zope.component import getGlobalSiteManager
        from zope.component import queryUtility
        from repoze.bfg.interfaces import INodeTemplateRenderer
        minimal = self._getTemplatePath('minimal.xsl')
        self.assertEqual(queryUtility(INodeTemplateRenderer, minimal), None)
        gsm = getGlobalSiteManager()
        result = self._callFUT(minimal, None)
        self.assertEqual(queryUtility(INodeTemplateRenderer, minimal).path,
                         minimal)

    def test_unregistered_missing(self):
        from zope.component import getGlobalSiteManager
        minimal = self._getTemplatePath('notthere.xsl')
        gsm = getGlobalSiteManager()
        self.assertRaises(ValueError, self._callFUT, minimal, None)

class RenderTransformToResponseTests(Base, unittest.TestCase):
    def _callFUT(self, minimal, node):
        from repoze.bfg.xslt import render_transform_to_response
        return render_transform_to_response(minimal, node=node)

    def test_nonabs_unregistered(self):
        self._zcmlConfigure()
        from zope.component import queryUtility
        from repoze.bfg.interfaces import INodeTemplateRenderer
        minimal = self._getTemplatePath('minimal.xsl')
        self.assertEqual(queryUtility(INodeTemplateRenderer, minimal), None)
        from lxml import etree
        info = etree.Element("info")
        result = self._callFUT(minimal, node=info)
        from webob import Response
        self.failUnless(isinstance(result, Response))
        resultstr = """<?xml version="1.0"?>\n<div/>\n"""
        self.assertEqual(result.app_iter, [resultstr])
        self.assertEqual(result.status, '200 OK')
        self.assertEqual(len(result.headerlist), 2)
        from repoze.bfg.xslt import XSLTemplateRenderer
        self.failUnless(isinstance(queryUtility(INodeTemplateRenderer, minimal),
                                   XSLTemplateRenderer))

    def test_nonabs_registered(self):
        self._zcmlConfigure()
        from zope.component import getGlobalSiteManager
        from zope.component import queryUtility
        from repoze.bfg.xslt import XSLTemplateRenderer
        from repoze.bfg.interfaces import INodeTemplateRenderer
        minimal = self._getTemplatePath('minimal.xsl')
        utility = XSLTemplateRenderer(minimal)
        gsm = getGlobalSiteManager()
        gsm.registerUtility(utility, INodeTemplateRenderer, name=minimal)
        from lxml import etree
        info = etree.Element("info")
        result = self._callFUT(minimal, node=info)
        from webob import Response
        self.failUnless(isinstance(result, Response))
        resultstr = """<?xml version="1.0"?>\n<div/>\n"""
        self.assertEqual(result.app_iter, [resultstr])
        self.assertEqual(result.status, '200 OK')
        self.assertEqual(len(result.headerlist), 2)
        self.assertEqual(queryUtility(INodeTemplateRenderer, minimal), utility)

    def test_alternate_iresponse_factory(self):
        self._zcmlConfigure()
        from repoze.bfg.interfaces import IResponseFactory
        from zope.component import getGlobalSiteManager
        gsm = getGlobalSiteManager()
        from webob import Response
        class Response2(Response):
            pass
        gsm.registerUtility(Response2, IResponseFactory)
        from zope.component import getGlobalSiteManager
        from repoze.bfg.xslt import XSLTemplateRenderer
        from repoze.bfg.interfaces import INodeTemplateRenderer
        minimal = self._getTemplatePath('minimal.xsl')
        utility = XSLTemplateRenderer(minimal)
        gsm = getGlobalSiteManager()
        gsm.registerUtility(utility, INodeTemplateRenderer, name=minimal)
        from lxml import etree
        info = etree.Element("info")
        result = self._callFUT(minimal, node=info)
        self.failUnless(isinstance(result, Response2))


class RenderTransformTests(Base, unittest.TestCase):
    def _callFUT(self, path, node):
        from repoze.bfg.xslt import render_transform
        return render_transform(path, node=node)

    def test_nonabs_unregistered(self):
        self._zcmlConfigure()
        from zope.component import queryUtility
        from repoze.bfg.interfaces import INodeTemplateRenderer
        minimal = self._getTemplatePath('minimal.xsl')
        self.assertEqual(queryUtility(INodeTemplateRenderer, minimal), None)
        from lxml import etree
        info = etree.Element("info")
        result = self._callFUT(minimal, node=info)
        self.failUnless(isinstance(result, str))
        resultstr = """<?xml version="1.0"?>\n<div/>\n"""
        self.assertEqual(result, resultstr)
        from repoze.bfg.xslt import XSLTemplateRenderer
        self.failUnless(isinstance(queryUtility(INodeTemplateRenderer, minimal),
                                   XSLTemplateRenderer))

    def test_nonabs_registered(self):
        self._zcmlConfigure()
        from zope.component import getGlobalSiteManager
        from zope.component import queryUtility
        from repoze.bfg.xslt import XSLTemplateRenderer
        from repoze.bfg.interfaces import INodeTemplateRenderer
        minimal = self._getTemplatePath('minimal.xsl')
        utility = XSLTemplateRenderer(minimal)
        gsm = getGlobalSiteManager()
        gsm.registerUtility(utility, INodeTemplateRenderer, name=minimal)
        from lxml import etree
        info = etree.Element("info")
        result = self._callFUT(minimal, node=info)
        self.failUnless(isinstance(result, str))
        resultstr = """<?xml version="1.0"?>\n<div/>\n"""
        self.assertEqual(result, resultstr)
        self.assertEqual(queryUtility(INodeTemplateRenderer, minimal), utility)

class TestGetProcessor(Base, unittest.TestCase):
    def _callFUT(self, fn, auto_reload=False):
        from repoze.bfg.xslt import get_processor
        return get_processor(fn, auto_reload)

    def test_no_processors(self):
        from lxml.etree import XSLT
        from repoze.bfg.xslt import xslt_pool
        del xslt_pool.processors
        path = self._getTemplatePath('minimal.xsl')
        result = self._callFUT(path)
        self.failUnless(isinstance(result, XSLT))
        
    def test_empty_processors(self):
        from lxml.etree import XSLT
        from repoze.bfg.xslt import xslt_pool
        xslt_pool.processors = {}
        path = self._getTemplatePath('minimal.xsl')
        result = self._callFUT(path)
        self.failUnless(isinstance(result, XSLT))
    
