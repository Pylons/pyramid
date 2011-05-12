import unittest

class TestPyramidTemplate(unittest.TestCase):
    def _getTargetClass(self):
        from pyramid.scaffolds import PyramidTemplate
        return PyramidTemplate

    def _makeOne(self, name):
        cls = self._getTargetClass()
        return cls(name)

    def test_pre_logger_eq_root(self):
        tmpl = self._makeOne('name')
        vars = {'package':'root'}
        result = tmpl.pre(None, None, vars)
        self.assertEqual(result, None)
        self.assertEqual(vars['package_logger'], 'app')
        self.assertTrue(len(vars['random_string']) == 40)

    def test_pre_logger_noteq_root(self):
        tmpl = self._makeOne('name')
        vars = {'package':'notroot'}
        result = tmpl.pre(None, None, vars)
        self.assertEqual(result, None)
        self.assertEqual(vars['package_logger'], 'notroot')
        self.assertTrue(len(vars['random_string']) == 40)

    def test_post(self):
        tmpl = self._makeOne('name')
        vars = {'package':'root'}
        L = []
        tmpl.out = lambda msg: L.append(msg)
        result = tmpl.post(None, None, vars)
        self.assertEqual(result, None)
        self.assertEqual(L, ['Welcome to Pyramid.  Sorry for the convenience.'])

