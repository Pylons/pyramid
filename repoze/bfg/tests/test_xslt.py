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
        
class XSLTemplateFactoryTests(unittest.TestCase, Base):
    def setUp(self):
        Base.setUp(self)

    def tearDown(self):
        Base.tearDown(self)

    def _getTargetClass(self):
        from repoze.bfg.template import XSLTemplateFactory
        return XSLTemplateFactory

    def _makeOne(self, *arg, **kw):
        klass = self._getTargetClass()
        return klass(*arg, **kw)

    def test_instance_implements_INodeTemplate(self):
        from zope.interface.verify import verifyObject
        from repoze.bfg.interfaces import INodeTemplate
        path = self._getTemplatePath('minimal.xsl')
        verifyObject(INodeTemplate, self._makeOne(path))

    def test_class_implements_INodeTemplate(self):
        from zope.interface.verify import verifyClass
        from repoze.bfg.interfaces import INodeTemplate
        verifyClass(INodeTemplate, self._getTargetClass())

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
        from repoze.bfg.template import render_transform_to_response
        return render_transform_to_response

    def test_nonabs_unregistered(self):
        self._zcmlConfigure()
        from zope.component import queryUtility
        from repoze.bfg.interfaces import INodeTemplate
        minimal = self._getTemplatePath('minimal.xsl')
        self.assertEqual(queryUtility(INodeTemplate, minimal), None)
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
        from repoze.bfg.template import XSLTemplateFactory
        self.failUnless(isinstance(queryUtility(INodeTemplate, minimal),
                                   XSLTemplateFactory))

    def test_nonabs_registered(self):
        self._zcmlConfigure()
        from zope.component import getGlobalSiteManager
        from zope.component import queryUtility
        from repoze.bfg.template import XSLTemplateFactory
        from repoze.bfg.interfaces import INodeTemplate
        minimal = self._getTemplatePath('minimal.xsl')
        utility = XSLTemplateFactory(minimal)
        gsm = getGlobalSiteManager()
        gsm.registerUtility(utility, INodeTemplate, name=minimal)
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
        self.assertEqual(queryUtility(INodeTemplate, minimal), utility)

class RenderTransformTests(unittest.TestCase, Base):
    def setUp(self):
        Base.setUp(self)

    def tearDown(self):
        Base.tearDown(self)

    def _getFUT(self):
        from repoze.bfg.template import render_transform
        return render_transform

    def test_nonabs_unregistered(self):
        self._zcmlConfigure()
        from zope.component import queryUtility
        from repoze.bfg.interfaces import INodeTemplate
        minimal = self._getTemplatePath('minimal.xsl')
        self.assertEqual(queryUtility(INodeTemplate, minimal), None)
        render = self._getFUT()
        from lxml import etree
        info = etree.Element("info")
        result = render(minimal, node=info)
        self.failUnless(isinstance(result, str))
        resultstr = """<?xml version="1.0"?>\n<div/>\n"""
        self.assertEqual(result, resultstr)
        from repoze.bfg.template import XSLTemplateFactory
        self.failUnless(isinstance(queryUtility(INodeTemplate, minimal),
                                   XSLTemplateFactory))

    def test_nonabs_registered(self):
        self._zcmlConfigure()
        from zope.component import getGlobalSiteManager
        from zope.component import queryUtility
        from repoze.bfg.template import XSLTemplateFactory
        from repoze.bfg.interfaces import INodeTemplate
        minimal = self._getTemplatePath('minimal.xsl')
        utility = XSLTemplateFactory(minimal)
        gsm = getGlobalSiteManager()
        gsm.registerUtility(utility, INodeTemplate, name=minimal)
        render = self._getFUT()
        from lxml import etree
        info = etree.Element("info")
        result = render(minimal, node=info)
        self.failUnless(isinstance(result, str))
        resultstr = """<?xml version="1.0"?>\n<div/>\n"""
        self.assertEqual(result, resultstr)
        self.assertEqual(queryUtility(INodeTemplate, minimal), utility)

