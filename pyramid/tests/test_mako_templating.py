## come on python gimme some of that sweet, sweet -*- coding: utf-8 -*-

import shutil
import tempfile
import unittest

from pyramid import testing

from pyramid.compat import (
    text_,
    text_type,
    )

class Base(object):
    def setUp(self):
        self.config = testing.setUp()
        self.config.begin()
        import os
        here = os.path.abspath(os.path.dirname(__file__))
        self.templates_dir = os.path.join(here, 'fixtures')

    def tearDown(self):
        self.config.end()

def maybe_unittest():
    # The latest release of MarkupSafe (0.17) which is used by Mako is
    # incompatible with Python 3.2, so we skip these tests if we cannot
    # import a Mako module which ends up importing MarkupSafe.  Note that
    # this version of MarkupSafe *is* compatible with Python 2.6, 2.7, and 3.3,
    # so these tests should not be skipped on those platforms.
    try:
        import mako.lookup
    except (ImportError, SyntaxError, AttributeError): # pragma: no cover
        return object
    else:
        return unittest.TestCase

class Test_renderer_factory(Base, maybe_unittest()):
    def _callFUT(self, info):
        from pyramid.mako_templating import renderer_factory
        return renderer_factory(info)

    def _getLookup(self, name='mako.'):
        from pyramid.mako_templating import IMakoLookup
        return self.config.registry.getUtility(IMakoLookup, name=name)

    def test_hyphen_filenames(self):
        from pyramid.mako_templating import renderer_factory

        info = DummyRendererInfo({
            'name':'app:moon-and-world.mak',
            'package':None,
            'registry':self.config.registry,
            'settings':{},
            'type': ''
        })

        result = renderer_factory(info)
        self.assertEqual(result.path, 'app:moon-and-world.mak')

    def test_no_directories(self):
        info = DummyRendererInfo({
            'name':'pyramid.tests:fixtures/helloworld.mak',
            'package':None,
            'registry':self.config.registry,
            'settings':{},
            })
        renderer = self._callFUT(info)
        lookup = self._getLookup()
        self.assertEqual(lookup.directories, [])
        self.assertEqual(lookup.filesystem_checks, False)
        self.assertEqual(renderer.path,
                         'pyramid.tests:fixtures/helloworld.mak')
        self.assertEqual(renderer.lookup, lookup)

    def test_no_lookup(self):
        settings = {'mako.directories':self.templates_dir}
        info = DummyRendererInfo({
            'name':'helloworld.mak',
            'package':None,
            'registry':self.config.registry,
            'settings':settings,
            })
        renderer = self._callFUT(info)
        lookup = self._getLookup()
        self.assertEqual(lookup.directories, [self.templates_dir])
        self.assertEqual(lookup.filesystem_checks, False)
        self.assertEqual(renderer.path, 'helloworld.mak')
        self.assertEqual(renderer.lookup, lookup)

    def test_composite_directories_path(self):
        twice = '\n' + self.templates_dir + '\n' + self.templates_dir + '\n'
        settings = {'mako.directories':twice}
        info = DummyRendererInfo({
            'name':'helloworld.mak',
            'package':None,
            'registry':self.config.registry,
            'settings':settings,
            })
        self._callFUT(info)
        lookup = self._getLookup()
        self.assertEqual(lookup.directories, [self.templates_dir]*2)

    def test_directories_list(self):
        import sys
        import os.path
        settings = {'mako.directories':['a', 'b']}
        info = DummyRendererInfo({
            'name':'helloworld.mak',
            'package':None,
            'registry':self.config.registry,
            'settings':settings,
            })
        self._callFUT(info)
        lookup = self._getLookup()
        module_path = os.path.dirname(
            sys.modules['__main__'].__file__).rstrip('.') # ./setup.py
        self.assertEqual(lookup.directories, [
            os.path.join(module_path, 'a'),
            os.path.join(module_path, 'b')])

    def test_with_module_directory_asset_spec(self):
        import os
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
        lookup = self._getLookup()
        fixtures = os.path.join(os.path.dirname(__file__), 'fixtures')
        self.assertEqual(lookup.module_directory, fixtures)

    def test_with_module_directory_asset_abspath(self):
        import os
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
        lookup = self._getLookup()
        self.assertEqual(lookup.module_directory, fixtures)

    def test_with_input_encoding(self):
        settings = {'mako.directories':self.templates_dir,
                    'mako.input_encoding':'utf-16'}
        info = DummyRendererInfo({
            'name':'helloworld.mak',
            'package':None,
            'registry':self.config.registry,
            'settings':settings,
            })
        self._callFUT(info)
        lookup = self._getLookup()
        self.assertEqual(lookup.template_args['input_encoding'], 'utf-16')

    def test_with_error_handler(self):
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
        lookup = self._getLookup()
        self.assertEqual(lookup.template_args['error_handler'], pyramid.tests)

    def test_with_preprocessor(self):
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
        lookup = self._getLookup()
        self.assertEqual(lookup.template_args['preprocessor'], pyramid.tests)

    def test_with_default_filters(self):
        settings = {'mako.directories':self.templates_dir,
                    'mako.default_filters':'\nh\ng\n\n'}
        info = DummyRendererInfo({
            'name':'helloworld.mak',
            'package':None,
            'registry':self.config.registry,
            'settings':settings,
            })
        self._callFUT(info)
        lookup = self._getLookup()
        self.assertEqual(lookup.template_args['default_filters'], ['h', 'g'])

    def test_with_default_filters_list(self):
        settings = {'mako.directories':self.templates_dir,
                    'mako.default_filters':['h', 'g']}
        info = DummyRendererInfo({
            'name':'helloworld.mak',
            'package':None,
            'registry':self.config.registry,
            'settings':settings,
            })
        self._callFUT(info)
        lookup = self._getLookup()
        self.assertEqual(lookup.template_args['default_filters'], ['h', 'g'])

    def test_with_imports(self):
        settings = {'mako.directories':self.templates_dir,
                    'mako.imports':'\none\ntwo\n\n'}
        info = DummyRendererInfo({
            'name':'helloworld.mak',
            'package':None,
            'registry':self.config.registry,
            'settings':settings,
            })
        self._callFUT(info)
        lookup = self._getLookup()
        self.assertEqual(lookup.template_args['imports'], ['one', 'two'])

    def test_with_imports_list(self):
        settings = {'mako.directories':self.templates_dir,
                    'mako.imports':['one', 'two']}
        info = DummyRendererInfo({
            'name':'helloworld.mak',
            'package':None,
            'registry':self.config.registry,
            'settings':settings,
            })
        self._callFUT(info)
        lookup = self._getLookup()
        self.assertEqual(lookup.template_args['imports'], ['one', 'two'])

    def test_with_strict_undefined_true(self):
        settings = {'mako.directories':self.templates_dir,
                    'mako.strict_undefined':'true'}
        info = DummyRendererInfo({
            'name':'helloworld.mak',
            'package':None,
            'registry':self.config.registry,
            'settings':settings,
            })
        self._callFUT(info)
        lookup = self._getLookup()
        self.assertEqual(lookup.template_args['strict_undefined'], True)

    def test_with_strict_undefined_false(self):
        settings = {'mako.directories':self.templates_dir,
                    'mako.strict_undefined':'false'}
        info = DummyRendererInfo({
            'name':'helloworld.mak',
            'package':None,
            'registry':self.config.registry,
            'settings':settings,
            })
        self._callFUT(info)
        lookup = self._getLookup()
        self.assertEqual(lookup.template_args['strict_undefined'], False)

    def test_with_lookup(self):
        from pyramid.mako_templating import IMakoLookup
        lookup = dict()
        self.config.registry.registerUtility(lookup, IMakoLookup, name='mako.')
        info = DummyRendererInfo({
            'name':'helloworld.mak',
            'package':None,
            'registry':self.config.registry,
            'settings':{},
            })
        renderer = self._callFUT(info)
        self.assertEqual(renderer.lookup, lookup)
        self.assertEqual(renderer.path, 'helloworld.mak')

    def test_space_dot_name(self):
        from pyramid.mako_templating import renderer_factory

        info = DummyRendererInfo({
            'name':'hello .world.mako',
            'package':None,
            'registry':self.config.registry,
            'settings':{},
        })

        result = renderer_factory(info)
        self.assertEqual(result.path, 'hello .world.mako')
        self.assertTrue(result.defname is None)

    def test_space_dot_name_def(self):
        from pyramid.mako_templating import renderer_factory

        info = DummyRendererInfo({
            'name':'hello .world#comp.mako',
            'package':None,
            'registry':self.config.registry,
            'settings':{},
            })

        result = renderer_factory(info)
        self.assertEqual(result.path, 'hello .world.mako')
        self.assertEqual(result.defname, 'comp')

class MakoRendererFactoryHelperTests(Base, maybe_unittest()):
    def _getTargetClass(self):
        from pyramid.mako_templating import MakoRendererFactoryHelper
        return MakoRendererFactoryHelper

    def _makeOne(self, *arg, **kw):
        klass = self._getTargetClass()
        return klass(*arg, **kw)

    def _getLookup(self, name='mako.'):
        from pyramid.mako_templating import IMakoLookup
        return self.config.registry.getUtility(IMakoLookup, name=name)

    def test_no_settings_prefix(self):
        settings = {'foo.directories':self.templates_dir}
        info = DummyRendererInfo({
            'name':'helloworld.mak',
            'package':None,
            'registry':self.config.registry,
            'settings':settings,
            'type':'foo',
            })
        helper = self._makeOne()
        renderer = helper(info)
        lookup = self._getLookup('foo.')
        self.assertEqual(lookup.directories, [self.templates_dir])
        self.assertEqual(lookup.filesystem_checks, False)
        self.assertEqual(renderer.path, 'helloworld.mak')
        self.assertEqual(renderer.lookup, lookup)

    def test_custom_settings_prefix(self):
        settings = {'bar.directories':self.templates_dir}
        info = DummyRendererInfo({
            'name':'helloworld.mak',
            'package':None,
            'registry':self.config.registry,
            'settings':settings,
            'type':'foo',
            })
        helper = self._makeOne('bar.')
        renderer = helper(info)
        lookup = self._getLookup('bar.')
        self.assertEqual(lookup.directories, [self.templates_dir])
        self.assertEqual(lookup.filesystem_checks, False)
        self.assertEqual(renderer.path, 'helloworld.mak')
        self.assertEqual(renderer.lookup, lookup)

class MakoLookupTemplateRendererTests(Base, maybe_unittest()):
    def _getTargetClass(self):
        from pyramid.mako_templating import MakoLookupTemplateRenderer
        return MakoLookupTemplateRenderer

    def _makeOne(self, *arg, **kw):
        klass = self._getTargetClass()
        return klass(*arg, **kw)

    def test_instance_implements_ITemplate(self):
        from zope.interface.verify import verifyObject
        from pyramid.interfaces import ITemplateRenderer
        verifyObject(ITemplateRenderer, self._makeOne(None, None, None))

    def test_class_implements_ITemplate(self):
        from zope.interface.verify import verifyClass
        from pyramid.interfaces import ITemplateRenderer
        verifyClass(ITemplateRenderer, self._getTargetClass())

    def test_call(self):
        lookup = DummyLookup()
        instance = self._makeOne('path', None, lookup)
        result = instance({}, {'system':1})
        self.assertTrue(isinstance(result, text_type))
        self.assertEqual(result, text_('result'))

    def test_call_with_system_context(self):
        # lame
        lookup = DummyLookup()
        instance = self._makeOne('path', None, lookup)
        result = instance({}, {'context':1})
        self.assertTrue(isinstance(result, text_type))
        self.assertEqual(result, text_('result'))
        self.assertEqual(lookup.values, {'_context':1})

    def test_call_with_tuple_value(self):
        lookup = DummyLookup()
        instance = self._makeOne('path', None, lookup)
        result = instance(('fub', {}), {'context':1})
        self.assertEqual(lookup.deffed, 'fub')
        self.assertEqual(result, text_('result'))
        self.assertEqual(lookup.values, {'_context':1})

    def test_call_with_defname(self):
        lookup = DummyLookup()
        instance = self._makeOne('path', 'defname', lookup)
        result = instance({}, {'system':1})
        self.assertTrue(isinstance(result, text_type))
        self.assertEqual(result, text_('result'))

    def test_call_with_defname_with_tuple_value(self):
        lookup = DummyLookup()
        instance = self._makeOne('path', 'defname', lookup)
        result = instance(('defname', {}), {'context':1})
        self.assertEqual(lookup.deffed, 'defname')
        self.assertEqual(result, text_('result'))
        self.assertEqual(lookup.values, {'_context':1})

    def test_call_with_defname_with_tuple_value_twice(self):
        lookup = DummyLookup()
        instance1 = self._makeOne('path', 'defname', lookup)
        result1 = instance1(('defname1', {}), {'context':1})
        self.assertEqual(lookup.deffed, 'defname1')
        self.assertEqual(result1, text_('result'))
        self.assertEqual(lookup.values, {'_context':1})
        instance2 = self._makeOne('path', 'defname', lookup)
        result2 = instance2(('defname2', {}), {'context':2})
        self.assertNotEqual(lookup.deffed, 'defname1')
        self.assertEqual(lookup.deffed, 'defname2')
        self.assertEqual(result2, text_('result'))
        self.assertEqual(lookup.values, {'_context':2})


    def test_call_with_nondict_value(self):
        lookup = DummyLookup()
        instance = self._makeOne('path', None, lookup)
        self.assertRaises(ValueError, instance, None, {})

    def test_call_render_raises(self):
        from pyramid.mako_templating import MakoRenderingException
        lookup = DummyLookup(exc=NotImplementedError)
        instance = self._makeOne('path', None, lookup)
        try:
            instance({}, {})
        except MakoRenderingException as e:
            self.assertTrue('NotImplementedError' in e.text)
        else: # pragma: no cover
            raise AssertionError

    def test_implementation(self):
        lookup = DummyLookup()
        instance = self._makeOne('path', None, lookup)
        result = instance.implementation().render_unicode()
        self.assertTrue(isinstance(result, text_type))
        self.assertEqual(result, text_('result'))

class TestIntegration(maybe_unittest()):
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

    def test_render_namespace(self):
        from pyramid.renderers import render
        result = render('hellocompo.mak', {}).replace('\r','')
        self.assertEqual(result, text_('\nNamespace\nHello \nWorld!\n'))

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

class TestPkgResourceTemplateLookup(maybe_unittest()):
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

    def test_adjust_uri_asset_spec_with_modified_asset_spec(self):
        inst = self._makeOne()
        result = inst.adjust_uri('a$b', None)
        self.assertEqual(result, 'a:b')

    def test_adjust_uri_not_asset_spec_with_relativeto_asset_spec(self):
        inst = self._makeOne()
        result = inst.adjust_uri('c', 'a:b')
        self.assertEqual(result, 'a:c')

    def test_adjust_uri_not_asset_spec_with_relativeto_modified_asset_spec(self):
        inst = self._makeOne()
        result = inst.adjust_uri('c', 'a$b')
        self.assertEqual(result, 'a:c')

    def test_adjust_uri_not_asset_spec_with_relativeto_not_asset_spec(self):
        inst = self._makeOne()
        result = inst.adjust_uri('b', '../a')
        self.assertEqual(result, '../b')

    def test_adjust_uri_not_asset_spec_abs_with_relativeto_asset_spec(self):
        inst = self._makeOne()
        result = inst.adjust_uri('/c', 'a:b')
        self.assertEqual(result, '/c')

    def test_adjust_uri_asset_spec_with_relativeto_not_asset_spec_abs(self):
        inst = self._makeOne()
        result = inst.adjust_uri('a:b', '/c')
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

    def test_get_template_asset_spec_with_module_dir(self):
        tmpdir = tempfile.mkdtemp()
        try:
            inst = self._makeOne(module_directory=tmpdir)
            result = inst.get_template('pyramid.tests:fixtures/helloworld.mak')
            self.assertFalse(result is None)
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

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

