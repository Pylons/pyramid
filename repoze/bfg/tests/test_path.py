import unittest

class TestCallerPath(unittest.TestCase):
    def tearDown(self):
        from repoze.bfg.tests import test_path
        if hasattr(test_path, '__bfg_abspath__'):
            del test_path.__bfg_abspath__

    def _callFUT(self, path, level=2):
        from repoze.bfg.path import caller_path
        return caller_path(path, level)

    def test_isabs(self):
        result = self._callFUT('/a/b/c')
        self.assertEqual(result, '/a/b/c')

    def test_pkgrelative(self):
        import os
        here = os.path.abspath(os.path.dirname(__file__))
        result = self._callFUT('a/b/c')
        self.assertEqual(result, os.path.join(here, 'a/b/c'))

    def test_memoization_has_bfg_abspath(self):
        import os
        from repoze.bfg.tests import test_path
        test_path.__bfg_abspath__ = '/foo/bar'
        result = self._callFUT('a/b/c')
        self.assertEqual(result, os.path.join('/foo/bar', 'a/b/c'))

    def test_memoization_success(self):
        import os
        here = os.path.abspath(os.path.dirname(__file__))
        from repoze.bfg.tests import test_path
        result = self._callFUT('a/b/c')
        self.assertEqual(result, os.path.join(here, 'a/b/c'))
        self.assertEqual(test_path.__bfg_abspath__, here)

class TestCallerModule(unittest.TestCase):
    def _callFUT(self, level=2):
        from repoze.bfg.path import caller_module
        return caller_module(level)

    def test_it_level_1(self):
        from repoze.bfg.tests import test_path
        result = self._callFUT(1)
        self.assertEqual(result, test_path)

    def test_it_level_2(self):
        from repoze.bfg.tests import test_path
        result = self._callFUT(2)
        self.assertEqual(result, test_path)

    def test_it_level_3(self):
        from repoze.bfg.tests import test_path
        result = self._callFUT(3)
        self.failIfEqual(result, test_path)

class TestCallerPackage(unittest.TestCase):
    def _callFUT(self, *arg, **kw):
        from repoze.bfg.path import caller_package
        return caller_package(*arg, **kw)

    def test_it_level_1(self):
        from repoze.bfg import tests
        result = self._callFUT(1)
        self.assertEqual(result, tests)

    def test_it_level_2(self):
        from repoze.bfg import tests
        result = self._callFUT(2)
        self.assertEqual(result, tests)

    def test_it_level_3(self):
        import unittest
        result = self._callFUT(3)
        self.assertEqual(result, unittest)

    def test_it_package(self):
        import repoze.bfg.tests
        def dummy_caller_module(*arg):
            return repoze.bfg.tests
        result = self._callFUT(1, caller_module=dummy_caller_module)
        self.assertEqual(result, repoze.bfg.tests)
        
class TestPackagePath(unittest.TestCase):
    def _callFUT(self, package):
        from repoze.bfg.path import package_path
        return package_path(package)

    def test_it_package(self):
        from repoze.bfg import tests
        package = DummyPackageOrModule(tests)
        result = self._callFUT(package)
        self.assertEqual(result, package.package_path)
        
    def test_it_module(self):
        from repoze.bfg.tests import test_path
        module = DummyPackageOrModule(test_path)
        result = self._callFUT(module)
        self.assertEqual(result, module.package_path)

    def test_memoization_success(self):
        from repoze.bfg.tests import test_path
        module = DummyPackageOrModule(test_path)
        self._callFUT(module)
        self.assertEqual(module.__bfg_abspath__, module.package_path)
        
    def test_memoization_fail(self):
        from repoze.bfg.tests import test_path
        module = DummyPackageOrModule(test_path, raise_exc=TypeError)
        result = self._callFUT(module)
        self.failIf(hasattr(module, '__bfg_abspath__'))
        self.assertEqual(result, module.package_path)

class TestPackageName(unittest.TestCase):
    def _callFUT(self, package):
        from repoze.bfg.path import package_name
        return package_name(package)

    def test_it_package(self):
        from repoze.bfg import tests
        package = DummyPackageOrModule(tests)
        result = self._callFUT(package)
        self.assertEqual(result, 'repoze.bfg.tests')
        
    def test_it_module(self):
        from repoze.bfg.tests import test_path
        module = DummyPackageOrModule(test_path)
        result = self._callFUT(module)
        self.assertEqual(result, 'repoze.bfg.tests')

    def test_it_None(self):
        result = self._callFUT(None)
        self.assertEqual(result, '__main__')
    
class DummyPackageOrModule:
    def __init__(self, real_package_or_module, raise_exc=None):
        self.__dict__['raise_exc'] = raise_exc
        self.__dict__['__name__'] = real_package_or_module.__name__
        import os
        self.__dict__['package_path'] = os.path.dirname(
            os.path.abspath(real_package_or_module.__file__))
        self.__dict__['__file__'] = real_package_or_module.__file__

    def __setattr__(self, key, val):
        if self.raise_exc is not None:
            raise self.raise_exc
        self.__dict__[key] = val
        
        
    
        

    
