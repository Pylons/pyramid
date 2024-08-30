from plaster.exceptions import PlasterError
import pytest
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


def test_get_config_loader_raises():
    from pyramid.scripts.common import get_config_loader

    with pytest.raises(PlasterError):
        get_config_loader('invalidscheme:/foo')


def test_get_config_loader_calls():
    from pyramid.scripts.common import get_config_loader

    def reporter(text):
        nonlocal reporter_called
        reporter_called = True

    reporter_called = False
    with pytest.raises(SystemExit) as execinfo:
        get_config_loader('invalidscheme:/foo', reporter)

        assert execinfo.code == 1

    assert reporter_called is True
