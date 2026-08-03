import os
import unittest

here = os.path.abspath(os.path.dirname(__file__))


class TestRefFilename(unittest.TestCase):
    def _callFUT(self, ref):
        from pyramid.path import ref_filename

        return ref_filename(ref)

    def test_returns_path(self):
        import importlib.resources

        ref = importlib.resources.files('tests.pkgs.assets') / 'foo.txt'
        path = self._callFUT(ref)
        expected = os.path.join(here, 'pkgs/assets/foo.txt')
        self.assertEqual(path, expected)


class TestResourceFilename(unittest.TestCase):
    def _callFUT(self, package, name):
        from pyramid.path import resource_filename

        return resource_filename(package, name)

    def test_returns_path(self):
        path = self._callFUT('tests.pkgs.assets', 'foo.txt')
        expected = os.path.join(here, 'pkgs/assets/foo.txt')
        self.assertEqual(path, expected)


class TestCallerPath(unittest.TestCase):
    def tearDown(self):
        from . import test_path

        if hasattr(test_path, '__abspath__'):
            del test_path.__abspath__

    def _callFUT(self, path, level=2):
        from pyramid.path import caller_path

        return caller_path(path, level)

    def test_isabs(self):
        path = os.path.abspath('/a/b/c')
        result = self._callFUT(path)
        self.assertEqual(result, path)

    def test_pkgrelative(self):
        import os

        result = self._callFUT('a/b/c')
        self.assertEqual(result, os.path.join(here, 'a/b/c'))

    def test_memoization_has_abspath(self):
        import os

        from . import test_path

        test_path.__abspath__ = '/foo/bar'
        result = self._callFUT('a/b/c')
        self.assertEqual(result, os.path.join('/foo/bar', 'a/b/c'))

    def test_memoization_success(self):
        import os

        from . import test_path

        result = self._callFUT('a/b/c')
        self.assertEqual(result, os.path.join(here, 'a/b/c'))
        self.assertEqual(test_path.__abspath__, here)


class TestCallerModule(unittest.TestCase):
    def _callFUT(self, *arg, **kw):
        from pyramid.path import caller_module

        return caller_module(*arg, **kw)

    def test_it_level_1(self):
        from . import test_path

        result = self._callFUT(1)
        self.assertEqual(result, test_path)

    def test_it_level_2(self):
        from . import test_path

        result = self._callFUT(2)
        self.assertEqual(result, test_path)

    def test_it_level_3(self):
        from . import test_path

        result = self._callFUT(3)
        self.assertNotEqual(result, test_path)

    def test_it_no___name__(self):
        class DummyFrame:
            f_globals = {}

        class DummySys:
            def _getframe(self, level):
                return DummyFrame()

            modules = {'__main__': 'main'}

        dummy_sys = DummySys()
        result = self._callFUT(3, sys=dummy_sys)
        self.assertEqual(result, 'main')


class TestCallerPackage(unittest.TestCase):
    def _callFUT(self, *arg, **kw):
        from pyramid.path import caller_package

        return caller_package(*arg, **kw)

    def test_it_level_1(self):
        import tests

        result = self._callFUT(1)
        self.assertEqual(result, tests)

    def test_it_level_2(self):
        import tests

        result = self._callFUT(2)
        self.assertEqual(result, tests)

    def test_it_level_3(self):
        import unittest

        result = self._callFUT(3)
        self.assertEqual(result, unittest)

    def test_it_package(self):
        import tests

        def dummy_caller_module(*arg):
            return tests

        result = self._callFUT(1, caller_module=dummy_caller_module)
        self.assertEqual(result, tests)


class TestPackagePath(unittest.TestCase):
    def _callFUT(self, package):
        from pyramid.path import package_path

        return package_path(package)

    def test_it_package(self):
        import tests

        package = DummyPackageOrModule(tests)
        result = self._callFUT(package)
        self.assertEqual(result, package.package_path)

    def test_it_module(self):
        from . import test_path

        module = DummyPackageOrModule(test_path)
        result = self._callFUT(module)
        self.assertEqual(result, module.package_path)

    def test_memoization_success(self):
        from . import test_path

        module = DummyPackageOrModule(test_path)
        self._callFUT(module)
        self.assertEqual(module.__abspath__, module.package_path)

    def test_memoization_fail(self):
        from . import test_path

        module = DummyPackageOrModule(test_path, raise_exc=TypeError)
        result = self._callFUT(module)
        self.assertFalse(hasattr(module, '__abspath__'))
        self.assertEqual(result, module.package_path)


class TestPackageOf(unittest.TestCase):
    def _callFUT(self, package):
        from pyramid.path import package_of

        return package_of(package)

    def test_it_package(self):
        import tests

        package = DummyPackageOrModule(tests)
        result = self._callFUT(package)
        self.assertEqual(result, tests)

    def test_it_module(self):
        import tests
        import tests.test_path

        package = DummyPackageOrModule(tests.test_path)
        result = self._callFUT(package)
        self.assertEqual(result, tests)


class TestPackageName(unittest.TestCase):
    def _callFUT(self, package):
        from pyramid.path import package_name

        return package_name(package)

    def test_it_package(self):
        import tests

        package = DummyPackageOrModule(tests)
        result = self._callFUT(package)
        self.assertEqual(result, 'tests')

    def test_it_namespace_package(self):
        import tests

        package = DummyNamespacePackage(tests)
        result = self._callFUT(package)
        self.assertEqual(result, 'tests')

    def test_it_module(self):
        from . import test_path

        module = DummyPackageOrModule(test_path)
        result = self._callFUT(module)
        self.assertEqual(result, 'tests')

    def test_it_None(self):
        result = self._callFUT(None)
        self.assertEqual(result, '__main__')

    def test_it_main(self):
        import __main__

        result = self._callFUT(__main__)
        self.assertEqual(result, '__main__')


class TestPkgResourcesAssetDescriptor(unittest.TestCase):
    def _getTargetClass(self):
        from pyramid.path import PkgResourcesAssetDescriptor

        return PkgResourcesAssetDescriptor

    def _makeOne(self, pkg='tests', path='test_asset.py'):
        return self._getTargetClass()(pkg, path)

    def test_class_conforms_to_IAssetDescriptor(self):
        from zope.interface.verify import verifyClass

        from pyramid.interfaces import IAssetDescriptor

        verifyClass(IAssetDescriptor, self._getTargetClass())

    def test_instance_conforms_to_IAssetDescriptor(self):
        from zope.interface.verify import verifyObject

        from pyramid.interfaces import IAssetDescriptor

        verifyObject(IAssetDescriptor, self._makeOne())

    def test_absspec(self):
        inst = self._makeOne()
        self.assertEqual(inst.absspec(), 'tests:test_asset.py')

    def test_abspath(self):
        inst = self._makeOne()
        self.assertEqual(inst.abspath(), os.path.join(here, 'test_asset.py'))

    def test_stream(self):
        inst = self._makeOne()
        inst.pkg_resources = DummyPkgResource()
        inst.pkg_resources.resource_stream = lambda x, y: f'{x}:{y}'
        s = inst.stream()
        self.assertEqual(s, '{}:{}'.format('tests', 'test_asset.py'))

    def test_isdir(self):
        inst = self._makeOne()
        inst.pkg_resources = DummyPkgResource()
        inst.pkg_resources.resource_isdir = lambda x, y: f'{x}:{y}'
        self.assertEqual(
            inst.isdir(), '{}:{}'.format('tests', 'test_asset.py')
        )

    def test_listdir(self):
        inst = self._makeOne()
        inst.pkg_resources = DummyPkgResource()
        inst.pkg_resources.resource_listdir = lambda x, y: f'{x}:{y}'
        self.assertEqual(
            inst.listdir(), '{}:{}'.format('tests', 'test_asset.py')
        )

    def test_exists(self):
        inst = self._makeOne()
        inst.pkg_resources = DummyPkgResource()
        inst.pkg_resources.resource_exists = lambda x, y: f'{x}:{y}'
        self.assertEqual(
            inst.exists(), '{}:{}'.format('tests', 'test_asset.py')
        )


class TestFSAssetDescriptor(unittest.TestCase):
    def _getTargetClass(self):
        from pyramid.path import FSAssetDescriptor

        return FSAssetDescriptor

    def _makeOne(self, path=os.path.join(here, 'test_asset.py')):
        return self._getTargetClass()(path)

    def test_class_conforms_to_IAssetDescriptor(self):
        from zope.interface.verify import verifyClass

        from pyramid.interfaces import IAssetDescriptor

        verifyClass(IAssetDescriptor, self._getTargetClass())

    def test_instance_conforms_to_IAssetDescriptor(self):
        from zope.interface.verify import verifyObject

        from pyramid.interfaces import IAssetDescriptor

        verifyObject(IAssetDescriptor, self._makeOne())

    def test_absspec(self):
        inst = self._makeOne()
        self.assertRaises(NotImplementedError, inst.absspec)

    def test_abspath(self):
        inst = self._makeOne()
        self.assertEqual(inst.abspath(), os.path.join(here, 'test_asset.py'))

    def test_stream(self):
        inst = self._makeOne()
        s = inst.stream()
        val = s.read()
        s.close()
        self.assertTrue(b'asset' in val)

    def test_isdir_False(self):
        inst = self._makeOne()
        self.assertFalse(inst.isdir())

    def test_isdir_True(self):
        inst = self._makeOne(here)
        self.assertTrue(inst.isdir())

    def test_listdir(self):
        inst = self._makeOne(here)
        self.assertTrue(inst.listdir())

    def test_exists(self):
        inst = self._makeOne()
        self.assertTrue(inst.exists())


class DummyPkgResource:
    pass


class DummyPackageOrModule:
    def __init__(self, real_package_or_module, raise_exc=None):
        self.__dict__['raise_exc'] = raise_exc
        self.__dict__['__name__'] = real_package_or_module.__name__
        import os

        self.__dict__['package_path'] = os.path.dirname(
            os.path.abspath(real_package_or_module.__file__)
        )
        self.__dict__['__file__'] = real_package_or_module.__file__

    def __setattr__(self, key, val):
        if self.raise_exc is not None:
            raise self.raise_exc
        self.__dict__[key] = val


class DummyNamespacePackage:
    """Has no __file__ attribute."""

    def __init__(self, real_package_or_module):
        self.__name__ = real_package_or_module.__name__
        import os

        self.package_path = os.path.dirname(
            os.path.abspath(real_package_or_module.__file__)
        )
