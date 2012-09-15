import sys
import unittest

from pyramid.compat import binary_type
from pyramid import testing

class Base(object):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _getTemplatePath(self, name):
        import os
        here = os.path.abspath(os.path.dirname(__file__))
        return os.path.join(here, 'fixtures', name)

class Test_renderer_factory(Base, unittest.TestCase):
    def _callFUT(self, info):
        from pyramid.chameleon_text import renderer_factory
        return renderer_factory(info)

    def test_it(self):
        # this test is way too functional
        from pyramid.chameleon_text import TextTemplateRenderer
        info = DummyInfo()
        result = self._callFUT(info)
        self.assertEqual(result.__class__, TextTemplateRenderer)

class TextTemplateRendererTests(Base, unittest.TestCase):
    def _getTargetClass(self):
        from pyramid.chameleon_text import TextTemplateRenderer
        return TextTemplateRenderer

    def _makeOne(self, *arg, **kw):
        klass = self._getTargetClass()
        return klass(*arg, **kw)

    def test_instance_implements_ITemplate(self):
        from zope.interface.verify import verifyObject
        from pyramid.interfaces import ITemplateRenderer
        path = self._getTemplatePath('minimal.txt')
        lookup = DummyLookup()
        verifyObject(ITemplateRenderer, self._makeOne(path, lookup))

    def test_class_implements_ITemplate(self):
        from zope.interface.verify import verifyClass
        from pyramid.interfaces import ITemplateRenderer
        verifyClass(ITemplateRenderer, self._getTargetClass())

    def test_template_reified(self):
        minimal = self._getTemplatePath('minimal.txt')
        lookup = DummyLookup()
        instance = self._makeOne(minimal, lookup)
        self.assertFalse('template' in instance.__dict__)
        template  = instance.template
        self.assertEqual(template, instance.__dict__['template'])

    def test_template_with_ichameleon_translate(self):
        minimal = self._getTemplatePath('minimal.txt')
        lookup = DummyLookup()
        instance = self._makeOne(minimal, lookup)
        self.assertFalse('template' in instance.__dict__)
        template  = instance.template
        self.assertEqual(template.translate, lookup.translate)

    def test_template_with_debug_templates(self):
        minimal = self._getTemplatePath('minimal.txt')
        lookup = DummyLookup()
        lookup.debug = True
        instance = self._makeOne(minimal, lookup)
        self.assertFalse('template' in instance.__dict__)
        template  = instance.template
        self.assertEqual(template.debug, True)

    def test_template_with_reload_templates(self):
        minimal = self._getTemplatePath('minimal.txt')
        lookup = DummyLookup()
        lookup.auto_reload = True
        instance = self._makeOne(minimal, lookup)
        self.assertFalse('template' in instance.__dict__)
        template  = instance.template
        self.assertEqual(template.auto_reload, True)

    def test_template_without_reload_templates(self):
        minimal = self._getTemplatePath('minimal.txt')
        lookup = DummyLookup()
        lookup.auto_reload = False
        instance = self._makeOne(minimal, lookup)
        self.assertFalse('template' in instance.__dict__)
        template  = instance.template
        self.assertEqual(template.auto_reload, False)

    def test_call(self):
        minimal = self._getTemplatePath('minimal.txt')
        lookup = DummyLookup()
        instance = self._makeOne(minimal, lookup)
        result = instance({}, {})
        self.assertTrue(isinstance(result, binary_type))
        self.assertEqual(result, b'Hello.\n')

    def test_call_with_nondict_value(self):
        minimal = self._getTemplatePath('minimal.txt')
        lookup = DummyLookup()
        instance = self._makeOne(minimal, lookup)
        self.assertRaises(ValueError, instance, None, {})

    def test_call_nonminimal(self):
        nonminimal = self._getTemplatePath('nonminimal.txt')
        lookup = DummyLookup()
        instance = self._makeOne(nonminimal, lookup)
        result = instance({'name':'Chris'}, {})
        self.assertTrue(isinstance(result, binary_type))
        self.assertEqual(result, b'Hello, Chris!\n')

    def test_implementation(self):
        minimal = self._getTemplatePath('minimal.txt')
        lookup = DummyLookup()
        instance = self._makeOne(minimal, lookup)
        result = instance.implementation()()
        self.assertTrue(isinstance(result, binary_type))
        self.assertEqual(result, b'Hello.\n')

class DummyLookup(object):
    auto_reload=True
    debug = True
    def translate(self, msg): pass

class DummyRegistry(object):
    def queryUtility(self, iface, name):
        self.queried = iface, name
        return None

    def registerUtility(self, impl, iface, name):
        self.registered = impl, iface, name
    
class DummyInfo(object):
    def __init__(self):
        self.registry = DummyRegistry()
        self.type = '.pt'
        self.name = 'fixtures/minimal.pt'
        self.package = sys.modules[__name__]
        self.settings = {}
    
