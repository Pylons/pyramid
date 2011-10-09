import unittest
import os
import pkg_resources

class Test_copy_dir(unittest.TestCase):
    def setUp(self):
        import tempfile
        from pyramid.compat import NativeIO
        self.dirname = tempfile.mkdtemp()
        self.out = NativeIO()
        self.fixturetuple = ('pyramid.tests.test_scaffolds',
                             'fixture_scaffold')

    def tearDown(self):
        import shutil
        shutil.rmtree(self.dirname, ignore_errors=True)
        self.out.close()

    def _callFUT(self, *arg, **kw):
        kw['out_'] = self.out
        from pyramid.scaffolds.copydir import copy_dir
        return copy_dir(*arg, **kw)

    def test_copy_source_as_pkg_resource(self):
        vars = {'package':'mypackage'}
        self._callFUT(self.fixturetuple,
                      self.dirname,
                      vars,
                      1, False,
                      template_renderer=dummy_template_renderer)
        result = self.out.getvalue()
        self.assertTrue('Creating %s/mypackage/' % self.dirname in result)
        self.assertTrue(
            'Copying fixture_scaffold/+package+/__init__.py_tmpl to' in result)
        source = pkg_resources.resource_filename(
            'pyramid.tests.test_scaffolds',
            'fixture_scaffold/+package+/__init__.py_tmpl')
        target = os.path.join(self.dirname, 'mypackage', '__init__.py')
        with open(target, 'r') as f:
            tcontent = f.read()
        with open(source, 'r') as f:
            scontent = f.read()
        self.assertEqual(scontent, tcontent)

    def test_copy_source_as_dirname(self):
        vars = {'package':'mypackage'}
        source = pkg_resources.resource_filename(*self.fixturetuple)
        self._callFUT(source,
                      self.dirname,
                      vars,
                      1, False,
                      template_renderer=dummy_template_renderer)
        result = self.out.getvalue()
        self.assertTrue('Creating %s/mypackage/' % self.dirname in result)
        self.assertTrue('Copying __init__.py_tmpl to' in result)
        source = pkg_resources.resource_filename(
            'pyramid.tests.test_scaffolds',
            'fixture_scaffold/+package+/__init__.py_tmpl')
        target = os.path.join(self.dirname, 'mypackage', '__init__.py')
        with open(target, 'r') as f:
            tcontent = f.read()
        with open(source, 'r') as f:
            scontent = f.read()
        self.assertEqual(scontent, tcontent)

def dummy_template_renderer(content, v, filename=None):
    return content
    
        
