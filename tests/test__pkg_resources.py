import importlib
import os
import types
import unittest


class TestRegisterLoaderType(unittest.TestCase):
    def _callFUT(self, loader_type, provider_factory):
        from pyramid._pkg_resources import register_loader_type

        return register_loader_type(loader_type, provider_factory)

    def test_it(self):
        from pyramid._pkg_resources import _provider_factories

        class DummyLoader:
            pass

        class DummyProvider:
            pass

        self._callFUT(DummyLoader, DummyProvider)
        self.assertIs(_provider_factories[DummyLoader], DummyProvider)
        # cleanup
        del _provider_factories[DummyLoader]

    def test_overwrite(self):
        from pyramid._pkg_resources import _provider_factories

        class DummyLoader:
            pass

        class Provider1:
            pass

        class Provider2:
            pass

        self._callFUT(DummyLoader, Provider1)
        self._callFUT(DummyLoader, Provider2)
        self.assertIs(_provider_factories[DummyLoader], Provider2)
        del _provider_factories[DummyLoader]


class TestAlwaysObject(unittest.TestCase):
    def _callFUT(self, classes):
        from pyramid._pkg_resources import _always_object

        return _always_object(classes)

    def test_object_not_present(self):
        result = self._callFUT((int, str))
        self.assertIn(object, result)
        self.assertEqual(result, (int, str, object))

    def test_object_already_present(self):
        classes = (int, object, str)
        result = self._callFUT(classes)
        self.assertIs(result, classes)


class TestFindAdapter(unittest.TestCase):
    def _callFUT(self, registry, ob):
        from pyramid._pkg_resources import _find_adapter

        return _find_adapter(registry, ob)

    def test_direct_match(self):
        class MyLoader:
            pass

        registry = {MyLoader: 'found'}
        result = self._callFUT(registry, MyLoader())
        self.assertEqual(result, 'found')

    def test_mro_traversal(self):
        class Base:
            pass

        class Child(Base):
            pass

        registry = {Base: 'found_base'}
        result = self._callFUT(registry, Child())
        self.assertEqual(result, 'found_base')

    def test_object_fallback(self):
        class Unknown:
            pass

        registry = {object: 'fallback'}
        result = self._callFUT(registry, Unknown())
        self.assertEqual(result, 'fallback')

    def test_no_match_returns_none(self):
        class Unknown:
            pass

        registry = {}
        result = self._callFUT(registry, Unknown())
        self.assertIsNone(result)


class TestGetProvider(unittest.TestCase):
    def _callFUT(self, moduleOrReq):
        from pyramid._pkg_resources import get_provider

        return get_provider(moduleOrReq)

    def test_returns_provider_for_imported_module(self):
        from pyramid._pkg_resources import DefaultProvider

        provider = self._callFUT('pyramid')
        self.assertIsInstance(provider, DefaultProvider)

    def test_auto_imports_missing_module(self):
        import sys

        # Use a module we know exists but may not be imported yet
        name = 'pyramid._pkg_resources'
        if name in sys.modules:
            provider = self._callFUT(name)
            self.assertIsNotNone(provider)
        else:
            provider = self._callFUT(name)
            self.assertIn(name, sys.modules)
            self.assertIsNotNone(provider)

    def test_raises_for_nonexistent_module(self):
        self.assertRaises(ImportError, self._callFUT, 'nonexistent_xyz_pkg')


class TestResourceManager(unittest.TestCase):
    def _makeOne(self):
        from pyramid._pkg_resources import ResourceManager

        return ResourceManager()

    def test_resource_exists(self):
        mgr = self._makeOne()
        self.assertTrue(mgr.resource_exists('pyramid', 'path.py'))
        self.assertFalse(mgr.resource_exists('pyramid', 'nonexistent.xyz'))

    def test_resource_filename(self):
        mgr = self._makeOne()
        result = mgr.resource_filename('pyramid', 'path.py')
        self.assertTrue(result.endswith('path.py'))
        self.assertTrue(os.path.isfile(result))

    def test_resource_isdir(self):
        mgr = self._makeOne()
        self.assertTrue(mgr.resource_isdir('pyramid', ''))
        self.assertFalse(mgr.resource_isdir('pyramid', 'path.py'))

    def test_resource_stream(self):
        mgr = self._makeOne()
        stream = mgr.resource_stream('pyramid', 'path.py')
        try:
            data = stream.read()
            self.assertIn(b'def package_path', data)
        finally:
            stream.close()

    def test_resource_string(self):
        mgr = self._makeOne()
        data = mgr.resource_string('pyramid', 'path.py')
        self.assertIn(b'def package_path', data)

    def test_resource_listdir(self):
        mgr = self._makeOne()
        listing = mgr.resource_listdir('pyramid', '')
        self.assertIn('path.py', listing)
        self.assertIn('config', listing)


class TestNullProvider(unittest.TestCase):
    def _getTargetClass(self):
        from pyramid._pkg_resources import NullProvider

        return NullProvider

    def _makeOne(self, module=None):
        if module is None:
            module = types.ModuleType('dummy')
            module.__file__ = '/fake/path/dummy.py'
        return self._getTargetClass()(module)

    def test_init_sets_loader(self):
        module = types.ModuleType('dummy')
        module.__file__ = '/fake/path/dummy.py'
        module.__loader__ = 'a_loader'
        provider = self._makeOne(module)
        self.assertEqual(provider.loader, 'a_loader')

    def test_init_sets_module_path(self):
        module = types.ModuleType('dummy')
        module.__file__ = '/fake/path/dummy.py'
        provider = self._makeOne(module)
        self.assertEqual(provider.module_path, '/fake/path')

    def test_init_no_file(self):
        module = types.ModuleType('dummy')
        # no __file__ attribute
        provider = self._getTargetClass()(module)
        self.assertEqual(provider.module_path, '')

    def test_fn_joins_paths(self):
        provider = self._makeOne()
        result = provider._fn('/base/dir', 'sub/file.txt')
        self.assertEqual(result, os.path.join('/base/dir', 'sub', 'file.txt'))

    def test_fn_empty_resource(self):
        provider = self._makeOne()
        result = provider._fn('/base/dir', '')
        self.assertEqual(result, '/base/dir')

    def test_validate_resource_path_valid(self):
        # Should not raise
        self._getTargetClass()._validate_resource_path('foo/bar.txt')

    def test_validate_resource_path_dotdot_warns(self):
        import warnings

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter('always')
            self._getTargetClass()._validate_resource_path('../foo/bar.txt')
            self.assertEqual(len(w), 1)
            self.assertIn('absolute path', str(w[0].message))

    def test_validate_resource_path_windows_absolute_raises(self):
        self.assertRaises(
            ValueError,
            self._getTargetClass()._validate_resource_path,
            r'C:\foo\bar.txt',
        )

    def test_validate_resource_path_blank_ok(self):
        # Should not raise
        self._getTargetClass()._validate_resource_path('')

    def test_has_resource_raises(self):
        provider = self._makeOne()
        self.assertRaises(NotImplementedError, provider._has, '/some/path')

    def test_isdir_raises(self):
        provider = self._makeOne()
        self.assertRaises(NotImplementedError, provider._isdir, '/some/path')

    def test_listdir_raises(self):
        provider = self._makeOne()
        self.assertRaises(
            NotImplementedError, provider._listdir, '/some/path'
        )

    def test_get_resource_filename(self):
        module = types.ModuleType('dummy')
        module.__file__ = '/fake/path/dummy.py'
        provider = self._makeOne(module)
        result = provider.get_resource_filename(None, 'sub/file.txt')
        self.assertEqual(
            result, os.path.join('/fake/path', 'sub', 'file.txt')
        )

    def test_get_resource_string_with_loader(self):
        module = types.ModuleType('dummy')
        module.__file__ = '/fake/path/dummy.py'

        class DummyLoader:
            def get_data(self, path):
                return b'some data'

        module.__loader__ = DummyLoader()
        provider = self._makeOne(module)
        result = provider.get_resource_string(None, 'file.txt')
        self.assertEqual(result, b'some data')

    def test_get_resource_stream_wraps_string(self):
        module = types.ModuleType('dummy')
        module.__file__ = '/fake/path/dummy.py'

        class DummyLoader:
            def get_data(self, path):
                return b'stream data'

        module.__loader__ = DummyLoader()
        provider = self._makeOne(module)
        stream = provider.get_resource_stream(None, 'file.txt')
        self.assertEqual(stream.read(), b'stream data')

    def test_get_no_loader_get_data_raises(self):
        module = types.ModuleType('dummy')
        module.__file__ = '/fake/path/dummy.py'
        module.__loader__ = object()  # no get_data method
        provider = self._makeOne(module)
        self.assertRaises(
            NotImplementedError, provider._get, '/some/path'
        )


class TestDefaultProvider(unittest.TestCase):
    def _getTargetClass(self):
        from pyramid._pkg_resources import DefaultProvider

        return DefaultProvider

    def _makeOne(self, module=None):
        if module is None:
            import pyramid

            module = pyramid
        return self._getTargetClass()(module)

    def test_has_existing_path(self):
        provider = self._makeOne()
        import pyramid

        module_dir = os.path.dirname(pyramid.__file__)
        self.assertTrue(provider._has(os.path.join(module_dir, 'path.py')))

    def test_has_nonexistent_path(self):
        provider = self._makeOne()
        self.assertFalse(provider._has('/nonexistent/path/file.xyz'))

    def test_isdir(self):
        provider = self._makeOne()
        import pyramid

        module_dir = os.path.dirname(pyramid.__file__)
        self.assertTrue(provider._isdir(module_dir))
        self.assertFalse(
            provider._isdir(os.path.join(module_dir, 'path.py'))
        )

    def test_listdir(self):
        provider = self._makeOne()
        import pyramid

        module_dir = os.path.dirname(pyramid.__file__)
        listing = provider._listdir(module_dir)
        self.assertIn('path.py', listing)

    def test_get_resource_stream(self):
        provider = self._makeOne()
        stream = provider.get_resource_stream(None, 'path.py')
        try:
            data = stream.read()
            self.assertIn(b'def package_path', data)
        finally:
            stream.close()

    def test_get(self):
        provider = self._makeOne()
        import pyramid

        filepath = os.path.join(
            os.path.dirname(pyramid.__file__), 'path.py'
        )
        data = provider._get(filepath)
        self.assertIn(b'def package_path', data)

    def test_register(self):
        from pyramid._pkg_resources import _provider_factories

        import importlib.machinery

        cls = self._getTargetClass()
        # SourceFileLoader should already be registered
        self.assertIs(
            _provider_factories[importlib.machinery.SourceFileLoader], cls
        )


class TestDefaultProviderRegistration(unittest.TestCase):
    def test_object_registered_as_null_provider(self):
        from pyramid._pkg_resources import NullProvider, _provider_factories

        self.assertIs(_provider_factories[object], NullProvider)

    def test_source_file_loader_registered(self):
        import importlib.machinery

        from pyramid._pkg_resources import (
            DefaultProvider,
            _provider_factories,
        )

        self.assertIs(
            _provider_factories[importlib.machinery.SourceFileLoader],
            DefaultProvider,
        )

    def test_sourceless_file_loader_registered(self):
        import importlib.machinery

        from pyramid._pkg_resources import (
            DefaultProvider,
            _provider_factories,
        )

        self.assertIs(
            _provider_factories[importlib.machinery.SourcelessFileLoader],
            DefaultProvider,
        )


class TestModuleLevelFunctions(unittest.TestCase):
    def test_resource_exists(self):
        from pyramid._pkg_resources import resource_exists

        self.assertTrue(resource_exists('pyramid', 'path.py'))
        self.assertFalse(resource_exists('pyramid', 'nonexistent.xyz'))

    def test_resource_filename(self):
        from pyramid._pkg_resources import resource_filename

        result = resource_filename('pyramid', 'path.py')
        self.assertTrue(result.endswith('path.py'))
        self.assertTrue(os.path.isfile(result))

    def test_resource_isdir(self):
        from pyramid._pkg_resources import resource_isdir

        self.assertTrue(resource_isdir('pyramid', ''))
        self.assertFalse(resource_isdir('pyramid', 'path.py'))

    def test_resource_stream(self):
        from pyramid._pkg_resources import resource_stream

        stream = resource_stream('pyramid', 'path.py')
        try:
            data = stream.read()
            self.assertIn(b'def package_path', data)
        finally:
            stream.close()

    def test_resource_string(self):
        from pyramid._pkg_resources import resource_string

        data = resource_string('pyramid', 'path.py')
        self.assertIn(b'def package_path', data)

    def test_resource_listdir(self):
        from pyramid._pkg_resources import resource_listdir

        listing = resource_listdir('pyramid', '')
        self.assertIn('path.py', listing)
        self.assertIn('config', listing)


class TestResourceAccessOnRealPackage(unittest.TestCase):
    """Integration tests using the pyramid package itself."""

    def test_resource_exists_real_file(self):
        from pyramid._pkg_resources import resource_exists

        self.assertTrue(resource_exists('pyramid', 'path.py'))

    def test_resource_exists_nonexistent(self):
        from pyramid._pkg_resources import resource_exists

        self.assertFalse(resource_exists('pyramid', 'does_not_exist.xyz'))

    def test_resource_filename_returns_real_path(self):
        from pyramid._pkg_resources import resource_filename

        path = resource_filename('pyramid', 'path.py')
        self.assertTrue(os.path.isfile(path))

    def test_resource_isdir_on_package(self):
        from pyramid._pkg_resources import resource_isdir

        self.assertTrue(resource_isdir('pyramid', ''))

    def test_resource_isdir_on_file(self):
        from pyramid._pkg_resources import resource_isdir

        self.assertFalse(resource_isdir('pyramid', 'path.py'))

    def test_resource_isdir_on_subpackage(self):
        from pyramid._pkg_resources import resource_isdir

        self.assertTrue(resource_isdir('pyramid', 'config'))


class TestProviderOverrideChain(unittest.TestCase):
    """Test that registering a custom provider intercepts lookups."""

    def test_custom_provider_intercepts(self):
        from pyramid._pkg_resources import (
            NullProvider,
            _provider_factories,
            get_provider,
            register_loader_type,
        )

        class CustomLoader:
            pass

        class CustomProvider(NullProvider):
            custom_flag = True

            def _has(self, path):
                return True

        register_loader_type(CustomLoader, CustomProvider)

        # Create a module with this loader
        module = types.ModuleType('_test_custom_module')
        module.__file__ = '/fake/custom.py'
        module.__loader__ = CustomLoader()
        import sys

        sys.modules['_test_custom_module'] = module

        try:
            provider = get_provider('_test_custom_module')
            self.assertIsInstance(provider, CustomProvider)
            self.assertTrue(provider.custom_flag)
        finally:
            del sys.modules['_test_custom_module']
            del _provider_factories[CustomLoader]


class TestAssetOverrideWithVendoredPkgResources(unittest.TestCase):
    """Integration test: full config.override_asset() flow."""

    def setUp(self):
        from pyramid.testing import cleanUp

        cleanUp()

    def tearDown(self):
        from pyramid.testing import cleanUp

        cleanUp()

    def test_override_asset_flow(self):
        from pyramid.config import Configurator

        config = Configurator(autocommit=True)
        # Override one package's templates with another's
        config.override_asset(
            'tests.test_config.pkgs.asset:templates/foo.pt',
            'tests.test_config.pkgs.asset.subpackage:templates/bar.pt',
        )
        # If we get here without error, the vendored _pkg_resources is
        # working with the override system
        from pyramid.interfaces import IPackageOverrides

        overrides = config.registry.queryUtility(
            IPackageOverrides, name='tests.test_config.pkgs.asset'
        )
        self.assertIsNotNone(overrides)


class TestPkgResourcesAssetDescriptorWithVendoredModule(unittest.TestCase):
    """Test that PkgResourcesAssetDescriptor uses vendored module."""

    def test_abspath(self):
        from pyramid.path import PkgResourcesAssetDescriptor

        desc = PkgResourcesAssetDescriptor('pyramid', 'path.py')
        abspath = desc.abspath()
        self.assertTrue(os.path.isfile(abspath))
        self.assertTrue(abspath.endswith('path.py'))

    def test_exists(self):
        from pyramid.path import PkgResourcesAssetDescriptor

        desc = PkgResourcesAssetDescriptor('pyramid', 'path.py')
        self.assertTrue(desc.exists())

    def test_isdir(self):
        from pyramid.path import PkgResourcesAssetDescriptor

        desc = PkgResourcesAssetDescriptor('pyramid', '')
        self.assertTrue(desc.isdir())

    def test_stream(self):
        from pyramid.path import PkgResourcesAssetDescriptor

        desc = PkgResourcesAssetDescriptor('pyramid', 'path.py')
        stream = desc.stream()
        try:
            data = stream.read()
            self.assertIn(b'def package_path', data)
        finally:
            stream.close()


class TestNoSetuptoolsImport(unittest.TestCase):
    """Verify importing pyramid does not pull in setuptools pkg_resources."""

    def test_no_setuptools_pkg_resources_import(self):
        import subprocess
        import sys

        result = subprocess.run(
            [
                sys.executable,
                '-c',
                'import pyramid; import sys; '
                'assert "pkg_resources" not in sys.modules, '
                '"pkg_resources still imported!"; '
                'print("clean")',
            ],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('clean', result.stdout)


class TestBackwardCompatibility(unittest.TestCase):
    """Verify the vendored module provides the same API surface."""

    def test_has_register_loader_type(self):
        from pyramid._pkg_resources import register_loader_type

        self.assertTrue(callable(register_loader_type))

    def test_has_get_provider(self):
        from pyramid._pkg_resources import get_provider

        self.assertTrue(callable(get_provider))

    def test_has_resource_functions(self):
        from pyramid._pkg_resources import (
            resource_exists,
            resource_filename,
            resource_isdir,
            resource_listdir,
            resource_stream,
            resource_string,
        )

        for fn in [
            resource_exists,
            resource_filename,
            resource_isdir,
            resource_listdir,
            resource_stream,
            resource_string,
        ]:
            self.assertTrue(callable(fn))

    def test_has_provider_classes(self):
        from pyramid._pkg_resources import DefaultProvider, NullProvider

        self.assertTrue(issubclass(DefaultProvider, NullProvider))

    def test_has_resource_manager(self):
        from pyramid._pkg_resources import ResourceManager

        mgr = ResourceManager()
        self.assertTrue(hasattr(mgr, 'resource_exists'))
        self.assertTrue(hasattr(mgr, 'resource_filename'))
        self.assertTrue(hasattr(mgr, 'resource_isdir'))
        self.assertTrue(hasattr(mgr, 'resource_stream'))
        self.assertTrue(hasattr(mgr, 'resource_string'))
        self.assertTrue(hasattr(mgr, 'resource_listdir'))
