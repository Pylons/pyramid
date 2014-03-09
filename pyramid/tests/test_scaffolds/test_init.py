import unittest

class TestPyramidTemplate(unittest.TestCase):
    def _makeOne(self):
        from pyramid.scaffolds import PyramidTemplate
        return PyramidTemplate('name')

    def test_pre(self):
        inst = self._makeOne()
        vars = {'package':'one', 'package_full_name': 'b.one'}
        inst.pre('command', 'output dir', vars)
        self.assertTrue(vars['random_string'])
        self.assertEqual(vars['package_logger'], 'one')
        self.assertEqual(vars['package_full_path'], 'b/one')
        self.assertEqual(vars['package_parent_path'], 'b')
        self.assertEqual(vars['package_root_name'], 'b')

    def test_pre_site(self):
        inst = self._makeOne()
        vars = {'package':'site', 'package_full_name': 'c.site'}
        self.assertRaises(ValueError, inst.pre, 'command', 'output dir', vars)
        
    def test_pre_root(self):
        inst = self._makeOne()
        vars = {'package':'root', 'package_full_name': 'root'}
        inst.pre('command', 'output dir', vars)
        self.assertTrue(vars['random_string'])
        self.assertEqual(vars['package_logger'], 'app')
        self.assertEqual(vars['package_full_path'], 'root')
        self.assertEqual(vars['package_parent_path'], '')
        self.assertEqual(vars['package_root_name'], 'root')
