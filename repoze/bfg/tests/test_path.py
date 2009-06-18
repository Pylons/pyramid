import unittest

class TestCallerPath(unittest.TestCase):
    def _callFUT(self, path, level=2, package_globals=None):
        from repoze.bfg.path import caller_path
        return caller_path(path, level, package_globals)

    def test_isabs(self):
        self.assertEqual(self._callFUT('/a/b/c'), '/a/b/c')

    def test_pkgrelative(self):
        import os
        here = os.path.abspath(os.path.dirname(__file__))
        self.assertEqual(self._callFUT('a/b/c'), os.path.join(here, 'a/b/c'))

    def test_memoization_has_bfg_abspath(self):
        import os
        here = os.path.abspath(os.path.dirname(__file__))
        package_globals =  {'__bfg_abspath__':'/foo/bar'}
        self.assertEqual(
            self._callFUT('a/b/c',
                          package_globals=package_globals),
            os.path.join('/foo/bar', 'a/b/c'))

    def test_memoization_success(self):
        import os
        here = os.path.abspath(os.path.dirname(__file__))
        package_globals = {'__name__':'repoze.bfg.tests.test_path'}
        self.assertEqual(
            self._callFUT('a/b/c',
                          package_globals=package_globals),
            os.path.join(here, 'a/b/c'))
        self.assertEqual(package_globals['__bfg_abspath__'], here)
        
    def test_memoization_fail(self):
        import os
        here = os.path.abspath(os.path.dirname(__file__))
        class faildict(dict):
            def __setitem__(self, *arg):
                raise KeyError('name')
        package_globals = faildict({'__name__':'repoze.bfg.tests.test_path'})
        self.assertEqual(
            self._callFUT('a/b/c',
                          package_globals=package_globals),
            os.path.join(here, 'a/b/c'))
        self.failIf('__bfg_abspath__' in package_globals)
        
        
        

    
