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

    def test_add_implicit_noaliases(self):
        from pyramid.tweens import INGRESS
        from pyramid.tweens import MAIN
        D = {MAIN:MAIN, INGRESS:INGRESS}
        tweens = self._makeOne()
        tweens.add_implicit('name', 'factory')
        self.assertEqual(tweens.names, ['name'])
        self.assertEqual(tweens.factories,
                         {'name':'factory'})
        self.assertEqual(tweens.alias_to_name, D)
        self.assertEqual(tweens.name_to_alias, D)
        self.assertEqual(tweens.order, [('name', INGRESS)])
        self.assertEqual(tweens.ingress_alias_names, ['name'])
        tweens.add_implicit('name2', 'factory2')
        self.assertEqual(tweens.names, ['name',  'name2'])
        self.assertEqual(tweens.factories,
                         {'name':'factory', 'name2':'factory2'})
        self.assertEqual(tweens.alias_to_name, D)
        self.assertEqual(tweens.name_to_alias, D)
        self.assertEqual(tweens.order,
                         [('name', INGRESS), ('name2', INGRESS)])
        self.assertEqual(tweens.ingress_alias_names, ['name', 'name2'])
        tweens.add_implicit('name3', 'factory3', below='name2')
        self.assertEqual(tweens.names,
                         ['name',  'name2', 'name3'])
        self.assertEqual(tweens.factories,
                         {'name':'factory', 'name2':'factory2',
                          'name3':'factory3'})
        self.assertEqual(tweens.alias_to_name, D)
        self.assertEqual(tweens.name_to_alias, D)
        self.assertEqual(tweens.order,
                         [('name', INGRESS), ('name2', INGRESS),
                          ('name2', 'name3')])
        self.assertEqual(tweens.ingress_alias_names, ['name', 'name2'])

    def test_add_implicit_withaliases(self):
        from pyramid.tweens import INGRESS
        from pyramid.tweens import MAIN
        D = {MAIN:MAIN, INGRESS:INGRESS}
        tweens = self._makeOne()
        tweens.add_implicit('name1', 'factory', alias='n1')
        self.assertEqual(tweens.names, ['name1'])
        self.assertEqual(tweens.factories,
                         {'name1':'factory'})
        self.assertEqual(tweens.alias_to_name['n1'], 'name1')
        self.assertEqual(tweens.name_to_alias['name1'], 'n1')
        self.assertEqual(tweens.order, [('n1', INGRESS)])
        self.assertEqual(tweens.ingress_alias_names, ['n1'])
        tweens.add_implicit('name2', 'factory2', alias='n2')
        self.assertEqual(tweens.names, ['name1',  'name2'])
        self.assertEqual(tweens.factories,
                         {'name1':'factory', 'name2':'factory2'})
        self.assertEqual(tweens.alias_to_name['n2'], 'name2')
        self.assertEqual(tweens.name_to_alias['name2'], 'n2')
        self.assertEqual(tweens.order,
                         [('n1', INGRESS), ('n2', INGRESS)])
        self.assertEqual(tweens.ingress_alias_names, ['n1', 'n2'])
        tweens.add_implicit('name3', 'factory3', alias='n3', below='name2')
        self.assertEqual(tweens.names,
                         ['name1',  'name2', 'name3'])
        self.assertEqual(tweens.factories,
                         {'name1':'factory', 'name2':'factory2',
                          'name3':'factory3'})
        self.assertEqual(tweens.alias_to_name['n3'], 'name3')
        self.assertEqual(tweens.name_to_alias['name3'], 'n3')
        self.assertEqual(tweens.order,
                         [('n1', INGRESS), ('n2', INGRESS),
                          ('name2', 'n3')])
        self.assertEqual(tweens.ingress_alias_names, ['n1', 'n2'])

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
        tweens.names = ['name', 'name2']
        tweens.alias_to_name = {'name':'name', 'name2':'name2'}
        tweens.name_to_alias = {'name':'name', 'name2':'name2'}
        tweens.factories = {'name':factory1, 'name2':factory2}
        self.assertEqual(tweens(None, None), '123')

    def test___call___implicit_with_aliasnames_different_than_names(self):
        tweens = self._makeOne()
        def factory1(handler, registry):
            return handler
        def factory2(handler, registry):
            return '123'
        tweens.names = ['foo1', 'foo2']
        tweens.alias_to_name = {'foo1':'name', 'foo2':'name2'}
        tweens.name_to_alias = {'name':'foo1', 'name2':'foo2'}
        tweens.factories = {'name':factory1, 'name2':factory2}
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

    def test_implicit_ordering_withaliases(self):
        from pyramid.tweens import MAIN
        tweens = self._makeOne()
        add = tweens.add_implicit
        add('exceptionview', 'excview_factory', alias='e', below=MAIN)
        add('auth', 'auth_factory', atop='b')
        add('retry', 'retry_factory', below='t', atop='exceptionview')
        add('browserid', 'browserid_factory', alias='b')
        add('txnmgr', 'txnmgr_factory', alias='t', atop='exceptionview')
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

