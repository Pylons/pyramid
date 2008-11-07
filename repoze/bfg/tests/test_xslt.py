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
        
class XSLTemplateRendererTests(unittest.TestCase, Base):
    def setUp(self):
        Base.setUp(self)

    def tearDown(self):
        Base.tearDown(self)

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

class RenderTransformToResponseTests(unittest.TestCase, Base):
    def setUp(self):
        Base.setUp(self)

    def tearDown(self):
        Base.tearDown(self)

    def _getFUT(self):
        from repoze.bfg.xslt import render_transform_to_response
        return render_transform_to_response

    def test_nonabs_unregistered(self):
        self._zcmlConfigure()
        from zope.component import queryUtility
        from repoze.bfg.interfaces import INodeTemplateRenderer
        minimal = self._getTemplatePath('minimal.xsl')
        self.assertEqual(queryUtility(INodeTemplateRenderer, minimal), None)
        render = self._getFUT()
        from lxml import etree
        info = etree.Element("info")
        result = render(minimal, node=info)
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
        render = self._getFUT()
        from lxml import etree
        info = etree.Element("info")
        result = render(minimal, node=info)
        from webob import Response
        self.failUnless(isinstance(result, Response))
        resultstr = """<?xml version="1.0"?>\n<div/>\n"""
        self.assertEqual(result.app_iter, [resultstr])
        self.assertEqual(result.status, '200 OK')
        self.assertEqual(len(result.headerlist), 2)
        self.assertEqual(queryUtility(INodeTemplateRenderer, minimal), utility)

class RenderTransformTests(unittest.TestCase, Base):
    def setUp(self):
        Base.setUp(self)

    def tearDown(self):
        Base.tearDown(self)

    def _getFUT(self):
        from repoze.bfg.xslt import render_transform
        return render_transform

    def test_nonabs_unregistered(self):
        self._zcmlConfigure()
        from zope.component import queryUtility
        from repoze.bfg.interfaces import INodeTemplateRenderer
        minimal = self._getTemplatePath('minimal.xsl')
        self.assertEqual(queryUtility(INodeTemplateRenderer, minimal), None)
        render = self._getFUT()
        from lxml import etree
        info = etree.Element("info")
        result = render(minimal, node=info)
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
        render = self._getFUT()
        from lxml import etree
        info = etree.Element("info")
        result = render(minimal, node=info)
        self.failUnless(isinstance(result, str))
        resultstr = """<?xml version="1.0"?>\n<div/>\n"""
        self.assertEqual(result, resultstr)
        self.assertEqual(queryUtility(INodeTemplateRenderer, minimal), utility)

