import unittest

class TestPyramidTemplate(unittest.TestCase):
    def _makeOne(self):
        from pyramid.scaffolds import PyramidTemplate
        return PyramidTemplate('name')

    def test_pre(self):
        inst = self._makeOne()
        vars = {'package':'one'}
        inst.pre('command', 'output dir', vars)
        self.assertTrue(vars['random_string'])
        self.assertEqual(vars['package_logger'], 'one')

    def test_pre_site(self):
        inst = self._makeOne()
        vars = {'package':'site'}
        self.assertRaises(ValueError, inst.pre, 'command', 'output dir', vars)
        
    def test_pre_root(self):
        inst = self._makeOne()
        vars = {'package':'root'}
        inst.pre('command', 'output dir', vars)
        self.assertTrue(vars['random_string'])
        self.assertEqual(vars['package_logger'], 'app')

class TestINIURLs(unittest.TestCase):

    def test_it(self):
        from pyramid.scaffolds import _add_ini_urls
        vars = {}
        pkg_resources = DummyPkgResources({'pyramid': DummyDistribution()})
        _add_ini_urls(vars, pkg_resources=pkg_resources)
        self.assertEqual(
            vars['settings_url'],
            ('http://docs.pylonsproject.org/projects/'
             'pyramid/en/1.3-branch/narr/environment.html'))
        self.assertEqual(
            vars['logging_url'],
            ('http://docs.pylonsproject.org/projects/'
             'pyramid/en/1.3-branch/narr/logging.html'))
        self.assertEqual(
            vars['debugtoolbar_url'],
            ('http://docs.pylonsproject.org/projects/'
             'pyramid_debugtoolbar/en/latest/#settings'))

    def test_it_failover(self):
        from pyramid.scaffolds import _add_ini_urls
        vars = {}
        class _dist(object):
            @property
            def parsed_version(self):
                raise ValueError
        pkg_resources = DummyPkgResources({'pyramid': _dist})
        _add_ini_urls(vars, pkg_resources=pkg_resources)
        self.assertEqual(
            vars['settings_url'],
            ('http://docs.pylonsproject.org/projects/'
             'pyramid/en/latest/narr/environment.html'))
        self.assertEqual(
            vars['logging_url'],
            ('http://docs.pylonsproject.org/projects/'
             'pyramid/en/latest/narr/logging.html'))
        self.assertEqual(
            vars['debugtoolbar_url'],
            ('http://docs.pylonsproject.org/projects/'
             'pyramid_debugtoolbar/en/latest/#settings'))

class DummyDistribution(object):
    parsed_version = ('00000001', '00000003', '*b', '00000002', '*final')

class DummyPkgResources(object):
    def __init__(self, dists):
        self.dists = dists

    def get_distribution(self, name):
        return self.dists[name]
