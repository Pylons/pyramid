from plaster.exceptions import PlasterError
import pytest
import unittest

import pyramid.scripts.common


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
    with pytest.raises(PlasterError):
        pyramid.scripts.common.get_config_loader('invalidscheme:/foo')


def test_get_config_loader_calls():
    def reporter(text):
        nonlocal reporter_called
        reporter_called = True

    reporter_called = False
    with pytest.raises(SystemExit):
        pyramid.scripts.common.get_config_loader(
            'invalidscheme:/foo', reporter
        )

    assert reporter_called is True
