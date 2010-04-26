import unittest

from repoze.bfg.testing import cleanUp

class Base(object):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _getTemplatePath(self, name):
        import os
        here = os.path.abspath(os.path.dirname(__file__))
        return os.path.join(here, 'fixtures', name)

    def _registerUtility(self, utility, iface, name=''):
        from repoze.bfg.threadlocal import get_current_registry
        reg = get_current_registry()
        reg.registerUtility(utility, iface, name=name)
        return reg
        
class ZPTTemplateRendererTests(Base, unittest.TestCase):
    def setUp(self):
        from repoze.bfg.configuration import Configurator
        from repoze.bfg.registry import Registry
        registry = Registry()
        self.config = Configurator(registry=registry)
        self.config.begin()

    def tearDown(self):
        self.config.end()

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
        minimal = self._getTemplatePath('minimal.pt')
        instance = self._makeOne(minimal)
        result = instance({}, {})
        self.failUnless(isinstance(result, unicode))
        self.assertEqual(result,
                     '<div xmlns="http://www.w3.org/1999/xhtml">\n</div>')

    def test_template_reified(self):
        minimal = self._getTemplatePath('minimal.pt')
        instance = self._makeOne(minimal)
        self.failIf('template' in instance.__dict__)
        template  = instance.template
        self.assertEqual(template, instance.__dict__['template'])

    def test_template_with_ichameleon_translate(self):
        from repoze.bfg.interfaces import IChameleonTranslate
        def ct(): pass
        self.config.registry.registerUtility(ct, IChameleonTranslate)
        minimal = self._getTemplatePath('minimal.pt')
        instance = self._makeOne(minimal)
        self.failIf('template' in instance.__dict__)
        template  = instance.template
        self.assertEqual(template.translate, ct)

    def test_template_with_debug_templates(self):
        self.config.add_settings({'debug_templates':True})
        minimal = self._getTemplatePath('minimal.pt')
        instance = self._makeOne(minimal)
        self.failIf('template' in instance.__dict__)
        template  = instance.template
        self.assertEqual(template.debug, True)

    def test_template_with_reload_templates(self):
        self.config.add_settings({'reload_templates':True})
        minimal = self._getTemplatePath('minimal.pt')
        instance = self._makeOne(minimal)
        self.failIf('template' in instance.__dict__)
        template  = instance.template
        self.assertEqual(template.auto_reload, True)

    def test_template_with_emptydict(self):
        from repoze.bfg.interfaces import ISettings
        self.config.registry.registerUtility({}, ISettings)
        minimal = self._getTemplatePath('minimal.pt')
        instance = self._makeOne(minimal)
        self.failIf('template' in instance.__dict__)
        template  = instance.template
        self.assertEqual(template.auto_reload, False)
        self.assertEqual(template.debug, False)

    def test_call_with_nondict_value(self):
        minimal = self._getTemplatePath('minimal.pt')
        instance = self._makeOne(minimal)
        self.assertRaises(ValueError, instance, None, {})

    def test_implementation(self):
        minimal = self._getTemplatePath('minimal.pt')
        instance = self._makeOne(minimal)
        result = instance.implementation()()
        self.failUnless(isinstance(result, unicode))
        self.assertEqual(result,
                     '<div xmlns="http://www.w3.org/1999/xhtml">\n</div>')
        

class RenderTemplateTests(Base, unittest.TestCase):
    def _callFUT(self, name, **kw):
        from repoze.bfg.chameleon_zpt import render_template
        return render_template(name, **kw)

    def test_it(self):
        minimal = self._getTemplatePath('minimal.pt')
        result = self._callFUT(minimal)
        self.failUnless(isinstance(result, unicode))
        self.assertEqual(result,
                     '<div xmlns="http://www.w3.org/1999/xhtml">\n</div>')

class RenderTemplateToResponseTests(Base, unittest.TestCase):
    def _callFUT(self, name, **kw):
        from repoze.bfg.chameleon_zpt import render_template_to_response
        return render_template_to_response(name, **kw)

    def test_it(self):
        minimal = self._getTemplatePath('minimal.pt')
        result = self._callFUT(minimal)
        from webob import Response
        self.failUnless(isinstance(result, Response))
        self.assertEqual(result.app_iter,
                     ['<div xmlns="http://www.w3.org/1999/xhtml">\n</div>'])
        self.assertEqual(result.status, '200 OK')
        self.assertEqual(len(result.headerlist), 2)

    def test_iresponsefactory_override(self):
        from webob import Response
        class Response2(Response):
            pass
        from repoze.bfg.interfaces import IResponseFactory
        self._registerUtility(Response2, IResponseFactory)
        minimal = self._getTemplatePath('minimal.pt')
        result = self._callFUT(minimal)
        self.failUnless(isinstance(result, Response2))

class GetRendererTests(Base, unittest.TestCase):
    def _callFUT(self, name):
        from repoze.bfg.chameleon_zpt import get_renderer
        return get_renderer(name)

    def test_nonabs_registered(self):
        from repoze.bfg.threadlocal import get_current_registry
        from repoze.bfg.chameleon_zpt import ZPTTemplateRenderer
        from repoze.bfg.interfaces import ITemplateRenderer
        minimal = self._getTemplatePath('minimal.pt')
        utility = ZPTTemplateRenderer(minimal)
        self._registerUtility(utility, ITemplateRenderer, name=minimal)
        result = self._callFUT(minimal)
        self.assertEqual(result, utility)
        reg = get_current_registry()
        self.assertEqual(reg.queryUtility(ITemplateRenderer, minimal), utility)
        
    def test_nonabs_unregistered(self):
        from repoze.bfg.threadlocal import get_current_registry
        from repoze.bfg.chameleon_zpt import ZPTTemplateRenderer
        from repoze.bfg.interfaces import ITemplateRenderer
        minimal = self._getTemplatePath('minimal.pt')
        reg = get_current_registry()
        self.assertEqual(reg.queryUtility(ITemplateRenderer, minimal), None)
        utility = ZPTTemplateRenderer(minimal)
        self._registerUtility(utility, ITemplateRenderer, name=minimal)
        result = self._callFUT(minimal)
        self.assertEqual(result, utility)
        self.assertEqual(reg.queryUtility(ITemplateRenderer, minimal), utility)

    def test_explicit_registration(self):
        from repoze.bfg.interfaces import ITemplateRenderer
        class Dummy:
            template = object()
        utility = Dummy()
        self._registerUtility(utility, ITemplateRenderer, name='foo')
        result = self._callFUT('foo')
        self.failUnless(result is utility)

class GetTemplateTests(Base, unittest.TestCase):
    def _callFUT(self, name):
        from repoze.bfg.chameleon_zpt import get_template
        return get_template(name)

    def test_nonabs_registered(self):
        from repoze.bfg.threadlocal import get_current_registry
        from repoze.bfg.chameleon_zpt import ZPTTemplateRenderer
        from repoze.bfg.interfaces import ITemplateRenderer
        minimal = self._getTemplatePath('minimal.pt')
        utility = ZPTTemplateRenderer(minimal)
        self._registerUtility(utility, ITemplateRenderer, name=minimal)
        result = self._callFUT(minimal)
        self.assertEqual(result.filename, minimal)
        reg = get_current_registry()
        self.assertEqual(reg.queryUtility(ITemplateRenderer, minimal), utility)
        
    def test_nonabs_unregistered(self):
        from repoze.bfg.threadlocal import get_current_registry
        from repoze.bfg.chameleon_zpt import ZPTTemplateRenderer
        from repoze.bfg.interfaces import ITemplateRenderer
        minimal = self._getTemplatePath('minimal.pt')
        reg = get_current_registry()
        self.assertEqual(reg.queryUtility(ITemplateRenderer, minimal), None)
        utility = ZPTTemplateRenderer(minimal)
        self._registerUtility(utility, ITemplateRenderer, name=minimal)
        result = self._callFUT(minimal)
        self.assertEqual(result.filename, minimal)
        self.assertEqual(reg.queryUtility(ITemplateRenderer, minimal), utility)

    def test_explicit_registration(self):
        from repoze.bfg.interfaces import ITemplateRenderer
        class Dummy:
            template = object()
            def implementation(self):
                return self.template
        utility = Dummy()
        self._registerUtility(utility, ITemplateRenderer, name='foo')
        result = self._callFUT('foo')
        self.failUnless(result is utility.template)
        
        
        


