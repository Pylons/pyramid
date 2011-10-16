## come on python gimme some of that sweet, sweet -*- coding: utf-8 -*-

import unittest
from pyramid import testing
from pyramid.compat import text_
from pyramid.compat import text_type

class Base(object):
    def setUp(self):
        self.config = testing.setUp()
        self.config.begin()
        import os
        here = os.path.abspath(os.path.dirname(__file__))
        self.templates_dir = os.path.join(here, 'fixtures')

    def tearDown(self):
        self.config.end()

class Test_renderer_factory(Base, unittest.TestCase):
    def _callFUT(self, info):
        from pyramid.mako_templating import renderer_factory
        return renderer_factory(info)

    def test_no_directories(self):
        from pyramid.mako_templating import IMakoLookup
        info = DummyRendererInfo({
            'name':'pyramid.tests:fixtures/helloworld.mak',
            'package':None,
            'registry':self.config.registry,
            'settings':{},
            })
        renderer = self._callFUT(info)
        lookup = self.config.registry.getUtility(IMakoLookup)
        self.assertEqual(lookup.directories, [])
        self.assertEqual(lookup.filesystem_checks, False)
        self.assertEqual(renderer.path,
                         'pyramid.tests:fixtures/helloworld.mak')
        self.assertEqual(renderer.lookup, lookup)

    def test_no_lookup(self):
        from pyramid.mako_templating import IMakoLookup
        settings = {'mako.directories':self.templates_dir}
        info = DummyRendererInfo({
            'name':'helloworld.mak',
            'package':None,
            'registry':self.config.registry,
            'settings':settings,
            })
        renderer = self._callFUT(info)
        lookup = self.config.registry.getUtility(IMakoLookup)
        self.assertEqual(lookup.directories, [self.templates_dir])
        self.assertEqual(lookup.filesystem_checks, False)
        self.assertEqual(renderer.path, 'helloworld.mak')
        self.assertEqual(renderer.lookup, lookup)

    def test_composite_directories_path(self):
        from pyramid.mako_templating import IMakoLookup
        twice = '\n' + self.templates_dir + '\n' + self.templates_dir + '\n'
        settings = {'mako.directories':twice}
        info = DummyRendererInfo({
            'name':'helloworld.mak',
            'package':None,
            'registry':self.config.registry,
            'settings':settings,
            })
        self._callFUT(info)
        lookup = self.config.registry.getUtility(IMakoLookup)
        self.assertEqual(lookup.directories, [self.templates_dir]*2)

    def test_directories_list(self):
        import sys
        import os.path
        from pyramid.mako_templating import IMakoLookup
        settings = {'mako.directories':['a', 'b']}
        info = DummyRendererInfo({
            'name':'helloworld.mak',
            'package':None,
            'registry':self.config.registry,
            'settings':settings,
            })
        self._callFUT(info)
        lookup = self.config.registry.getUtility(IMakoLookup)
        module_path = os.path.dirname(
            sys.modules['__main__'].__file__).rstrip('.') # ./setup.py
        self.assertEqual(lookup.directories, [
            os.path.join(module_path, 'a'),
            os.path.join(module_path, 'b')])

    def test_with_module_directory_asset_spec(self):
        import os
        from pyramid.mako_templating import IMakoLookup
        module_directory = 'pyramid.tests:fixtures'
        settings = {'mako.directories':self.templates_dir,
                    'mako.module_directory':module_directory}
        info = DummyRendererInfo({
            'name':'helloworld.mak',
            'package':None,
            'registry':self.config.registry,
            'settings':settings,
            })
        self._callFUT(info)
        lookup = self.config.registry.getUtility(IMakoLookup)
        fixtures = os.path.join(os.path.dirname(__file__), 'fixtures')
        self.assertEqual(lookup.module_directory, fixtures)

    def test_with_module_directory_asset_abspath(self):
        import os
        from pyramid.mako_templating import IMakoLookup
        fixtures = os.path.join(os.path.dirname(__file__), 'fixtures')
        settings = {'mako.directories':self.templates_dir,
                    'mako.module_directory':fixtures}
        info = DummyRendererInfo({
            'name':'helloworld.mak',
            'package':None,
            'registry':self.config.registry,
            'settings':settings,
            })
        self._callFUT(info)
        lookup = self.config.registry.getUtility(IMakoLookup)
        self.assertEqual(lookup.module_directory, fixtures)

    def test_with_input_encoding(self):
        from pyramid.mako_templating import IMakoLookup
        settings = {'mako.directories':self.templates_dir,
                    'mako.input_encoding':'utf-16'}
        info = DummyRendererInfo({
            'name':'helloworld.mak',
            'package':None,
            'registry':self.config.registry,
            'settings':settings,
            })
        self._callFUT(info)
        lookup = self.config.registry.getUtility(IMakoLookup)
        self.assertEqual(lookup.template_args['input_encoding'], 'utf-16')
        
    def test_with_error_handler(self):
        from pyramid.mako_templating import IMakoLookup
        settings = {'mako.directories':self.templates_dir,
                    'mako.error_handler':'pyramid.tests'}
        import pyramid.tests
        info = DummyRendererInfo({
            'name':'helloworld.mak',
            'package':None,
            'registry':self.config.registry,
            'settings':settings,
            })
        self._callFUT(info)
        lookup = self.config.registry.getUtility(IMakoLookup)
        self.assertEqual(lookup.template_args['error_handler'], pyramid.tests)

    def test_with_preprocessor(self):
        from pyramid.mako_templating import IMakoLookup
        settings = {'mako.directories':self.templates_dir,
                    'mako.preprocessor':'pyramid.tests'}
        import pyramid.tests
        info = DummyRendererInfo({
            'name':'helloworld.mak',
            'package':None,
            'registry':self.config.registry,
            'settings':settings,
            })
        self._callFUT(info)
        lookup = self.config.registry.getUtility(IMakoLookup)
        self.assertEqual(lookup.template_args['preprocessor'], pyramid.tests)

    def test_with_default_filters(self):
        from pyramid.mako_templating import IMakoLookup
        settings = {'mako.directories':self.templates_dir,
                    'mako.default_filters':'\nh\ng\n\n'}
        info = DummyRendererInfo({
            'name':'helloworld.mak',
            'package':None,
            'registry':self.config.registry,
            'settings':settings,
            })
        self._callFUT(info)
        lookup = self.config.registry.getUtility(IMakoLookup)
        self.assertEqual(lookup.template_args['default_filters'], ['h', 'g'])

    def test_with_default_filters_list(self):
        from pyramid.mako_templating import IMakoLookup
        settings = {'mako.directories':self.templates_dir,
                    'mako.default_filters':['h', 'g']}
        info = DummyRendererInfo({
            'name':'helloworld.mak',
            'package':None,
            'registry':self.config.registry,
            'settings':settings,
            })
        self._callFUT(info)
        lookup = self.config.registry.getUtility(IMakoLookup)
        self.assertEqual(lookup.template_args['default_filters'], ['h', 'g'])

    def test_with_imports(self):
        from pyramid.mako_templating import IMakoLookup
        settings = {'mako.directories':self.templates_dir,
                    'mako.imports':'\none\ntwo\n\n'}
        info = DummyRendererInfo({
            'name':'helloworld.mak',
            'package':None,
            'registry':self.config.registry,
            'settings':settings,
            })
        self._callFUT(info)
        lookup = self.config.registry.getUtility(IMakoLookup)
        self.assertEqual(lookup.template_args['imports'], ['one', 'two'])

    def test_with_imports_list(self):
        from pyramid.mako_templating import IMakoLookup
        settings = {'mako.directories':self.templates_dir,
                    'mako.imports':['one', 'two']}
        info = DummyRendererInfo({
            'name':'helloworld.mak',
            'package':None,
            'registry':self.config.registry,
            'settings':settings,
            })
        self._callFUT(info)
        lookup = self.config.registry.getUtility(IMakoLookup)
        self.assertEqual(lookup.template_args['imports'], ['one', 'two'])

    def test_with_strict_undefined_true(self):
        from pyramid.mako_templating import IMakoLookup
        settings = {'mako.directories':self.templates_dir,
                    'mako.strict_undefined':'true'}
        info = DummyRendererInfo({
            'name':'helloworld.mak',
            'package':None,
            'registry':self.config.registry,
            'settings':settings,
            })
        self._callFUT(info)
        lookup = self.config.registry.getUtility(IMakoLookup)
        self.assertEqual(lookup.template_args['strict_undefined'], True)

    def test_with_strict_undefined_false(self):
        from pyramid.mako_templating import IMakoLookup
        settings = {'mako.directories':self.templates_dir,
                    'mako.strict_undefined':'false'}
        info = DummyRendererInfo({
            'name':'helloworld.mak',
            'package':None,
            'registry':self.config.registry,
            'settings':settings,
            })
        self._callFUT(info)
        lookup = self.config.registry.getUtility(IMakoLookup)
        self.assertEqual(lookup.template_args['strict_undefined'], False)

    def test_with_lookup(self):
        from pyramid.mako_templating import IMakoLookup
        lookup = dict()
        self.config.registry.registerUtility(lookup, IMakoLookup)
        info = DummyRendererInfo({
            'name':'helloworld.mak',
            'package':None,
            'registry':self.config.registry,
            'settings':{},
            })
        renderer = self._callFUT(info)
        self.assertEqual(renderer.lookup, lookup)
        self.assertEqual(renderer.path, 'helloworld.mak')

class MakoLookupTemplateRendererTests(Base, unittest.TestCase):
    def _getTargetClass(self):
        from pyramid.mako_templating import MakoLookupTemplateRenderer
        return MakoLookupTemplateRenderer

    def _makeOne(self, *arg, **kw):
        klass = self._getTargetClass()
        return klass(*arg, **kw)

    def test_instance_implements_ITemplate(self):
        from zope.interface.verify import verifyObject
        from pyramid.interfaces import ITemplateRenderer
        verifyObject(ITemplateRenderer, self._makeOne(None, None))

    def test_class_implements_ITemplate(self):
        from zope.interface.verify import verifyClass
        from pyramid.interfaces import ITemplateRenderer
        verifyClass(ITemplateRenderer, self._getTargetClass())

    def test_call(self):
        lookup = DummyLookup()
        instance = self._makeOne('path', lookup)
        result = instance({}, {'system':1})
        self.assertTrue(isinstance(result, text_type))
        self.assertEqual(result, text_('result'))

    def test_call_with_system_context(self):
        # lame
        lookup = DummyLookup()
        instance = self._makeOne('path', lookup)
        result = instance({}, {'context':1})
        self.assertTrue(isinstance(result, text_type))
        self.assertEqual(result, text_('result'))
        self.assertEqual(lookup.values, {'_context':1})

    def test_call_with_tuple_value(self):
        lookup = DummyLookup()
        instance = self._makeOne('path', lookup)
        result = instance(('fub', {}), {'context':1})
        self.assertEqual(lookup.deffed, 'fub')
        self.assertEqual(result, text_('result'))
        self.assertEqual(lookup.values, {'_context':1})

    def test_call_with_nondict_value(self):
        lookup = DummyLookup()
        instance = self._makeOne('path', lookup)
        self.assertRaises(ValueError, instance, None, {})

    def test_call_render_raises(self):
        from pyramid.mako_templating import MakoRenderingException
        lookup = DummyLookup(exc=NotImplementedError)
        instance = self._makeOne('path', lookup)
        try:
            instance({}, {})
        except MakoRenderingException as e:
            self.assertTrue('NotImplementedError' in e.text)
        else: # pragma: no cover
            raise AssertionError

    def test_implementation(self):
        lookup = DummyLookup()
        instance = self._makeOne('path', lookup)
        result = instance.implementation().render_unicode()
        self.assertTrue(isinstance(result, text_type))
        self.assertEqual(result, text_('result'))
        
class TestIntegration(unittest.TestCase):
    def setUp(self):
        import pyramid.mako_templating
        self.config = testing.setUp()
        self.config.add_settings({'mako.directories':
                                  'pyramid.tests:fixtures'})
        self.config.add_renderer('.mak',
                                 pyramid.mako_templating.renderer_factory)

    def tearDown(self):
        self.config.end()

    def test_render(self):
        from pyramid.renderers import render
        result = render('helloworld.mak', {'a':1}).replace('\r','')
        self.assertEqual(result, text_('\nHello föö\n', 'utf-8'))

    def test_render_from_fs(self):
        from pyramid.renderers import render
        self.config.add_settings({'reload_templates': True})
        result = render('helloworld.mak', {'a':1}).replace('\r','')
        self.assertEqual(result, text_('\nHello föö\n', 'utf-8'))
    
    def test_render_inheritance(self):
        from pyramid.renderers import render
        result = render('helloinherit.mak', {}).replace('\r','')
        self.assertEqual(result, text_('Layout\nHello World!\n'))

    def test_render_inheritance_pkg_spec(self):
        from pyramid.renderers import render
        result = render('hello_inherit_pkg.mak', {}).replace('\r','')
        self.assertEqual(result, text_('Layout\nHello World!\n'))

    def test_render_to_response(self):
        from pyramid.renderers import render_to_response
        result = render_to_response('helloworld.mak', {'a':1})
        self.assertEqual(result.ubody.replace('\r',''),
                         text_('\nHello föö\n', 'utf-8'))

    def test_render_to_response_pkg_spec(self):
        from pyramid.renderers import render_to_response
        result = render_to_response('pyramid.tests:fixtures/helloworld.mak',
                                    {'a':1})
        self.assertEqual(result.ubody.replace('\r', ''),
                         text_('\nHello föö\n', 'utf-8'))
    
    def test_render_with_abs_path(self):
        from pyramid.renderers import render
        result = render('/helloworld.mak', {'a':1}).replace('\r','')
        self.assertEqual(result, text_('\nHello föö\n', 'utf-8'))

    def test_get_renderer(self):
        from pyramid.renderers import get_renderer
        result = get_renderer('helloworld.mak')
        self.assertEqual(
            result.implementation().render_unicode().replace('\r',''),
            text_('\nHello föö\n', 'utf-8'))
    
    def test_template_not_found(self):
        from pyramid.renderers import render
        from mako.exceptions import TemplateLookupException
        self.assertRaises(TemplateLookupException, render,
                          'helloworld_not_here.mak', {})

    def test_template_default_escaping(self):
        from pyramid.renderers import render
        result = render('nonminimal.mak',
                        {'name':'<b>fred</b>'}).replace('\r','')
        self.assertEqual(result, text_('Hello, &lt;b&gt;fred&lt;/b&gt;!\n'))

class TestPkgResourceTemplateLookup(unittest.TestCase):
    def _makeOne(self, **kw):
        from pyramid.mako_templating import PkgResourceTemplateLookup
        return PkgResourceTemplateLookup(**kw)

    def get_fixturedir(self):
        import os
        import pyramid.tests
        return os.path.join(os.path.dirname(pyramid.tests.__file__), 'fixtures')

    def test_adjust_uri_not_asset_spec(self):
        inst = self._makeOne()
        result = inst.adjust_uri('a', None)
        self.assertEqual(result, '/a')

    def test_adjust_uri_asset_spec(self):
        inst = self._makeOne()
        result = inst.adjust_uri('a:b', None)
        self.assertEqual(result, 'a:b')

    def test_get_template_not_asset_spec(self):
        fixturedir = self.get_fixturedir()
        inst = self._makeOne(directories=[fixturedir])
        result = inst.get_template('helloworld.mak')
        self.assertFalse(result is None)
        
    def test_get_template_asset_spec_with_filesystem_checks(self):
        inst = self._makeOne(filesystem_checks=True)
        result = inst.get_template('pyramid.tests:fixtures/helloworld.mak')
        self.assertFalse(result is None)

    def test_get_template_asset_spec_missing(self):
        from mako.exceptions import TopLevelLookupException
        fixturedir = self.get_fixturedir()
        inst = self._makeOne(filesystem_checks=True, directories=[fixturedir])
        self.assertRaises(TopLevelLookupException, inst.get_template,
                          'pyramid.tests:fixtures/notthere.mak')

class TestMakoRenderingException(unittest.TestCase):
    def _makeOne(self, text):
        from pyramid.mako_templating import MakoRenderingException
        return MakoRenderingException(text)
    
    def test_repr_and_str(self):
        exc = self._makeOne('text')
        self.assertEqual(str(exc), 'text')
        self.assertEqual(repr(exc), 'text')

class DummyLookup(object):
    def __init__(self, exc=None):
        self.exc = exc
        
    def get_template(self, path):
        self.path = path
        return self

    def get_def(self, path):
        self.deffed = path
        return self

    def render_unicode(self, **values):
        if self.exc:
            raise self.exc
        self.values = values
        return text_('result')
        
class DummyRendererInfo(object):
    def __init__(self, kw):
        self.__dict__.update(kw)
        
