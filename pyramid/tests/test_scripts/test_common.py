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
