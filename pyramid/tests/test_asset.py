import unittest
from pyramid.testing import cleanUp

class TestOverrideProvider(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _getTargetClass(self):
        from pyramid.asset import OverrideProvider
        return OverrideProvider

    def _makeOne(self, module):
        klass = self._getTargetClass()
        return klass(module)

    def _registerOverrides(self, overrides, name='pyramid.tests'):
        from pyramid.interfaces import IPackageOverrides
        from pyramid.threadlocal import get_current_registry
        reg = get_current_registry()
        reg.registerUtility(overrides, IPackageOverrides, name=name)

    def test_get_resource_filename_no_overrides(self):
        import os
        resource_name = 'test_asset.py'
        import pyramid.tests
        provider = self._makeOne(pyramid.tests)
        here = os.path.dirname(os.path.abspath(__file__))
        expected = os.path.join(here, resource_name)
        result = provider.get_resource_filename(None, resource_name)
        self.assertEqual(result, expected)

    def test_get_resource_stream_no_overrides(self):
        import os
        resource_name = 'test_asset.py'
        import pyramid.tests
        provider = self._makeOne(pyramid.tests)
        here = os.path.dirname(os.path.abspath(__file__))
        expected = open(os.path.join(here, resource_name)).read()
        result = provider.get_resource_stream(None, resource_name)
        self.assertEqual(result.read(), expected)

    def test_get_resource_string_no_overrides(self):
        import os
        resource_name = 'test_asset.py'
        import pyramid.tests
        provider = self._makeOne(pyramid.tests)
        here = os.path.dirname(os.path.abspath(__file__))
        expected = open(os.path.join(here, resource_name)).read()
        result = provider.get_resource_string(None, resource_name)
        self.assertEqual(result, expected)

    def test_has_resource_no_overrides(self):
        resource_name = 'test_asset.py'
        import pyramid.tests
        provider = self._makeOne(pyramid.tests)
        result = provider.has_resource(resource_name)
        self.assertEqual(result, True)

    def test_resource_isdir_no_overrides(self):
        file_resource_name = 'test_asset.py'
        directory_resource_name = 'fixtures'
        import pyramid.tests
        provider = self._makeOne(pyramid.tests)
        result = provider.resource_isdir(file_resource_name)
        self.assertEqual(result, False)
        result = provider.resource_isdir(directory_resource_name)
        self.assertEqual(result, True)

    def test_resource_listdir_no_overrides(self):
        resource_name = 'fixtures'
        import pyramid.tests
        provider = self._makeOne(pyramid.tests)
        result = provider.resource_isdir(resource_name)
        self.failUnless(result)

    def test_get_resource_filename_override_returns_None(self):
        overrides = DummyOverrides(None)
        self._registerOverrides(overrides)
        import os
        resource_name = 'test_asset.py'
        import pyramid.tests
        provider = self._makeOne(pyramid.tests)
        here = os.path.dirname(os.path.abspath(__file__))
        expected = os.path.join(here, resource_name)
        result = provider.get_resource_filename(None, resource_name)
        self.assertEqual(result, expected)
        
    def test_get_resource_stream_override_returns_None(self):
        overrides = DummyOverrides(None)
        self._registerOverrides(overrides)
        import os
        resource_name = 'test_asset.py'
        import pyramid.tests
        provider = self._makeOne(pyramid.tests)
        here = os.path.dirname(os.path.abspath(__file__))
        expected = os.path.join(here, resource_name)
        result = provider.get_resource_filename(None, resource_name)
        self.assertEqual(result, expected)

    def test_get_resource_string_override_returns_None(self):
        overrides = DummyOverrides(None)
        self._registerOverrides(overrides)
        import os
        resource_name = 'test_asset.py'
        import pyramid.tests
        provider = self._makeOne(pyramid.tests)
        here = os.path.dirname(os.path.abspath(__file__))
        expected = os.path.join(here, resource_name)
        result = provider.get_resource_filename(None, resource_name)
        self.assertEqual(result, expected)

    def test_has_resource_override_returns_None(self):
        overrides = DummyOverrides(None)
        self._registerOverrides(overrides)
        resource_name = 'test_asset.py'
        import pyramid.tests
        provider = self._makeOne(pyramid.tests)
        result = provider.has_resource(resource_name)
        self.assertEqual(result, True)

    def test_resource_isdir_override_returns_None(self):
        overrides = DummyOverrides(None)
        self._registerOverrides(overrides)
        resource_name = 'fixtures'
        import pyramid.tests
        provider = self._makeOne(pyramid.tests)
        result = provider.resource_isdir(resource_name)
        self.assertEqual(result, True)

    def test_resource_listdir_override_returns_None(self):
        overrides = DummyOverrides(None)
        self._registerOverrides(overrides)
        resource_name = 'fixtures'
        import pyramid.tests
        provider = self._makeOne(pyramid.tests)
        result = provider.resource_listdir(resource_name)
        self.failUnless(result)

    def test_get_resource_filename_override_returns_value(self):
        overrides = DummyOverrides('value')
        import pyramid.tests
        self._registerOverrides(overrides)
        provider = self._makeOne(pyramid.tests)
        result = provider.get_resource_filename(None, 'test_asset.py')
        self.assertEqual(result, 'value')

    def test_get_resource_stream_override_returns_value(self):
        overrides = DummyOverrides('value')
        import pyramid.tests
        self._registerOverrides(overrides)
        provider = self._makeOne(pyramid.tests)
        result = provider.get_resource_stream(None, 'test_asset.py')
        self.assertEqual(result, 'value')

    def test_get_resource_string_override_returns_value(self):
        overrides = DummyOverrides('value')
        import pyramid.tests
        self._registerOverrides(overrides)
        provider = self._makeOne(pyramid.tests)
        result = provider.get_resource_string(None, 'test_asset.py')
        self.assertEqual(result, 'value')

    def test_has_resource_override_returns_True(self):
        overrides = DummyOverrides(True)
        import pyramid.tests
        self._registerOverrides(overrides)
        provider = self._makeOne(pyramid.tests)
        result = provider.has_resource('test_asset.py')
        self.assertEqual(result, True)

    def test_resource_isdir_override_returns_False(self):
        overrides = DummyOverrides(False)
        import pyramid.tests
        self._registerOverrides(overrides)
        provider = self._makeOne(pyramid.tests)
        result = provider.resource_isdir('fixtures')
        self.assertEqual(result, False)

    def test_resource_listdir_override_returns_values(self):
        overrides = DummyOverrides(['a'])
        import pyramid.tests
        self._registerOverrides(overrides)
        provider = self._makeOne(pyramid.tests)
        result = provider.resource_listdir('fixtures')
        self.assertEqual(result, ['a'])

class TestPackageOverrides(unittest.TestCase):
    def _getTargetClass(self):
        from pyramid.asset import PackageOverrides
        return PackageOverrides

    def _makeOne(self, package, pkg_resources=None):
        klass = self._getTargetClass()
        if pkg_resources is None:
            pkg_resources = DummyPkgResources()
        return klass(package, pkg_resources=pkg_resources)

    def test_ctor_package_already_has_loader_of_different_type(self):
        package = DummyPackage('package')
        package.__loader__ = True
        self.assertRaises(TypeError, self._makeOne, package)

    def test_ctor_package_already_has_loader_of_same_type(self):
        package = DummyPackage('package')
        package.__loader__ = self._makeOne(package)
        po = self._makeOne(package)
        self.assertEqual(package.__loader__, po)

    def test_ctor_sets_loader(self):
        package = DummyPackage('package')
        po = self._makeOne(package)
        self.assertEqual(package.__loader__, po)

    def test_ctor_registers_loader_type(self):
        from pyramid.resource import OverrideProvider
        dummy_pkg_resources = DummyPkgResources()
        package = DummyPackage('package')
        po = self._makeOne(package, dummy_pkg_resources)
        self.assertEqual(dummy_pkg_resources.registered, [(po.__class__,
                         OverrideProvider)])

    def test_ctor_sets_local_state(self):
        package = DummyPackage('package')
        po = self._makeOne(package)
        self.assertEqual(po.overrides, [])
        self.assertEqual(po.overridden_package_name, 'package')

    def test_insert_directory(self):
        from pyramid.resource import DirectoryOverride
        package = DummyPackage('package')
        po = self._makeOne(package)
        po.overrides= [None]
        po.insert('foo/', 'package', 'bar/')
        self.assertEqual(len(po.overrides), 2)
        override = po.overrides[0]
        self.assertEqual(override.__class__, DirectoryOverride)

    def test_insert_file(self):
        from pyramid.resource import FileOverride
        package = DummyPackage('package')
        po = self._makeOne(package)
        po.overrides= [None]
        po.insert('foo.pt', 'package', 'bar.pt')
        self.assertEqual(len(po.overrides), 2)
        override = po.overrides[0]
        self.assertEqual(override.__class__, FileOverride)

    def test_search_path(self):
        overrides = [ DummyOverride(None), DummyOverride(('package', 'name'))]
        package = DummyPackage('package')
        po = self._makeOne(package)
        po.overrides= overrides
        self.assertEqual(list(po.search_path('whatever')),
                         [('package', 'name')])

    def test_get_filename(self):
        import os
        overrides = [ DummyOverride(None), DummyOverride(
            ('pyramid.tests', 'test_asset.py'))]
        package = DummyPackage('package')
        po = self._makeOne(package)
        po.overrides= overrides
        here = os.path.dirname(os.path.abspath(__file__))
        expected = os.path.join(here, 'test_asset.py')
        self.assertEqual(po.get_filename('whatever'), expected)
        
    def test_get_stream(self):
        import os
        overrides = [ DummyOverride(None), DummyOverride(
            ('pyramid.tests', 'test_asset.py'))]
        package = DummyPackage('package')
        po = self._makeOne(package)
        po.overrides= overrides
        here = os.path.dirname(os.path.abspath(__file__))
        expected = open(os.path.join(here, 'test_asset.py')).read()
        self.assertEqual(po.get_stream('whatever').read(), expected)
        
    def test_get_string(self):
        import os
        overrides = [ DummyOverride(None), DummyOverride(
            ('pyramid.tests', 'test_asset.py'))]
        package = DummyPackage('package')
        po = self._makeOne(package)
        po.overrides= overrides
        here = os.path.dirname(os.path.abspath(__file__))
        expected = open(os.path.join(here, 'test_asset.py')).read()
        self.assertEqual(po.get_string('whatever'), expected)
        
    def test_has_resource(self):
        overrides = [ DummyOverride(None), DummyOverride(
            ('pyramid.tests', 'test_asset.py'))]
        package = DummyPackage('package')
        po = self._makeOne(package)
        po.overrides= overrides
        self.assertEqual(po.has_resource('whatever'), True)

    def test_isdir_false(self):
        overrides = [ DummyOverride(
            ('pyramid.tests', 'test_asset.py'))]
        package = DummyPackage('package')
        po = self._makeOne(package)
        po.overrides= overrides
        self.assertEqual(po.isdir('whatever'), False)
        
    def test_isdir_true(self):
        overrides = [ DummyOverride(
            ('pyramid.tests', 'fixtures'))]
        package = DummyPackage('package')
        po = self._makeOne(package)
        po.overrides= overrides
        self.assertEqual(po.isdir('whatever'), True)

    def test_listdir(self):
        overrides = [ DummyOverride(
            ('pyramid.tests', 'fixtures'))]
        package = DummyPackage('package')
        po = self._makeOne(package)
        po.overrides= overrides
        self.failUnless(po.listdir('whatever'))

class TestDirectoryOverride(unittest.TestCase):
    def _getTargetClass(self):
        from pyramid.asset import DirectoryOverride
        return DirectoryOverride

    def _makeOne(self, path, package, prefix):
        klass = self._getTargetClass()
        return klass(path, package, prefix)

    def test_it_match(self):
        o = self._makeOne('foo/', 'package', 'bar/')
        result = o('foo/something.pt')
        self.assertEqual(result, ('package', 'bar/something.pt'))
        
    def test_it_no_match(self):
        o = self._makeOne('foo/', 'package', 'bar/')
        result = o('baz/notfound.pt')
        self.assertEqual(result, None)

class Test_resolve_asset_spec(unittest.TestCase):
    def _callFUT(self, spec, package_name='__main__'):
        from pyramid.resource import resolve_asset_spec
        return resolve_asset_spec(spec, package_name)

    def test_abspath(self):
        import os
        here = os.path.dirname(__file__)
        path = os.path.abspath(here)
        package_name, filename = self._callFUT(path, 'apackage')
        self.assertEqual(filename, path)
        self.assertEqual(package_name, None)

    def test_rel_spec(self):
        pkg = 'pyramid.tests'
        path = 'test_asset.py'
        package_name, filename = self._callFUT(path, pkg)
        self.assertEqual(package_name, 'pyramid.tests')
        self.assertEqual(filename, 'test_asset.py')
        
    def test_abs_spec(self):
        pkg = 'pyramid.tests'
        path = 'pyramid.nottests:test_asset.py'
        package_name, filename = self._callFUT(path, pkg)
        self.assertEqual(package_name, 'pyramid.nottests')
        self.assertEqual(filename, 'test_asset.py')

    def test_package_name_is_None(self):
        pkg = None
        path = 'test_asset.py'
        package_name, filename = self._callFUT(path, pkg)
        self.assertEqual(package_name, None)
        self.assertEqual(filename, 'test_asset.py')

    def test_package_name_is_package_object(self):
        import pyramid.tests
        pkg = pyramid.tests
        path = 'test_asset.py'
        package_name, filename = self._callFUT(path, pkg)
        self.assertEqual(package_name, 'pyramid.tests')
        self.assertEqual(filename, 'test_asset.py')


class TestFileOverride(unittest.TestCase):
    def _getTargetClass(self):
        from pyramid.asset import FileOverride
        return FileOverride

    def _makeOne(self, path, package, prefix):
        klass = self._getTargetClass()
        return klass(path, package, prefix)

    def test_it_match(self):
        o = self._makeOne('foo.pt', 'package', 'bar.pt')
        result = o('foo.pt')
        self.assertEqual(result, ('package', 'bar.pt'))
        
    def test_it_no_match(self):
        o = self._makeOne('foo.pt', 'package', 'bar.pt')
        result = o('notfound.pt')
        self.assertEqual(result, None)

class Test_abspath_from_asset_spec(unittest.TestCase):
    def _callFUT(self, spec, pname='__main__'):
        from pyramid.resource import abspath_from_asset_spec
        return abspath_from_asset_spec(spec, pname)

    def test_pname_is_None_before_resolve_asset_spec(self):
        result = self._callFUT('abc', None)
        self.assertEqual(result, 'abc')

    def test_pname_is_None_after_resolve_asset_spec(self):
        result = self._callFUT('/abc', '__main__')
        self.assertEqual(result, '/abc')

    def test_pkgrelative(self):
        import os
        here = os.path.dirname(__file__)
        path = os.path.abspath(here)
        result = self._callFUT('abc', 'pyramid.tests')
        self.assertEqual(result, os.path.join(path, 'abc'))

class Test_asset_spec_from_abspath(unittest.TestCase):
    def _callFUT(self, abspath, package):
        from pyramid.asset import asset_spec_from_abspath
        return asset_spec_from_abspath(abspath, package)

    def test_package_name_is_main(self):
        pkg = DummyPackage('__main__')
        result = self._callFUT('abspath', pkg)
        self.assertEqual(result, 'abspath')

    def test_abspath_startswith_package_path(self):
        import os
        abspath = os.path.dirname(__file__) + '/fixtureapp'
        pkg = DummyPackage('pyramid.tests')
        pkg.__file__ = 'file'
        result = self._callFUT(abspath, pkg)
        self.assertEqual(result, 'pyramid:fixtureapp')

    def test_abspath_doesnt_startwith_package_path(self):
        import os
        abspath = os.path.dirname(__file__)
        pkg = DummyPackage('pyramid.tests')
        result = self._callFUT(abspath, pkg)
        self.assertEqual(result, abspath)
        

class DummyOverride:
    def __init__(self, result):
        self.result = result

    def __call__(self, resource_name):
        return self.result

class DummyOverrides:
    def __init__(self, result):
        self.result = result

    def get_filename(self, resource_name):
        return self.result

    listdir = isdir = has_resource = get_stream = get_string = get_filename
    
class DummyPkgResources:
    def __init__(self):
        self.registered = []

    def register_loader_type(self, typ, inst):
        self.registered.append((typ, inst))
        
class DummyPackage:
    def __init__(self, name):
        self.__name__ = name
    
