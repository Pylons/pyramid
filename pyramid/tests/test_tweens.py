import unittest

class TestTweens(unittest.TestCase):
    def _makeOne(self):
        from pyramid.tweens import Tweens
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
        tweens = self._makeOne()
        tweens.add_implicit('name', 'factory')
        self.assertEqual(tweens.names, ['name'])
        self.assertEqual(tweens.factories,
                         {'name':'factory'})
        self.assertEqual(tweens.alias_to_name['name'], 'name')
        self.assertEqual(tweens.name_to_alias['name'], 'name')
        self.assertEqual(tweens.order, [(INGRESS, 'name')])
        tweens.add_implicit('name2', 'factory2')
        self.assertEqual(tweens.names, ['name',  'name2'])
        self.assertEqual(tweens.factories,
                         {'name':'factory', 'name2':'factory2'})
        self.assertEqual(tweens.alias_to_name['name2'], 'name2')
        self.assertEqual(tweens.name_to_alias['name2'], 'name2')
        self.assertEqual(tweens.order,
                         [(INGRESS, 'name'), (INGRESS, 'name2')])
        tweens.add_implicit('name3', 'factory3', over='name2')
        self.assertEqual(tweens.names,
                         ['name',  'name2', 'name3'])
        self.assertEqual(tweens.factories,
                         {'name':'factory', 'name2':'factory2',
                          'name3':'factory3'})
        self.assertEqual(tweens.alias_to_name['name3'], 'name3')
        self.assertEqual(tweens.name_to_alias['name3'], 'name3')
        self.assertEqual(tweens.order,
                         [(INGRESS, 'name'), (INGRESS, 'name2'),
                          ('name3', 'name2')])

    def test_add_implicit_withaliases(self):
        from pyramid.tweens import INGRESS
        tweens = self._makeOne()
        tweens.add_implicit('name1', 'factory', alias='n1')
        self.assertEqual(tweens.names, ['name1'])
        self.assertEqual(tweens.factories,
                         {'name1':'factory'})
        self.assertEqual(tweens.alias_to_name['n1'], 'name1')
        self.assertEqual(tweens.name_to_alias['name1'], 'n1')
        self.assertEqual(tweens.order, [(INGRESS, 'n1')])
        tweens.add_implicit('name2', 'factory2', alias='n2')
        self.assertEqual(tweens.names, ['name1',  'name2'])
        self.assertEqual(tweens.factories,
                         {'name1':'factory', 'name2':'factory2'})
        self.assertEqual(tweens.alias_to_name['n2'], 'name2')
        self.assertEqual(tweens.name_to_alias['name2'], 'n2')
        self.assertEqual(tweens.order,
                         [(INGRESS, 'n1'), (INGRESS, 'n2')])
        tweens.add_implicit('name3', 'factory3', alias='n3', over='name2')
        self.assertEqual(tweens.names,
                         ['name1',  'name2', 'name3'])
        self.assertEqual(tweens.factories,
                         {'name1':'factory', 'name2':'factory2',
                          'name3':'factory3'})
        self.assertEqual(tweens.alias_to_name['n3'], 'name3')
        self.assertEqual(tweens.name_to_alias['name3'], 'n3')
        self.assertEqual(tweens.order,
                         [(INGRESS, 'n1'), (INGRESS, 'n2'),
                          ('n3', 'name2')])

    def test___call___explicit(self):
        tweens = self._makeOne()
        def factory1(handler, registry):
            return handler
        def factory2(handler, registry):
            return '123'
        tweens.explicit = [('name', factory1), ('name', factory2)]
        self.assertEqual(tweens(None, None), '123')

    def test___call___implicit(self):
        from pyramid.tweens import INGRESS
        tweens = self._makeOne()
        def factory1(handler, registry):
            return handler
        def factory2(handler, registry):
            return '123'
        tweens.names = ['name', 'name2']
        tweens.alias_to_name = {'name':'name', 'name2':'name2'}
        tweens.name_to_alias = {'name':'name', 'name2':'name2'}
        tweens.req_under = set(['name', 'name2'])
        tweens.order = [(INGRESS, 'name'), (INGRESS, 'name2')]
        tweens.factories = {'name':factory1, 'name2':factory2}
        self.assertEqual(tweens(None, None), '123')

    def test___call___implicit_with_aliasnames_different_than_names(self):
        from pyramid.tweens import INGRESS
        tweens = self._makeOne()
        def factory1(handler, registry):
            return handler
        def factory2(handler, registry):
            return '123'
        tweens.names = ['name', 'name2']
        tweens.alias_to_name = {'foo1':'name', 'foo2':'name2'}
        tweens.name_to_alias = {'name':'foo1', 'name2':'foo2'}
        tweens.req_under = set(['foo1', 'foo2'])
        tweens.order = [(INGRESS, 'name'), (INGRESS, 'name2')]
        tweens.factories = {'name':factory1, 'name2':factory2}
        self.assertEqual(tweens(None, None), '123')

    def test_implicit_ordering_1(self):
        tweens = self._makeOne()
        tweens.add_implicit('name1', 'factory1')
        tweens.add_implicit('name2', 'factory2')
        self.assertEqual(tweens.implicit(),
                         [
                             ('name2', 'factory2'),
                             ('name1', 'factory1'),
                             ])

    def test_implicit_ordering_2(self):
        from pyramid.tweens import MAIN
        tweens = self._makeOne()
        tweens.add_implicit('name1', 'factory1')
        tweens.add_implicit('name2', 'factory2', over=MAIN)
        self.assertEqual(tweens.implicit(),
                         [
                             ('name1', 'factory1'),
                             ('name2', 'factory2'),
                             ])

    def test_implicit_ordering_3(self):
        from pyramid.tweens import MAIN
        tweens = self._makeOne()
        add = tweens.add_implicit
        add('auth', 'auth_factory', under='browserid')
        add('dbt', 'dbt_factory') 
        add('retry', 'retry_factory', over='txnmgr', under='exceptionview')
        add('browserid', 'browserid_factory')
        add('txnmgr', 'txnmgr_factory', under='exceptionview')
        add('exceptionview', 'excview_factory', over=MAIN)
        self.assertEqual(tweens.implicit(),
                         [
                             ('browserid', 'browserid_factory'),
                             ('auth', 'auth_factory'),
                             ('dbt', 'dbt_factory'),
                             ('exceptionview', 'excview_factory'),
                             ('retry', 'retry_factory'),
                             ('txnmgr', 'txnmgr_factory'),
                             ])

    def test_implicit_ordering_4(self):
        from pyramid.tweens import MAIN
        tweens = self._makeOne()
        add = tweens.add_implicit
        add('exceptionview', 'excview_factory', over=MAIN)
        add('auth', 'auth_factory', under='browserid')
        add('retry', 'retry_factory', over='txnmgr', under='exceptionview')
        add('browserid', 'browserid_factory')
        add('txnmgr', 'txnmgr_factory', under='exceptionview')
        add('dbt', 'dbt_factory') 
        self.assertEqual(tweens.implicit(),
                         [
                             ('dbt', 'dbt_factory'),
                             ('browserid', 'browserid_factory'),
                             ('auth', 'auth_factory'),
                             ('exceptionview', 'excview_factory'),
                             ('retry', 'retry_factory'),
                             ('txnmgr', 'txnmgr_factory'),
                             ])

    def test_implicit_ordering_5(self):
        from pyramid.tweens import MAIN, INGRESS
        tweens = self._makeOne()
        add = tweens.add_implicit
        add('exceptionview', 'excview_factory', over=MAIN)
        add('auth', 'auth_factory', under=INGRESS)
        add('retry', 'retry_factory', over='txnmgr', under='exceptionview')
        add('browserid', 'browserid_factory', under=INGRESS)
        add('txnmgr', 'txnmgr_factory', under='exceptionview', over=MAIN)
        add('dbt', 'dbt_factory') 
        self.assertEqual(tweens.implicit(),
                         [
                             ('dbt', 'dbt_factory'),
                             ('browserid', 'browserid_factory'),
                             ('auth', 'auth_factory'),
                             ('exceptionview', 'excview_factory'),
                             ('retry', 'retry_factory'),
                             ('txnmgr', 'txnmgr_factory'),
                             ])

    def test_implicit_ordering_withaliases(self):
        from pyramid.tweens import MAIN
        tweens = self._makeOne()
        add = tweens.add_implicit
        add('exceptionview', 'excview_factory', alias='e', over=MAIN)
        add('auth', 'auth_factory', under='b')
        add('retry', 'retry_factory', over='t', under='exceptionview')
        add('browserid', 'browserid_factory', alias='b')
        add('txnmgr', 'txnmgr_factory', alias='t', under='exceptionview')
        add('dbt', 'dbt_factory') 
        self.assertEqual(tweens.implicit(),
                         [
                             ('dbt', 'dbt_factory'),
                             ('browserid', 'browserid_factory'),
                             ('auth', 'auth_factory'),
                             ('exceptionview', 'excview_factory'),
                             ('retry', 'retry_factory'),
                             ('txnmgr', 'txnmgr_factory'),
                          ])

    def test_implicit_ordering_withaliases2(self):
        from pyramid.tweens import MAIN
        tweens = self._makeOne()
        add = tweens.add_implicit
        add('exceptionview', 'excview_factory', alias='e', over=MAIN)
        add('auth', 'auth_factory', alias='a', under='b')
        add('retry', 'retry_factory', alias='r', over='t', under='e')
        add('browserid', 'browserid_factory', alias='b')
        add('txnmgr', 'txnmgr_factory', alias='t', under='e')
        add('dbt', 'dbt_factory', alias='d') 
        self.assertEqual(tweens.implicit(),
                         [
                             ('dbt', 'dbt_factory'),
                             ('browserid', 'browserid_factory'),
                             ('auth', 'auth_factory'),
                             ('exceptionview', 'excview_factory'),
                             ('retry', 'retry_factory'),
                             ('txnmgr', 'txnmgr_factory'),
                          ])

    def test_implicit_ordering_missing_over_partial(self):
        from pyramid.exceptions import ConfigurationError
        tweens = self._makeOne()
        add = tweens.add_implicit
        add('dbt', 'dbt_factory')
        add('auth', 'auth_factory', under='browserid')
        add('retry', 'retry_factory', over='txnmgr', under='exceptionview')
        add('browserid', 'browserid_factory')
        self.assertRaises(ConfigurationError, tweens.implicit)

    def test_implicit_ordering_missing_under_partial(self):
        from pyramid.exceptions import ConfigurationError
        tweens = self._makeOne()
        add = tweens.add_implicit
        add('dbt', 'dbt_factory')
        add('auth', 'auth_factory', under='txnmgr')
        add('retry', 'retry_factory', over='dbt', under='exceptionview')
        add('browserid', 'browserid_factory')
        self.assertRaises(ConfigurationError, tweens.implicit)

    def test_implicit_ordering_missing_over_and_under_partials(self):
        from pyramid.exceptions import ConfigurationError
        tweens = self._makeOne()
        add = tweens.add_implicit
        add('dbt', 'dbt_factory')
        add('auth', 'auth_factory', under='browserid')
        add('retry', 'retry_factory', over='foo', under='txnmgr')
        add('browserid', 'browserid_factory')
        self.assertRaises(ConfigurationError, tweens.implicit)

    def test_implicit_ordering_missing_over_partial_with_fallback(self):
        from pyramid.tweens import MAIN
        tweens = self._makeOne()
        add = tweens.add_implicit
        add('exceptionview', 'excview_factory', over=MAIN)
        add('auth', 'auth_factory', under='browserid')
        add('retry', 'retry_factory', over=('txnmgr',MAIN),
                                      under='exceptionview')
        add('browserid', 'browserid_factory')
        add('dbt', 'dbt_factory') 
        self.assertEqual(tweens.implicit(),
                         [
                             ('dbt', 'dbt_factory'),
                             ('browserid', 'browserid_factory'),
                             ('auth', 'auth_factory'),
                             ('exceptionview', 'excview_factory'),
                             ('retry', 'retry_factory'),
                             ])

    def test_implicit_ordering_missing_under_partial_with_fallback(self):
        from pyramid.tweens import MAIN
        tweens = self._makeOne()
        add = tweens.add_implicit
        add('exceptionview', 'excview_factory', over=MAIN)
        add('auth', 'auth_factory', under=('txnmgr','browserid'))
        add('retry', 'retry_factory', under='exceptionview')
        add('browserid', 'browserid_factory')
        add('dbt', 'dbt_factory')
        self.assertEqual(tweens.implicit(),
                         [
                             ('dbt', 'dbt_factory'),
                             ('browserid', 'browserid_factory'),
                             ('auth', 'auth_factory'),
                             ('exceptionview', 'excview_factory'),
                             ('retry', 'retry_factory'),
                             ])

    def test_implicit_ordering_missing_partial_with_aliases(self):
        from pyramid.tweens import MAIN
        tweens = self._makeOne()
        add = tweens.add_implicit
        add('exceptionview', 'excview_factory', alias='e', over=MAIN)
        add('retry', 'retry_factory', over=('txnmgr',MAIN), under='e')
        add('browserid', 'browserid_factory')
        self.assertEqual(tweens.implicit(),
                         [
                             ('browserid', 'browserid_factory'),
                             ('exceptionview', 'excview_factory'),
                             ('retry', 'retry_factory'),
                             ])

    def test_implicit_ordering_with_partial_fallbacks(self):
        from pyramid.tweens import MAIN
        tweens = self._makeOne()
        add = tweens.add_implicit
        add('exceptionview', 'excview_factory', alias='e', over=('b', MAIN))
        add('retry', 'retry_factory', under='e')
        add('browserid', 'browserid_factory', over=('txnmgr', 'e'))
        self.assertEqual(tweens.implicit(),
                         [
                             ('browserid', 'browserid_factory'),
                             ('exceptionview', 'excview_factory'),
                             ('retry', 'retry_factory'),
                             ])

    def test_implicit_ordering_with_multiple_matching_fallbacks(self):
        from pyramid.tweens import MAIN
        tweens = self._makeOne()
        add = tweens.add_implicit
        add('exceptionview', 'excview_factory', alias='e', over=MAIN)
        add('retry', 'retry_factory', under='e')
        add('browserid', 'browserid_factory', over=('retry', 'e'))
        self.assertEqual(tweens.implicit(),
                         [
                             ('browserid', 'browserid_factory'),
                             ('exceptionview', 'excview_factory'),
                             ('retry', 'retry_factory'),
                             ])

    def test_implicit_ordering_with_missing_fallbacks(self):
        from pyramid.exceptions import ConfigurationError
        from pyramid.tweens import MAIN
        tweens = self._makeOne()
        add = tweens.add_implicit
        add('exceptionview', 'excview_factory', alias='e', over=MAIN)
        add('retry', 'retry_factory', under='e')
        add('browserid', 'browserid_factory', over=('txnmgr', 'auth'))
        self.assertRaises(ConfigurationError, tweens.implicit)

    def test_implicit_ordering_conflict_direct(self):
        from pyramid.tweens import CyclicDependencyError
        tweens = self._makeOne()
        add = tweens.add_implicit
        add('browserid', 'browserid_factory')
        add('auth', 'auth_factory', over='browserid', under='browserid')
        self.assertRaises(CyclicDependencyError, tweens.implicit)

    def test_implicit_ordering_conflict_indirect(self):
        from pyramid.tweens import CyclicDependencyError
        tweens = self._makeOne()
        add = tweens.add_implicit
        add('browserid', 'browserid_factory')
        add('auth', 'auth_factory', over='browserid')
        add('dbt', 'dbt_factory', under='browserid', over='auth')
        self.assertRaises(CyclicDependencyError, tweens.implicit)

class TestCyclicDependencyError(unittest.TestCase):
    def _makeOne(self, cycles):
        from pyramid.tweens import CyclicDependencyError
        return CyclicDependencyError(cycles)

    def test___str__(self):
        exc = self._makeOne({'a':['c', 'd'], 'c':['a']})
        result = str(exc)
        self.assertTrue("'a' sorts over ['c', 'd']" in result)
        self.assertTrue("'c' sorts over ['a']" in result)

