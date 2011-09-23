import unittest

from pyramid.compat import binary_type
from pyramid.testing import skip_on
from pyramid import testing

class Base:
    def setUp(self):
        self.config = testing.setUp()
        from zope.deprecation import __show__
        __show__.off()

    def tearDown(self):
        testing.tearDown()
        from zope.deprecation import __show__
        __show__.on()

    def _getTemplatePath(self, name):
        import os
        here = os.path.abspath(os.path.dirname(__file__))
        return os.path.join(here, 'fixtures', name)

    def _registerUtility(self, utility, iface, name=''):
        reg = self.config.registry
        reg.registerUtility(utility, iface, name=name)

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

    @skip_on('java')
    def test_template_reified(self):
        minimal = self._getTemplatePath('minimal.txt')
        lookup = DummyLookup()
        instance = self._makeOne(minimal, lookup)
        self.assertFalse('template' in instance.__dict__)
        template  = instance.template
        self.assertEqual(template, instance.__dict__['template'])

    @skip_on('java')
    def test_template_with_ichameleon_translate(self):
        minimal = self._getTemplatePath('minimal.txt')
        lookup = DummyLookup()
        instance = self._makeOne(minimal, lookup)
        self.assertFalse('template' in instance.__dict__)
        template  = instance.template
        self.assertEqual(template.translate, lookup.translate)

    @skip_on('java')
    def test_template_with_debug_templates(self):
        minimal = self._getTemplatePath('minimal.txt')
        lookup = DummyLookup()
        lookup.debug = True
        instance = self._makeOne(minimal, lookup)
        self.assertFalse('template' in instance.__dict__)
        template  = instance.template
        self.assertEqual(template.debug, True)

    @skip_on('java')
    def test_template_with_reload_templates(self):
        minimal = self._getTemplatePath('minimal.txt')
        lookup = DummyLookup()
        lookup.auto_reload = True
        instance = self._makeOne(minimal, lookup)
        self.assertFalse('template' in instance.__dict__)
        template  = instance.template
        self.assertEqual(template.auto_reload, True)

    @skip_on('java')
    def test_template_without_reload_templates(self):
        minimal = self._getTemplatePath('minimal.txt')
        lookup = DummyLookup()
        lookup.auto_reload = False
        instance = self._makeOne(minimal, lookup)
        self.assertFalse('template' in instance.__dict__)
        template  = instance.template
        self.assertEqual(template.auto_reload, False)

    @skip_on('java')
    def test_call(self):
        minimal = self._getTemplatePath('minimal.txt')
        lookup = DummyLookup()
        instance = self._makeOne(minimal, lookup)
        result = instance({}, {})
        self.assertTrue(isinstance(result, binary_type))
        self.assertEqual(result, b'Hello.\n')

    @skip_on('java')
    def test_call_with_nondict_value(self):
        minimal = self._getTemplatePath('minimal.txt')
        lookup = DummyLookup()
        instance = self._makeOne(minimal, lookup)
        self.assertRaises(ValueError, instance, None, {})

    @skip_on('java')
    def test_call_nonminimal(self):
        nonminimal = self._getTemplatePath('nonminimal.txt')
        lookup = DummyLookup()
        instance = self._makeOne(nonminimal, lookup)
        result = instance({'name':'Chris'}, {})
        self.assertTrue(isinstance(result, binary_type))
        self.assertEqual(result, b'Hello, Chris!\n')

    @skip_on('java')
    def test_implementation(self):
        minimal = self._getTemplatePath('minimal.txt')
        lookup = DummyLookup()
        instance = self._makeOne(minimal, lookup)
        result = instance.implementation()()
        self.assertTrue(isinstance(result, binary_type))
        self.assertEqual(result, b'Hello.\n')

class RenderTemplateTests(Base, unittest.TestCase):
    def _callFUT(self, name, **kw):
        from pyramid.chameleon_text import render_template
        return render_template(name, **kw)

    @skip_on('java')
    def test_it(self):
        minimal = self._getTemplatePath('minimal.txt')
        result = self._callFUT(minimal)
        self.assertTrue(isinstance(result, binary_type))
        self.assertEqual(result, b'Hello.\n')

class RenderTemplateToResponseTests(Base, unittest.TestCase):
    def _callFUT(self, name, **kw):
        from pyramid.chameleon_text import render_template_to_response
        return render_template_to_response(name, **kw)

    @skip_on('java')
    def test_minimal(self):
        minimal = self._getTemplatePath('minimal.txt')
        result = self._callFUT(minimal)
        from webob import Response
        self.assertTrue(isinstance(result, Response))
        self.assertEqual(result.app_iter, [b'Hello.\n'])
        self.assertEqual(result.status, '200 OK')
        self.assertEqual(len(result.headerlist), 2)

    @skip_on('java')
    def test_iresponsefactory_override(self):
        from webob import Response
        class Response2(Response):
            pass
        from pyramid.interfaces import IResponseFactory
        self._registerUtility(Response2, IResponseFactory)
        minimal = self._getTemplatePath('minimal.txt')
        result = self._callFUT(minimal)
        self.assertTrue(isinstance(result, Response2))

class GetRendererTests(Base, unittest.TestCase):
    def _callFUT(self, name):
        from pyramid.chameleon_text import get_renderer
        return get_renderer(name)

    @skip_on('java')
    def test_it(self):
        from pyramid.interfaces import IRendererFactory
        class Dummy:
            template = object()
            def implementation(self): pass
        renderer = Dummy()
        def rf(spec):
            return renderer
        self._registerUtility(rf, IRendererFactory, name='foo')
        result = self._callFUT('foo')
        self.assertTrue(result is renderer)

class GetTemplateTests(Base, unittest.TestCase):
    def _callFUT(self, name):
        from pyramid.chameleon_text import get_template
        return get_template(name)

    @skip_on('java')
    def test_it(self):
        from pyramid.interfaces import IRendererFactory
        class Dummy:
            template = object()
            def implementation(self):
                return self.template
        renderer = Dummy()
        def rf(spec):
            return renderer
        self._registerUtility(rf, IRendererFactory, name='foo')
        result = self._callFUT('foo')
        self.assertTrue(result is renderer.template)

class DummyLookup(object):
    auto_reload=True
    debug = True
    def translate(self, msg): pass
    
