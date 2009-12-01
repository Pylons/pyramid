import unittest
from repoze.bfg.testing import cleanUp

class TestOverrideProvider(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _getTargetClass(self):
        from repoze.bfg.resource import OverrideProvider
        return OverrideProvider

    def _makeOne(self, module):
        klass = self._getTargetClass()
        return klass(module)

    def _registerOverrides(self, overrides, name='repoze.bfg.tests'):
        from repoze.bfg.interfaces import IPackageOverrides
        from repoze.bfg.threadlocal import get_current_registry
        reg = get_current_registry()
        reg.registerUtility(overrides, IPackageOverrides, name=name)

    def test_get_resource_filename_no_overrides(self):
        import os
        resource_name = 'test_resource.py'
        import repoze.bfg.tests
        provider = self._makeOne(repoze.bfg.tests)
        here = os.path.dirname(os.path.abspath(__file__))
        expected = os.path.join(here, resource_name)
        result = provider.get_resource_filename(None, resource_name)
        self.assertEqual(result, expected)

    def test_get_resource_stream_no_overrides(self):
        import os
        resource_name = 'test_resource.py'
        import repoze.bfg.tests
        provider = self._makeOne(repoze.bfg.tests)
        here = os.path.dirname(os.path.abspath(__file__))
        expected = open(os.path.join(here, resource_name)).read()
        result = provider.get_resource_stream(None, resource_name)
        self.assertEqual(result.read(), expected)

    def test_get_resource_string_no_overrides(self):
        import os
        resource_name = 'test_resource.py'
        import repoze.bfg.tests
        provider = self._makeOne(repoze.bfg.tests)
        here = os.path.dirname(os.path.abspath(__file__))
        expected = open(os.path.join(here, resource_name)).read()
        result = provider.get_resource_string(None, resource_name)
        self.assertEqual(result, expected)

    def test_has_resource_no_overrides(self):
        resource_name = 'test_resource.py'
        import repoze.bfg.tests
        provider = self._makeOne(repoze.bfg.tests)
        result = provider.has_resource(resource_name)
        self.assertEqual(result, True)

    def test_resource_isdir_no_overrides(self):
        file_resource_name = 'test_resource.py'
        directory_resource_name = 'fixtures'
        import repoze.bfg.tests
        provider = self._makeOne(repoze.bfg.tests)
        result = provider.resource_isdir(file_resource_name)
        self.assertEqual(result, False)
        result = provider.resource_isdir(directory_resource_name)
        self.assertEqual(result, True)

    def test_resource_listdir_no_overrides(self):
        resource_name = 'fixtures'
        import repoze.bfg.tests
        provider = self._makeOne(repoze.bfg.tests)
        result = provider.resource_isdir(resource_name)
        self.failUnless(result)

    def test_get_resource_filename_override_returns_None(self):
        overrides = DummyOverrides(None)
        self._registerOverrides(overrides)
        import os
        resource_name = 'test_resource.py'
        import repoze.bfg.tests
        provider = self._makeOne(repoze.bfg.tests)
        here = os.path.dirname(os.path.abspath(__file__))
        expected = os.path.join(here, resource_name)
        result = provider.get_resource_filename(None, resource_name)
        self.assertEqual(result, expected)
        
    def test_get_resource_stream_override_returns_None(self):
        overrides = DummyOverrides(None)
        self._registerOverrides(overrides)
        import os
        resource_name = 'test_resource.py'
        import repoze.bfg.tests
        provider = self._makeOne(repoze.bfg.tests)
        here = os.path.dirname(os.path.abspath(__file__))
        expected = os.path.join(here, resource_name)
        result = provider.get_resource_filename(None, resource_name)
        self.assertEqual(result, expected)

    def test_get_resource_string_override_returns_None(self):
        overrides = DummyOverrides(None)
        self._registerOverrides(overrides)
        import os
        resource_name = 'test_resource.py'
        import repoze.bfg.tests
        provider = self._makeOne(repoze.bfg.tests)
        here = os.path.dirname(os.path.abspath(__file__))
        expected = os.path.join(here, resource_name)
        result = provider.get_resource_filename(None, resource_name)
        self.assertEqual(result, expected)

    def test_has_resource_override_returns_None(self):
        overrides = DummyOverrides(None)
        self._registerOverrides(overrides)
        resource_name = 'test_resource.py'
        import repoze.bfg.tests
        provider = self._makeOne(repoze.bfg.tests)
        result = provider.has_resource(resource_name)
        self.assertEqual(result, True)

    def test_resource_isdir_override_returns_None(self):
        overrides = DummyOverrides(None)
        self._registerOverrides(overrides)
        resource_name = 'fixtures'
        import repoze.bfg.tests
        provider = self._makeOne(repoze.bfg.tests)
        result = provider.resource_isdir(resource_name)
        self.assertEqual(result, True)

    def test_resource_listdir_override_returns_None(self):
        overrides = DummyOverrides(None)
        self._registerOverrides(overrides)
        resource_name = 'fixtures'
        import repoze.bfg.tests
        provider = self._makeOne(repoze.bfg.tests)
        result = provider.resource_listdir(resource_name)
        self.failUnless(result)

    def test_get_resource_filename_override_returns_value(self):
        overrides = DummyOverrides('value')
        import repoze.bfg.tests
        self._registerOverrides(overrides)
        provider = self._makeOne(repoze.bfg.tests)
        result = provider.get_resource_filename(None, 'test_resource.py')
        self.assertEqual(result, 'value')

    def test_get_resource_stream_override_returns_value(self):
        overrides = DummyOverrides('value')
        import repoze.bfg.tests
        self._registerOverrides(overrides)
        provider = self._makeOne(repoze.bfg.tests)
        result = provider.get_resource_stream(None, 'test_resource.py')
        self.assertEqual(result, 'value')

    def test_get_resource_string_override_returns_value(self):
        overrides = DummyOverrides('value')
        import repoze.bfg.tests
        self._registerOverrides(overrides)
        provider = self._makeOne(repoze.bfg.tests)
        result = provider.get_resource_string(None, 'test_resource.py')
        self.assertEqual(result, 'value')

    def test_has_resource_override_returns_True(self):
        overrides = DummyOverrides(True)
        import repoze.bfg.tests
        self._registerOverrides(overrides)
        provider = self._makeOne(repoze.bfg.tests)
        result = provider.has_resource('test_resource.py')
        self.assertEqual(result, True)

    def test_resource_isdir_override_returns_False(self):
        overrides = DummyOverrides(False)
        import repoze.bfg.tests
        self._registerOverrides(overrides)
        provider = self._makeOne(repoze.bfg.tests)
        result = provider.resource_isdir('fixtures')
        self.assertEqual(result, False)

    def test_resource_listdir_override_returns_values(self):
        overrides = DummyOverrides(['a'])
        import repoze.bfg.tests
        self._registerOverrides(overrides)
        provider = self._makeOne(repoze.bfg.tests)
        result = provider.resource_listdir('fixtures')
        self.assertEqual(result, ['a'])

class TestPackageOverrides(unittest.TestCase):
    def _getTargetClass(self):
        from repoze.bfg.resource import PackageOverrides
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
        from repoze.bfg.resource import OverrideProvider
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
        from repoze.bfg.resource import DirectoryOverride
        package = DummyPackage('package')
        po = self._makeOne(package)
        po.overrides= [None]
        po.insert('foo/', 'package', 'bar/')
        self.assertEqual(len(po.overrides), 2)
        override = po.overrides[0]
        self.assertEqual(override.__class__, DirectoryOverride)

    def test_insert_file(self):
        from repoze.bfg.resource import FileOverride
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
            ('repoze.bfg.tests', 'test_resource.py'))]
        package = DummyPackage('package')
        po = self._makeOne(package)
        po.overrides= overrides
        here = os.path.dirname(os.path.abspath(__file__))
        expected = os.path.join(here, 'test_resource.py')
        self.assertEqual(po.get_filename('whatever'), expected)
        
    def test_get_stream(self):
        import os
        overrides = [ DummyOverride(None), DummyOverride(
            ('repoze.bfg.tests', 'test_resource.py'))]
        package = DummyPackage('package')
        po = self._makeOne(package)
        po.overrides= overrides
        here = os.path.dirname(os.path.abspath(__file__))
        expected = open(os.path.join(here, 'test_resource.py')).read()
        self.assertEqual(po.get_stream('whatever').read(), expected)
        
    def test_get_string(self):
        import os
        overrides = [ DummyOverride(None), DummyOverride(
            ('repoze.bfg.tests', 'test_resource.py'))]
        package = DummyPackage('package')
        po = self._makeOne(package)
        po.overrides= overrides
        here = os.path.dirname(os.path.abspath(__file__))
        expected = open(os.path.join(here, 'test_resource.py')).read()
        self.assertEqual(po.get_string('whatever'), expected)
        
    def test_has_resource(self):
        overrides = [ DummyOverride(None), DummyOverride(
            ('repoze.bfg.tests', 'test_resource.py'))]
        package = DummyPackage('package')
        po = self._makeOne(package)
        po.overrides= overrides
        self.assertEqual(po.has_resource('whatever'), True)

    def test_isdir_false(self):
        overrides = [ DummyOverride(
            ('repoze.bfg.tests', 'test_resource.py'))]
        package = DummyPackage('package')
        po = self._makeOne(package)
        po.overrides= overrides
        self.assertEqual(po.isdir('whatever'), False)
        
    def test_isdir_true(self):
        overrides = [ DummyOverride(
            ('repoze.bfg.tests', 'fixtures'))]
        package = DummyPackage('package')
        po = self._makeOne(package)
        po.overrides= overrides
        self.assertEqual(po.isdir('whatever'), True)

    def test_listdir(self):
        overrides = [ DummyOverride(
            ('repoze.bfg.tests', 'fixtures'))]
        package = DummyPackage('package')
        po = self._makeOne(package)
        po.overrides= overrides
        self.failUnless(po.listdir('whatever'))

class TestDirectoryOverride(unittest.TestCase):
    def _getTargetClass(self):
        from repoze.bfg.resource import DirectoryOverride
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

class Test_resolve_resource_spec(unittest.TestCase):
    def _callFUT(self, spec, package_name='__main__'):
        from repoze.bfg.resource import resolve_resource_spec
        return resolve_resource_spec(spec, package_name)

    def test_abspath(self):
        import os
        here = os.path.dirname(__file__)
        path = os.path.abspath(here)
        package_name, filename = self._callFUT(path, 'apackage')
        self.assertEqual(filename, path)
        self.assertEqual(package_name, None)

    def test_rel_spec(self):
        pkg = 'repoze.bfg.tests'
        path = 'test_resource.py'
        package_name, filename = self._callFUT(path, pkg)
        self.assertEqual(package_name, 'repoze.bfg.tests')
        self.assertEqual(filename, 'test_resource.py')
        
    def test_abs_spec(self):
        pkg = 'repoze.bfg.tests'
        path = 'repoze.bfg.nottests:test_resource.py'
        package_name, filename = self._callFUT(path, pkg)
        self.assertEqual(package_name, 'repoze.bfg.nottests')
        self.assertEqual(filename, 'test_resource.py')

    def test_package_name_is_None(self):
        pkg = None
        path = 'test_resource.py'
        package_name, filename = self._callFUT(path, pkg)
        self.assertEqual(package_name, None)
        self.assertEqual(filename, 'test_resource.py')
        

class TestFileOverride(unittest.TestCase):
    def _getTargetClass(self):
        from repoze.bfg.resource import FileOverride
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
    
