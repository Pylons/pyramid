import unittest

from repoze.bfg.testing import cleanUp

class Base:
    def setUp(self):
        cleanUp()
        import os
        try:
            # avoid spew from chameleon logger?
            os.unlink(self._getTemplatePath('minimal.txt.py'))
        except:
            pass

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
        

class TextTemplateRendererTests(Base, unittest.TestCase):
    def _getTargetClass(self):
        from repoze.bfg.chameleon_text import TextTemplateRenderer
        return TextTemplateRenderer

    def _makeOne(self, *arg, **kw):
        klass = self._getTargetClass()
        return klass(*arg, **kw)

    def test_instance_implements_ITemplate(self):
        from zope.interface.verify import verifyObject
        from repoze.bfg.interfaces import ITemplateRenderer
        path = self._getTemplatePath('minimal.txt')
        verifyObject(ITemplateRenderer, self._makeOne(path))

    def test_class_implements_ITemplate(self):
        from zope.interface.verify import verifyClass
        from repoze.bfg.interfaces import ITemplateRenderer
        verifyClass(ITemplateRenderer, self._getTargetClass())

    def test_template_reified(self):
        minimal = self._getTemplatePath('minimal.txt')
        instance = self._makeOne(minimal)
        self.failIf('template' in instance.__dict__)
        template  = instance.template
        self.assertEqual(template, instance.__dict__['template'])

    def test_call(self):
        minimal = self._getTemplatePath('minimal.txt')
        instance = self._makeOne(minimal)
        result = instance({}, {})
        self.failUnless(isinstance(result, str))
        self.assertEqual(result, 'Hello.\n')

    def test_call_with_nondict_value(self):
        minimal = self._getTemplatePath('minimal.txt')
        instance = self._makeOne(minimal)
        self.assertRaises(ValueError, instance, None, {})

    def test_call_nonminimal(self):
        nonminimal = self._getTemplatePath('nonminimal.txt')
        instance = self._makeOne(nonminimal)
        result = instance({'name':'Chris'}, {})
        self.failUnless(isinstance(result, str))
        self.assertEqual(result, 'Hello, Chris!\n')

    def test_implementation(self):
        minimal = self._getTemplatePath('minimal.txt')
        instance = self._makeOne(minimal)
        result = instance.implementation()()
        self.failUnless(isinstance(result, str))
        self.assertEqual(result, 'Hello.\n')

class RenderTemplateTests(Base, unittest.TestCase):
    def _callFUT(self, name, **kw):
        from repoze.bfg.chameleon_text import render_template
        return render_template(name, **kw)

    def test_it(self):
        minimal = self._getTemplatePath('minimal.txt')
        result = self._callFUT(minimal)
        self.failUnless(isinstance(result, str))
        self.assertEqual(result, 'Hello.\n')

class RenderTemplateToResponseTests(Base, unittest.TestCase):
    def _callFUT(self, name, **kw):
        from repoze.bfg.chameleon_text import render_template_to_response
        return render_template_to_response(name, **kw)

    def test_minimal(self):
        minimal = self._getTemplatePath('minimal.txt')
        result = self._callFUT(minimal)
        from webob import Response
        self.failUnless(isinstance(result, Response))
        self.assertEqual(result.app_iter, ['Hello.\n'])
        self.assertEqual(result.status, '200 OK')
        self.assertEqual(len(result.headerlist), 2)

    def test_iresponsefactory_override(self):
        from webob import Response
        class Response2(Response):
            pass
        from repoze.bfg.interfaces import IResponseFactory
        self._registerUtility(Response2, IResponseFactory)
        minimal = self._getTemplatePath('minimal.txt')
        result = self._callFUT(minimal)
        self.failUnless(isinstance(result, Response2))

class GetRendererTests(Base, unittest.TestCase):
    def _callFUT(self, name):
        from repoze.bfg.chameleon_text import get_renderer
        return get_renderer(name)

    def test_nonabs_registered(self):
        from repoze.bfg.threadlocal import get_current_registry
        from repoze.bfg.chameleon_text import TextTemplateRenderer
        from repoze.bfg.interfaces import ITemplateRenderer
        minimal = self._getTemplatePath('minimal.txt')
        utility = TextTemplateRenderer(minimal)
        self._registerUtility(utility, ITemplateRenderer, name=minimal)
        result = self._callFUT(minimal)
        self.assertEqual(result, utility)
        reg = get_current_registry()
        self.assertEqual(reg.queryUtility(ITemplateRenderer, minimal), utility)
        
    def test_nonabs_unregistered(self):
        from repoze.bfg.threadlocal import get_current_registry
        from repoze.bfg.chameleon_text import TextTemplateRenderer
        from repoze.bfg.interfaces import ITemplateRenderer
        minimal = self._getTemplatePath('minimal.txt')
        reg = get_current_registry()
        self.assertEqual(reg.queryUtility(ITemplateRenderer, minimal), None)
        utility = TextTemplateRenderer(minimal)
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

class GetTemplateTests(unittest.TestCase, Base):
    def setUp(self):
        Base.setUp(self)

    def tearDown(self):
        Base.tearDown(self)

    def _callFUT(self, name):
        from repoze.bfg.chameleon_text import get_template
        return get_template(name)

    def test_nonabs_registered(self):
        from repoze.bfg.threadlocal import get_current_registry
        from repoze.bfg.chameleon_text import TextTemplateRenderer
        from repoze.bfg.interfaces import ITemplateRenderer
        minimal = self._getTemplatePath('minimal.txt')
        utility = TextTemplateRenderer(minimal)
        self._registerUtility(utility, ITemplateRenderer, name=minimal)
        result = self._callFUT(minimal)
        self.assertEqual(result.filename, minimal)
        reg = get_current_registry()
        self.assertEqual(reg.queryUtility(ITemplateRenderer, minimal), utility)
        
    def test_nonabs_unregistered(self):
        from repoze.bfg.threadlocal import get_current_registry
        from repoze.bfg.chameleon_text import TextTemplateRenderer
        from repoze.bfg.interfaces import ITemplateRenderer
        minimal = self._getTemplatePath('minimal.txt')
        reg = get_current_registry()
        self.assertEqual(reg.queryUtility(ITemplateRenderer, minimal), None)
        utility = TextTemplateRenderer(minimal)
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
        
        
        


