from contextlib import redirect_stderr
import io
import os
import tempfile
import unittest


class TestParseVars(unittest.TestCase):
    def test_parse_vars_good(self):
        from pyramid.scripts.common import parse_vars

        vars = ['a=1', 'b=2']
        result = parse_vars(vars)
        self.assertEqual(result, {'a': '1', 'b': '2'})

    def test_parse_vars_bad(self):
        from pyramid.scripts.common import parse_vars

        vars = ['a']
        self.assertRaises(ValueError, parse_vars, vars)


class TestGetConfigLoader(unittest.TestCase):
    def _callFUT(self, *args, **kw):
        from pyramid.scripts.common import get_config_loader

        return get_config_loader(*args, **kw)

    def test_bad_scheme_raises(self):
        from plaster import PlasterError

        self.assertRaises(PlasterError, self._callFUT, 'invalidscheme:/foo')

    def test_bad_scheme_exit_on_error(self):
        with redirect_stderr(io.StringIO()) as err:
            with self.assertRaises(SystemExit) as cm:
                self._callFUT('invalidscheme:/foo', exit_on_error=True)
        self.assertEqual(cm.exception.code, 1)
        self.assertIn(
            'Unable to load config "invalidscheme:/foo"', err.getvalue()
        )

    def test_missing_file_without_exit_on_error(self):
        loader = self._callFUT('/nonexistent/myapp.ini#main')
        self.assertEqual(loader.uri.path, '/nonexistent/myapp.ini')

    def test_missing_file_exit_on_error(self):
        with redirect_stderr(io.StringIO()) as err:
            with self.assertRaises(SystemExit) as cm:
                self._callFUT(
                    '/nonexistent/myapp.ini#main', exit_on_error=True
                )
        self.assertEqual(cm.exception.code, 1)
        self.assertIn(
            'Config file "/nonexistent/myapp.ini" does not exist',
            err.getvalue(),
        )

    def test_existing_file_exit_on_error(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, 'myapp.ini')
            with open(path, 'w') as f:
                f.write('[app:main]\nuse = egg:pyramid\n')
            loader = self._callFUT(path + '#main', exit_on_error=True)
        self.assertEqual(loader.uri.path, path)
