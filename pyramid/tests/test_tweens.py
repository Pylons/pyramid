import unittest

class TestTweens(unittest.TestCase):
    def _makeOne(self):
        from pyramid.config import Tweens
        return Tweens()

    def test_add_explicit(self):
        tweens = self._makeOne()
        tweens.add_explicit('name', 'factory')
        self.assertEqual(tweens.explicit, [('name',  'factory')])
        tweens.add_explicit('name2', 'factory2')
        self.assertEqual(tweens.explicit, [('name',  'factory'),
                                           ('name2', 'factory2')])

    def test_add_implicit(self):
        from pyramid.tweens import INGRESS
        tweens = self._makeOne()
        tweens.add_implicit('name', 'factory')
        self.assertEqual(tweens.implicit_names, ['name'])
        self.assertEqual(tweens.implicit_factories,
                         {'name':'factory'})
        self.assertEqual(tweens.implicit_ingress_names, ['name'])
        self.assertEqual(tweens.implicit_order, [('name', INGRESS)])
        tweens.add_implicit('name2', 'factory2')
        self.assertEqual(tweens.implicit_names, ['name',  'name2'])
        self.assertEqual(tweens.implicit_factories,
                         {'name':'factory', 'name2':'factory2'})
        self.assertEqual(tweens.implicit_ingress_names, ['name', 'name2'])
        self.assertEqual(tweens.implicit_order,
                         [('name', INGRESS), ('name2', INGRESS)])
        tweens.add_implicit('name3', 'factory3', below='name2')
        self.assertEqual(tweens.implicit_names, ['name',  'name2', 'name3'])
        self.assertEqual(tweens.implicit_factories,
                         {'name':'factory', 'name2':'factory2',
                          'name3':'factory3'})
        self.assertEqual(tweens.implicit_ingress_names, ['name', 'name2'])
        self.assertEqual(tweens.implicit_order,
                         [('name', INGRESS), ('name2', INGRESS),
                          ('name2', 'name3')])

    def test___call___explicit(self):
        tweens = self._makeOne()
        def factory1(handler, registry):
            return handler
        def factory2(handler, registry):
            return '123'
        tweens.explicit = [('name', factory1), ('name', factory2)]
        self.assertEqual(tweens(None, None), '123')

    def test___call___implicit(self):
        tweens = self._makeOne()
        def factory1(handler, registry):
            return handler
        def factory2(handler, registry):
            return '123'
        tweens.implicit_names = ['name', 'name2']
        tweens.implicit_factories = {'name':factory1, 'name2':factory2}
        self.assertEqual(tweens(None, None), '123')

    def test_implicit_ordering_1(self):
        tweens = self._makeOne()
        tweens.add_implicit('name1', 'factory1')
        tweens.add_implicit('name2', 'factory2')
        self.assertEqual(tweens.implicit(), [('name1', 'factory1'),
                                             ('name2', 'factory2')])

    def test_implicit_ordering_2(self):
        from pyramid.tweens import MAIN
        tweens = self._makeOne()
        tweens.add_implicit('name1', 'factory1')
        tweens.add_implicit('name2', 'factory2', below=MAIN)
        self.assertEqual(tweens.implicit(),
                         [('name2', 'factory2'), ('name1', 'factory1')])

    def test_implicit_ordering_3(self):
        from pyramid.tweens import MAIN
        tweens = self._makeOne()
        add = tweens.add_implicit
        add('auth', 'auth_factory', atop='browserid')
        add('dbt', 'dbt_factory') 
        add('retry', 'retry_factory', below='txnmgr', atop='exceptionview')
        add('browserid', 'browserid_factory')
        add('txnmgr', 'txnmgr_factory', atop='exceptionview')
        add('exceptionview', 'excview_factory', below=MAIN)
        self.assertEqual(tweens.implicit(),
                         [('txnmgr', 'txnmgr_factory'),
                          ('retry', 'retry_factory'),
                          ('exceptionview', 'excview_factory'),
                          ('auth', 'auth_factory'),
                          ('browserid', 'browserid_factory'),
                          ('dbt', 'dbt_factory')])

    def test_implicit_ordering_4(self):
        from pyramid.tweens import MAIN
        tweens = self._makeOne()
        add = tweens.add_implicit
        add('exceptionview', 'excview_factory', below=MAIN)
        add('auth', 'auth_factory', atop='browserid')
        add('retry', 'retry_factory', below='txnmgr', atop='exceptionview')
        add('browserid', 'browserid_factory')
        add('txnmgr', 'txnmgr_factory', atop='exceptionview')
        add('dbt', 'dbt_factory') 
        self.assertEqual(tweens.implicit(),
                         [('txnmgr', 'txnmgr_factory'),
                          ('retry', 'retry_factory'),
                          ('exceptionview', 'excview_factory'),
                          ('auth', 'auth_factory'),
                          ('browserid', 'browserid_factory'),
                          ('dbt', 'dbt_factory')])

    def test_implicit_ordering_missing_partial(self):
        from pyramid.tweens import MAIN
        tweens = self._makeOne()
        add = tweens.add_implicit
        add('exceptionview', 'excview_factory', below=MAIN)
        add('auth', 'auth_factory', atop='browserid')
        add('retry', 'retry_factory', below='txnmgr', atop='exceptionview')
        add('browserid', 'browserid_factory')
        add('dbt', 'dbt_factory') 
        self.assertEqual(tweens.implicit(),
                         [('retry', 'retry_factory'),
                          ('exceptionview', 'excview_factory'),
                          ('auth', 'auth_factory'),
                          ('browserid', 'browserid_factory'),
                          ('dbt', 'dbt_factory')])

    def test_implicit_ordering_missing_partial2(self):
        tweens = self._makeOne()
        add = tweens.add_implicit
        add('dbt', 'dbt_factory')
        add('auth', 'auth_factory', atop='browserid')
        add('retry', 'retry_factory', below='txnmgr', atop='exceptionview')
        add('browserid', 'browserid_factory')
        self.assertEqual(tweens.implicit(),
                         [('dbt', 'dbt_factory'),
                          ('auth', 'auth_factory'),
                          ('browserid', 'browserid_factory'),
                          ('retry', 'retry_factory')])

    def test_implicit_ordering_missing_partial3(self):
        from pyramid.tweens import MAIN
        tweens = self._makeOne()
        add = tweens.add_implicit
        add('exceptionview', 'excview_factory', below=MAIN)
        add('retry', 'retry_factory', below='txnmgr', atop='exceptionview')
        add('browserid', 'browserid_factory')
        self.assertEqual(tweens.implicit(),
                         [('retry', 'retry_factory'),
                          ('exceptionview', 'excview_factory'),
                          ('browserid', 'browserid_factory')])

    def test_implicit_ordering_conflict_direct(self):
        from pyramid.tweens import CyclicDependencyError
        tweens = self._makeOne()
        add = tweens.add_implicit
        add('browserid', 'browserid_factory')
        add('auth', 'auth_factory', atop='browserid', below='browserid')
        self.assertRaises(CyclicDependencyError, tweens.implicit)

    def test_implicit_ordering_conflict_indirect(self):
        from pyramid.tweens import CyclicDependencyError
        tweens = self._makeOne()
        add = tweens.add_implicit
        add('browserid', 'browserid_factory')
        add('auth', 'auth_factory', atop='browserid')
        add('dbt', 'dbt_factory', below='browserid', atop='auth')
        self.assertRaises(CyclicDependencyError, tweens.implicit)

class TestCyclicDependencyError(unittest.TestCase):
    def _makeOne(self, cycles):
        from pyramid.tweens import CyclicDependencyError
        return CyclicDependencyError(cycles)

    def test___str__(self):
        exc = self._makeOne({'a':['c', 'd'], 'c':['a']})
        result = str(exc)
        self.assertEqual(result,
                         "'a' sorts atop ['c', 'd']; 'c' sorts atop ['a']")

