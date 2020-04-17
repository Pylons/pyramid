import sys
import unittest

from pyramid.util import bytes_, text_


class Test_InstancePropertyHelper(unittest.TestCase):
    def _makeOne(self):
        cls = self._getTargetClass()
        return cls()

    def _getTargetClass(self):
        from pyramid.util import InstancePropertyHelper

        return InstancePropertyHelper

    def test_callable(self):
        def worker(obj):
            return obj.bar

        foo = Dummy()
        helper = self._getTargetClass()
        helper.set_property(foo, worker)
        foo.bar = 1
        self.assertEqual(1, foo.worker)
        foo.bar = 2
        self.assertEqual(2, foo.worker)

    def test_callable_with_name(self):
        def worker(obj):
            return obj.bar

        foo = Dummy()
        helper = self._getTargetClass()
        helper.set_property(foo, worker, name='x')
        foo.bar = 1
        self.assertEqual(1, foo.x)
        foo.bar = 2
        self.assertEqual(2, foo.x)

    def test_callable_with_reify(self):
        def worker(obj):
            return obj.bar

        foo = Dummy()
        helper = self._getTargetClass()
        helper.set_property(foo, worker, reify=True)
        foo.bar = 1
        self.assertEqual(1, foo.worker)
        foo.bar = 2
        self.assertEqual(1, foo.worker)

    def test_callable_with_name_reify(self):
        def worker(obj):
            return obj.bar

        foo = Dummy()
        helper = self._getTargetClass()
        helper.set_property(foo, worker, name='x')
        helper.set_property(foo, worker, name='y', reify=True)
        foo.bar = 1
        self.assertEqual(1, foo.y)
        self.assertEqual(1, foo.x)
        foo.bar = 2
        self.assertEqual(2, foo.x)
        self.assertEqual(1, foo.y)

    def test_property_without_name(self):
        def worker(obj):  # pragma: no cover
            pass

        foo = Dummy()
        helper = self._getTargetClass()
        self.assertRaises(
            ValueError, helper.set_property, foo, property(worker)
        )

    def test_property_with_name(self):
        def worker(obj):
            return obj.bar

        foo = Dummy()
        helper = self._getTargetClass()
        helper.set_property(foo, property(worker), name='x')
        foo.bar = 1
        self.assertEqual(1, foo.x)
        foo.bar = 2
        self.assertEqual(2, foo.x)

    def test_property_with_reify(self):
        def worker(obj):  # pragma: no cover
            pass

        foo = Dummy()
        helper = self._getTargetClass()
        self.assertRaises(
            ValueError,
            helper.set_property,
            foo,
            property(worker),
            name='x',
            reify=True,
        )

    def test_override_property(self):
        def worker(obj):
            pass

        foo = Dummy()
        helper = self._getTargetClass()
        helper.set_property(foo, worker, name='x')
        self.assertIsNone(foo.x)
        foo.x = 1
        self.assertEqual(foo.x, 1)
        del foo.x
        self.assertIsNone(foo.x)

    def test_override_reify(self):
        def worker(obj):
            pass

        foo = Dummy()
        helper = self._getTargetClass()
        helper.set_property(foo, worker, name='x', reify=True)
        self.assertIsNone(foo.x)
        foo.x = 1
        self.assertEqual(1, foo.x)
        foo.x = 2
        self.assertEqual(2, foo.x)

    def test_reset_property(self):
        foo = Dummy()
        helper = self._getTargetClass()
        helper.set_property(foo, lambda _: 1, name='x')
        self.assertEqual(1, foo.x)
        helper.set_property(foo, lambda _: 2, name='x')
        self.assertEqual(2, foo.x)

    def test_reset_reify(self):
        """ This is questionable behavior, but may as well get notified
        if it changes."""
        foo = Dummy()
        helper = self._getTargetClass()
        helper.set_property(foo, lambda _: 1, name='x', reify=True)
        self.assertEqual(1, foo.x)
        helper.set_property(foo, lambda _: 2, name='x', reify=True)
        self.assertEqual(1, foo.x)

    def test_make_property(self):
        from pyramid.decorator import reify

        helper = self._getTargetClass()
        name, fn = helper.make_property(lambda x: 1, name='x', reify=True)
        self.assertEqual(name, 'x')
        self.assertTrue(isinstance(fn, reify))

    def test_apply_properties_with_iterable(self):
        foo = Dummy()
        helper = self._getTargetClass()
        x = helper.make_property(lambda _: 1, name='x', reify=True)
        y = helper.make_property(lambda _: 2, name='y')
        helper.apply_properties(foo, [x, y])
        self.assertEqual(1, foo.x)
        self.assertEqual(2, foo.y)

    def test_apply_properties_with_dict(self):
        foo = Dummy()
        helper = self._getTargetClass()
        x_name, x_fn = helper.make_property(lambda _: 1, name='x', reify=True)
        y_name, y_fn = helper.make_property(lambda _: 2, name='y')
        helper.apply_properties(foo, {x_name: x_fn, y_name: y_fn})
        self.assertEqual(1, foo.x)
        self.assertEqual(2, foo.y)

    def test_make_property_unicode(self):
        from pyramid.exceptions import ConfigurationError

        cls = self._getTargetClass()
        name = b'La Pe\xc3\xb1a'

        def make_bad_name():
            cls.make_property(lambda x: 1, name=name, reify=True)

        self.assertRaises(ConfigurationError, make_bad_name)

    def test_add_property(self):
        helper = self._makeOne()
        helper.add_property(lambda obj: obj.bar, name='x', reify=True)
        helper.add_property(lambda obj: obj.bar, name='y')
        self.assertEqual(len(helper.properties), 2)
        foo = Dummy()
        helper.apply(foo)
        foo.bar = 1
        self.assertEqual(foo.x, 1)
        self.assertEqual(foo.y, 1)
        foo.bar = 2
        self.assertEqual(foo.x, 1)
        self.assertEqual(foo.y, 2)

    def test_apply_multiple_times(self):
        helper = self._makeOne()
        helper.add_property(lambda obj: 1, name='x')
        foo, bar = Dummy(), Dummy()
        helper.apply(foo)
        self.assertEqual(foo.x, 1)
        helper.add_property(lambda obj: 2, name='x')
        helper.apply(bar)
        self.assertEqual(foo.x, 1)
        self.assertEqual(bar.x, 2)


class Test_InstancePropertyMixin(unittest.TestCase):
    def _makeOne(self):
        cls = self._getTargetClass()

        class Foo(cls):
            pass

        return Foo()

    def _getTargetClass(self):
        from pyramid.util import InstancePropertyMixin

        return InstancePropertyMixin

    def test_callable(self):
        def worker(obj):
            return obj.bar

        foo = self._makeOne()
        foo.set_property(worker)
        foo.bar = 1
        self.assertEqual(1, foo.worker)
        foo.bar = 2
        self.assertEqual(2, foo.worker)

    def test_callable_with_name(self):
        def worker(obj):
            return obj.bar

        foo = self._makeOne()
        foo.set_property(worker, name='x')
        foo.bar = 1
        self.assertEqual(1, foo.x)
        foo.bar = 2
        self.assertEqual(2, foo.x)

    def test_callable_with_reify(self):
        def worker(obj):
            return obj.bar

        foo = self._makeOne()
        foo.set_property(worker, reify=True)
        foo.bar = 1
        self.assertEqual(1, foo.worker)
        foo.bar = 2
        self.assertEqual(1, foo.worker)

    def test_callable_with_name_reify(self):
        def worker(obj):
            return obj.bar

        foo = self._makeOne()
        foo.set_property(worker, name='x')
        foo.set_property(worker, name='y', reify=True)
        foo.bar = 1
        self.assertEqual(1, foo.y)
        self.assertEqual(1, foo.x)
        foo.bar = 2
        self.assertEqual(2, foo.x)
        self.assertEqual(1, foo.y)

    def test_property_without_name(self):
        def worker(obj):  # pragma: no cover
            pass

        foo = self._makeOne()
        self.assertRaises(ValueError, foo.set_property, property(worker))

    def test_property_with_name(self):
        def worker(obj):
            return obj.bar

        foo = self._makeOne()
        foo.set_property(property(worker), name='x')
        foo.bar = 1
        self.assertEqual(1, foo.x)
        foo.bar = 2
        self.assertEqual(2, foo.x)

    def test_property_with_reify(self):
        def worker(obj):  # pragma: no cover
            pass

        foo = self._makeOne()
        self.assertRaises(
            ValueError,
            foo.set_property,
            property(worker),
            name='x',
            reify=True,
        )

    def test_override_property(self):
        def worker(obj):
            pass

        foo = self._makeOne()
        foo.set_property(worker, name='x')
        self.assertIsNone(foo.x)
        foo.x = 1
        self.assertEqual(foo.x, 1)
        del foo.x
        self.assertIsNone(foo.x)

    def test_override_reify(self):
        def worker(obj):
            pass

        foo = self._makeOne()
        foo.set_property(worker, name='x', reify=True)
        self.assertIsNone(foo.x)
        foo.x = 1
        self.assertEqual(1, foo.x)
        foo.x = 2
        self.assertEqual(2, foo.x)

    def test_reset_property(self):
        foo = self._makeOne()
        foo.set_property(lambda _: 1, name='x')
        self.assertEqual(1, foo.x)
        foo.set_property(lambda _: 2, name='x')
        self.assertEqual(2, foo.x)

    def test_reset_reify(self):
        """ This is questionable behavior, but may as well get notified
        if it changes."""
        foo = self._makeOne()
        foo.set_property(lambda _: 1, name='x', reify=True)
        self.assertEqual(1, foo.x)
        foo.set_property(lambda _: 2, name='x', reify=True)
        self.assertEqual(1, foo.x)

    def test_new_class_keeps_parent_module_name(self):
        foo = self._makeOne()
        self.assertEqual(foo.__module__, 'tests.test_util')
        self.assertEqual(foo.__class__.__module__, 'tests.test_util')
        foo.set_property(lambda _: 1, name='x', reify=True)
        self.assertEqual(foo.__module__, 'tests.test_util')
        self.assertEqual(foo.__class__.__module__, 'tests.test_util')


class Test_WeakOrderedSet(unittest.TestCase):
    def _makeOne(self):
        from pyramid.config import WeakOrderedSet

        return WeakOrderedSet()

    def test_ctor(self):
        wos = self._makeOne()
        self.assertEqual(len(wos), 0)
        self.assertEqual(wos.last, None)

    def test_add_item(self):
        wos = self._makeOne()
        reg = Dummy()
        wos.add(reg)
        self.assertEqual(list(wos), [reg])
        self.assertTrue(reg in wos)
        self.assertEqual(wos.last, reg)

    def test_add_multiple_items(self):
        wos = self._makeOne()
        reg1 = Dummy()
        reg2 = Dummy()
        wos.add(reg1)
        wos.add(reg2)
        self.assertEqual(len(wos), 2)
        self.assertEqual(list(wos), [reg1, reg2])
        self.assertTrue(reg1 in wos)
        self.assertTrue(reg2 in wos)
        self.assertEqual(wos.last, reg2)

    def test_add_duplicate_items(self):
        wos = self._makeOne()
        reg = Dummy()
        wos.add(reg)
        wos.add(reg)
        self.assertEqual(len(wos), 1)
        self.assertEqual(list(wos), [reg])
        self.assertTrue(reg in wos)
        self.assertEqual(wos.last, reg)

    def test_weakref_removal(self):
        wos = self._makeOne()
        reg = Dummy()
        wos.add(reg)
        wos.remove(reg)
        self.assertEqual(len(wos), 0)
        self.assertEqual(list(wos), [])
        self.assertEqual(wos.last, None)

    def test_last_updated(self):
        wos = self._makeOne()
        reg = Dummy()
        reg2 = Dummy()
        wos.add(reg)
        wos.add(reg2)
        wos.remove(reg2)
        self.assertEqual(len(wos), 1)
        self.assertEqual(list(wos), [reg])
        self.assertEqual(wos.last, reg)

    def test_empty(self):
        wos = self._makeOne()
        reg = Dummy()
        reg2 = Dummy()
        wos.add(reg)
        wos.add(reg2)
        wos.empty()
        self.assertEqual(len(wos), 0)
        self.assertEqual(list(wos), [])
        self.assertEqual(wos.last, None)


class Test_strings_differ(unittest.TestCase):
    def _callFUT(self, *args, **kw):
        from pyramid.util import strings_differ

        return strings_differ(*args, **kw)

    def test_it_bytes(self):
        self.assertFalse(self._callFUT(b'foo', b'foo'))
        self.assertTrue(self._callFUT(b'123', b'345'))
        self.assertTrue(self._callFUT(b'1234', b'123'))
        self.assertTrue(self._callFUT(b'123', b'1234'))

    def test_it_native_str(self):
        self.assertFalse(self._callFUT('123', '123'))
        self.assertTrue(self._callFUT('123', '1234'))

    def test_it(self):
        result = self._callFUT(b'foo', b'foo')
        self.assertFalse(result)

        result = self._callFUT(b'123', b'abc')
        self.assertTrue(result)


class Test_object_description(unittest.TestCase):
    def _callFUT(self, object):
        from pyramid.util import object_description

        return object_description(object)

    def test_string(self):
        self.assertEqual(self._callFUT('abc'), 'abc')

    def test_int(self):
        self.assertEqual(self._callFUT(1), '1')

    def test_bool(self):
        self.assertEqual(self._callFUT(True), 'True')

    def test_None(self):
        self.assertEqual(self._callFUT(None), 'None')

    def test_float(self):
        self.assertEqual(self._callFUT(1.2), '1.2')

    def test_tuple(self):
        self.assertEqual(self._callFUT(('a', 'b')), "('a', 'b')")

    def test_set(self):
        self.assertEqual(self._callFUT(set(['a'])), "{'a'}")

    def test_list(self):
        self.assertEqual(self._callFUT(['a']), "['a']")

    def test_dict(self):
        self.assertEqual(self._callFUT({'a': 1}), "{'a': 1}")

    def test_nomodule(self):
        o = object()
        self.assertEqual(self._callFUT(o), 'object %s' % str(o))

    def test_module(self):
        import pyramid

        self.assertEqual(self._callFUT(pyramid), 'module pyramid')

    def test_method(self):
        self.assertEqual(
            self._callFUT(self.test_method),
            'method test_method of class tests.test_util.'
            'Test_object_description',
        )

    def test_class(self):
        self.assertEqual(
            self._callFUT(self.__class__),
            'class tests.test_util.Test_object_description',
        )

    def test_function(self):
        self.assertEqual(
            self._callFUT(dummyfunc), 'function tests.test_util.dummyfunc'
        )

    def test_instance(self):
        inst = Dummy()
        self.assertEqual(self._callFUT(inst), "object %s" % str(inst))

    def test_shortened_repr(self):
        inst = ['1'] * 1000
        self.assertEqual(self._callFUT(inst), str(inst)[:100] + ' ... ]')


class TestTopologicalSorter(unittest.TestCase):
    def _makeOne(self, *arg, **kw):
        from pyramid.util import TopologicalSorter

        return TopologicalSorter(*arg, **kw)

    def test_remove(self):
        inst = self._makeOne()
        inst.names.append('name')
        inst.name2val['name'] = 1
        inst.req_after.add('name')
        inst.req_before.add('name')
        inst.name2after['name'] = ('bob',)
        inst.name2before['name'] = ('fred',)
        inst.order.append(('bob', 'name'))
        inst.order.append(('name', 'fred'))
        inst.remove('name')
        self.assertFalse(inst.names)
        self.assertFalse(inst.req_before)
        self.assertFalse(inst.req_after)
        self.assertFalse(inst.name2before)
        self.assertFalse(inst.name2after)
        self.assertFalse(inst.name2val)
        self.assertFalse(inst.order)

    def test_add(self):
        from pyramid.util import LAST

        sorter = self._makeOne()
        sorter.add('name', 'factory')
        self.assertEqual(sorter.names, ['name'])
        self.assertEqual(sorter.name2val, {'name': 'factory'})
        self.assertEqual(sorter.order, [('name', LAST)])
        sorter.add('name2', 'factory2')
        self.assertEqual(sorter.names, ['name', 'name2'])
        self.assertEqual(
            sorter.name2val, {'name': 'factory', 'name2': 'factory2'}
        )
        self.assertEqual(sorter.order, [('name', LAST), ('name2', LAST)])
        sorter.add('name3', 'factory3', before='name2')
        self.assertEqual(sorter.names, ['name', 'name2', 'name3'])
        self.assertEqual(
            sorter.name2val,
            {'name': 'factory', 'name2': 'factory2', 'name3': 'factory3'},
        )
        self.assertEqual(
            sorter.order, [('name', LAST), ('name2', LAST), ('name3', 'name2')]
        )

    def test_sorted_ordering_1(self):
        sorter = self._makeOne()
        sorter.add('name1', 'factory1')
        sorter.add('name2', 'factory2')
        self.assertEqual(
            sorter.sorted(), [('name1', 'factory1'), ('name2', 'factory2')]
        )

    def test_sorted_ordering_2(self):
        from pyramid.util import FIRST

        sorter = self._makeOne()
        sorter.add('name1', 'factory1')
        sorter.add('name2', 'factory2', after=FIRST)
        self.assertEqual(
            sorter.sorted(), [('name2', 'factory2'), ('name1', 'factory1')]
        )

    def test_sorted_ordering_3(self):
        from pyramid.util import FIRST

        sorter = self._makeOne()
        add = sorter.add
        add('auth', 'auth_factory', after='browserid')
        add('dbt', 'dbt_factory')
        add('retry', 'retry_factory', before='txnmgr', after='exceptionview')
        add('browserid', 'browserid_factory')
        add('txnmgr', 'txnmgr_factory', after='exceptionview')
        add('exceptionview', 'excview_factory', after=FIRST)
        self.assertEqual(
            sorter.sorted(),
            [
                ('exceptionview', 'excview_factory'),
                ('retry', 'retry_factory'),
                ('txnmgr', 'txnmgr_factory'),
                ('dbt', 'dbt_factory'),
                ('browserid', 'browserid_factory'),
                ('auth', 'auth_factory'),
            ],
        )

    def test_sorted_ordering_4(self):
        from pyramid.util import FIRST

        sorter = self._makeOne()
        add = sorter.add
        add('exceptionview', 'excview_factory', after=FIRST)
        add('auth', 'auth_factory', after='browserid')
        add('retry', 'retry_factory', before='txnmgr', after='exceptionview')
        add('browserid', 'browserid_factory')
        add('txnmgr', 'txnmgr_factory', after='exceptionview')
        add('dbt', 'dbt_factory')
        self.assertEqual(
            sorter.sorted(),
            [
                ('exceptionview', 'excview_factory'),
                ('retry', 'retry_factory'),
                ('txnmgr', 'txnmgr_factory'),
                ('browserid', 'browserid_factory'),
                ('auth', 'auth_factory'),
                ('dbt', 'dbt_factory'),
            ],
        )

    def test_sorted_ordering_5(self):
        from pyramid.util import LAST, FIRST

        sorter = self._makeOne()
        add = sorter.add
        add('exceptionview', 'excview_factory')
        add('auth', 'auth_factory', after=FIRST)
        add('retry', 'retry_factory', before='txnmgr', after='exceptionview')
        add('browserid', 'browserid_factory', after=FIRST)
        add('txnmgr', 'txnmgr_factory', after='exceptionview', before=LAST)
        add('dbt', 'dbt_factory')
        self.assertEqual(
            sorter.sorted(),
            [
                ('browserid', 'browserid_factory'),
                ('auth', 'auth_factory'),
                ('exceptionview', 'excview_factory'),
                ('retry', 'retry_factory'),
                ('txnmgr', 'txnmgr_factory'),
                ('dbt', 'dbt_factory'),
            ],
        )

    def test_sorted_ordering_missing_before_partial(self):
        from pyramid.exceptions import ConfigurationError

        sorter = self._makeOne()
        add = sorter.add
        add('dbt', 'dbt_factory')
        add('auth', 'auth_factory', after='browserid')
        add('retry', 'retry_factory', before='txnmgr', after='exceptionview')
        add('browserid', 'browserid_factory')
        self.assertRaises(ConfigurationError, sorter.sorted)

    def test_sorted_ordering_missing_after_partial(self):
        from pyramid.exceptions import ConfigurationError

        sorter = self._makeOne()
        add = sorter.add
        add('dbt', 'dbt_factory')
        add('auth', 'auth_factory', after='txnmgr')
        add('retry', 'retry_factory', before='dbt', after='exceptionview')
        add('browserid', 'browserid_factory')
        self.assertRaises(ConfigurationError, sorter.sorted)

    def test_sorted_ordering_missing_before_and_after_partials(self):
        from pyramid.exceptions import ConfigurationError

        sorter = self._makeOne()
        add = sorter.add
        add('dbt', 'dbt_factory')
        add('auth', 'auth_factory', after='browserid')
        add('retry', 'retry_factory', before='foo', after='txnmgr')
        add('browserid', 'browserid_factory')
        self.assertRaises(ConfigurationError, sorter.sorted)

    def test_sorted_ordering_missing_before_partial_with_fallback(self):
        from pyramid.util import LAST

        sorter = self._makeOne()
        add = sorter.add
        add('exceptionview', 'excview_factory', before=LAST)
        add('auth', 'auth_factory', after='browserid')
        add(
            'retry',
            'retry_factory',
            before=('txnmgr', LAST),
            after='exceptionview',
        )
        add('browserid', 'browserid_factory')
        add('dbt', 'dbt_factory')
        self.assertEqual(
            sorter.sorted(),
            [
                ('exceptionview', 'excview_factory'),
                ('retry', 'retry_factory'),
                ('browserid', 'browserid_factory'),
                ('auth', 'auth_factory'),
                ('dbt', 'dbt_factory'),
            ],
        )

    def test_sorted_ordering_missing_after_partial_with_fallback(self):
        from pyramid.util import FIRST

        sorter = self._makeOne()
        add = sorter.add
        add('exceptionview', 'excview_factory', after=FIRST)
        add('auth', 'auth_factory', after=('txnmgr', 'browserid'))
        add('retry', 'retry_factory', after='exceptionview')
        add('browserid', 'browserid_factory')
        add('dbt', 'dbt_factory')
        self.assertEqual(
            sorter.sorted(),
            [
                ('exceptionview', 'excview_factory'),
                ('retry', 'retry_factory'),
                ('browserid', 'browserid_factory'),
                ('auth', 'auth_factory'),
                ('dbt', 'dbt_factory'),
            ],
        )

    def test_sorted_ordering_with_partial_fallbacks(self):
        from pyramid.util import LAST

        sorter = self._makeOne()
        add = sorter.add
        add('exceptionview', 'excview_factory', before=('wontbethere', LAST))
        add('retry', 'retry_factory', after='exceptionview')
        add(
            'browserid', 'browserid_factory', before=('wont2', 'exceptionview')
        )
        self.assertEqual(
            sorter.sorted(),
            [
                ('browserid', 'browserid_factory'),
                ('exceptionview', 'excview_factory'),
                ('retry', 'retry_factory'),
            ],
        )

    def test_sorted_ordering_with_multiple_matching_fallbacks(self):
        from pyramid.util import LAST

        sorter = self._makeOne()
        add = sorter.add
        add('exceptionview', 'excview_factory', before=LAST)
        add('retry', 'retry_factory', after='exceptionview')
        add(
            'browserid', 'browserid_factory', before=('retry', 'exceptionview')
        )
        self.assertEqual(
            sorter.sorted(),
            [
                ('browserid', 'browserid_factory'),
                ('exceptionview', 'excview_factory'),
                ('retry', 'retry_factory'),
            ],
        )

    def test_sorted_ordering_with_missing_fallbacks(self):
        from pyramid.exceptions import ConfigurationError
        from pyramid.util import LAST

        sorter = self._makeOne()
        add = sorter.add
        add('exceptionview', 'excview_factory', before=LAST)
        add('retry', 'retry_factory', after='exceptionview')
        add('browserid', 'browserid_factory', before=('txnmgr', 'auth'))
        self.assertRaises(ConfigurationError, sorter.sorted)

    def test_sorted_ordering_conflict_direct(self):
        from pyramid.exceptions import CyclicDependencyError

        sorter = self._makeOne()
        add = sorter.add
        add('browserid', 'browserid_factory')
        add('auth', 'auth_factory', before='browserid', after='browserid')
        self.assertRaises(CyclicDependencyError, sorter.sorted)

    def test_sorted_ordering_conflict_indirect(self):
        from pyramid.exceptions import CyclicDependencyError

        sorter = self._makeOne()
        add = sorter.add
        add('browserid', 'browserid_factory')
        add('auth', 'auth_factory', before='browserid')
        add('dbt', 'dbt_factory', after='browserid', before='auth')
        self.assertRaises(CyclicDependencyError, sorter.sorted)


class TestSentinel(unittest.TestCase):
    def test_repr(self):
        from pyramid.util import Sentinel

        r = repr(Sentinel('ABC'))
        self.assertEqual(r, 'ABC')


class TestCallableName(unittest.TestCase):
    def _callFUT(self, val):
        from pyramid.util import get_callable_name

        return get_callable_name(val)

    def test_valid_ascii_bytes(self):
        name = b'hello world'
        self.assertEqual(self._callFUT(name), 'hello world')

    def test_valid_ascii_string(self):
        from pyramid.exceptions import ConfigurationError

        name = b'La Pe\xc3\xb1a'.decode('utf-8')
        self.assertRaises(ConfigurationError, self._callFUT, name)

    def test_invalid_ascii(self):
        from pyramid.exceptions import ConfigurationError

        name = b'La Pe\xc3\xb1a'
        self.assertRaises(ConfigurationError, self._callFUT, name)


class Test_hide_attrs(unittest.TestCase):
    def _callFUT(self, obj, *attrs):
        from pyramid.util import hide_attrs

        return hide_attrs(obj, *attrs)

    def _makeDummy(self):
        from pyramid.decorator import reify

        class Dummy:
            x = 1

            @reify
            def foo(self):
                return self.x

        return Dummy()

    def test_restores_attrs(self):
        obj = self._makeDummy()
        obj.bar = 'asdf'
        orig_foo = obj.foo
        with self._callFUT(obj, 'foo', 'bar'):
            obj.foo = object()
            obj.bar = 'nope'
        self.assertEqual(obj.foo, orig_foo)
        self.assertEqual(obj.bar, 'asdf')

    def test_restores_attrs_on_exception(self):
        obj = self._makeDummy()
        orig_foo = obj.foo
        try:
            with self._callFUT(obj, 'foo'):
                obj.foo = object()
                raise RuntimeError()
        except RuntimeError:
            self.assertEqual(obj.foo, orig_foo)
        else:  # pragma: no cover
            self.fail("RuntimeError not raised")

    def test_restores_attrs_to_none(self):
        obj = self._makeDummy()
        obj.foo = None
        with self._callFUT(obj, 'foo'):
            obj.foo = object()
        self.assertEqual(obj.foo, None)

    def test_deletes_attrs(self):
        obj = self._makeDummy()
        with self._callFUT(obj, 'foo'):
            obj.foo = object()
        self.assertTrue('foo' not in obj.__dict__)

    def test_does_not_delete_attr_if_no_attr_to_delete(self):
        obj = self._makeDummy()
        with self._callFUT(obj, 'foo'):
            pass
        self.assertTrue('foo' not in obj.__dict__)


def dummyfunc():  # pragma: no cover
    pass


class Dummy:
    pass


class Test_is_same_domain(unittest.TestCase):
    def _callFUT(self, *args, **kw):
        from pyramid.util import is_same_domain

        return is_same_domain(*args, **kw)

    def test_it(self):
        self.assertTrue(self._callFUT("example.com", "example.com"))
        self.assertFalse(self._callFUT("evil.com", "example.com"))
        self.assertFalse(self._callFUT("evil.example.com", "example.com"))
        self.assertFalse(self._callFUT("example.com", ""))

    def test_with_wildcard(self):
        self.assertTrue(self._callFUT("example.com", ".example.com"))
        self.assertTrue(self._callFUT("good.example.com", ".example.com"))

    def test_with_port(self):
        self.assertTrue(self._callFUT("example.com:8080", "example.com:8080"))
        self.assertFalse(self._callFUT("example.com:8080", "example.com"))
        self.assertFalse(self._callFUT("example.com", "example.com:8080"))


class Test_make_contextmanager(unittest.TestCase):
    def _callFUT(self, *args, **kw):
        from pyramid.util import make_contextmanager

        return make_contextmanager(*args, **kw)

    def test_with_None(self):
        mgr = self._callFUT(None)
        with mgr() as ctx:
            self.assertIsNone(ctx)

    def test_with_generator(self):
        def mygen(ctx):
            yield ctx

        mgr = self._callFUT(mygen)
        with mgr('a') as ctx:
            self.assertEqual(ctx, 'a')

    def test_with_multiple_yield_generator(self):
        def mygen():
            yield 'a'
            yield 'b'

        mgr = self._callFUT(mygen)
        try:
            with mgr() as ctx:
                self.assertEqual(ctx, 'a')
        except RuntimeError:
            pass
        else:  # pragma: no cover
            raise AssertionError('expected raise from multiple yields')

    def test_with_regular_fn(self):
        def mygen():
            return 'a'

        mgr = self._callFUT(mygen)
        with mgr() as ctx:
            self.assertEqual(ctx, 'a')


class Test_takes_one_arg(unittest.TestCase):
    def _callFUT(self, view, attr=None, argname=None):
        from pyramid.util import takes_one_arg

        return takes_one_arg(view, attr=attr, argname=argname)

    def test_requestonly_newstyle_class_no_init(self):
        class foo:
            """ """

        self.assertFalse(self._callFUT(foo))

    def test_requestonly_newstyle_class_init_toomanyargs(self):
        class foo:
            def __init__(self, context, request):
                """ """

        self.assertFalse(self._callFUT(foo))

    def test_requestonly_newstyle_class_init_onearg_named_request(self):
        class foo:
            def __init__(self, request):
                """ """

        self.assertTrue(self._callFUT(foo))

    def test_newstyle_class_init_onearg_named_somethingelse(self):
        class foo:
            def __init__(self, req):
                """ """

        self.assertTrue(self._callFUT(foo))

    def test_newstyle_class_init_defaultargs_firstname_not_request(self):
        class foo:
            def __init__(self, context, request=None):
                """ """

        self.assertFalse(self._callFUT(foo))

    def test_newstyle_class_init_defaultargs_firstname_request(self):
        class foo:
            def __init__(self, request, foo=1, bar=2):
                """ """

        self.assertTrue(self._callFUT(foo, argname='request'))

    def test_newstyle_class_init_firstname_request_with_secondname(self):
        class foo:
            def __init__(self, request, two):
                """ """

        self.assertFalse(self._callFUT(foo))

    def test_newstyle_class_init_noargs(self):
        class foo:
            def __init__():
                """ """

        self.assertFalse(self._callFUT(foo))

    def test_oldstyle_class_no_init(self):
        class foo:
            """ """

        self.assertFalse(self._callFUT(foo))

    def test_oldstyle_class_init_toomanyargs(self):
        class foo:
            def __init__(self, context, request):
                """ """

        self.assertFalse(self._callFUT(foo))

    def test_oldstyle_class_init_onearg_named_request(self):
        class foo:
            def __init__(self, request):
                """ """

        self.assertTrue(self._callFUT(foo))

    def test_oldstyle_class_init_onearg_named_somethingelse(self):
        class foo:
            def __init__(self, req):
                """ """

        self.assertTrue(self._callFUT(foo))

    def test_oldstyle_class_init_defaultargs_firstname_not_request(self):
        class foo:
            def __init__(self, context, request=None):
                """ """

        self.assertFalse(self._callFUT(foo))

    def test_oldstyle_class_init_defaultargs_firstname_request(self):
        class foo:
            def __init__(self, request, foo=1, bar=2):
                """ """

        self.assertTrue(self._callFUT(foo, argname='request'), True)

    def test_oldstyle_class_init_noargs(self):
        class foo:
            def __init__():
                """ """

        self.assertFalse(self._callFUT(foo))

    def test_function_toomanyargs(self):
        def foo(context, request):
            """ """

        self.assertFalse(self._callFUT(foo))

    def test_function_with_attr_false(self):
        def bar(context, request):
            """ """

        def foo(context, request):
            """ """

        foo.bar = bar
        self.assertFalse(self._callFUT(foo, 'bar'))

    def test_function_with_attr_true(self):
        def bar(context, request):
            """ """

        def foo(request):
            """ """

        foo.bar = bar
        self.assertTrue(self._callFUT(foo, 'bar'))

    def test_function_onearg_named_request(self):
        def foo(request):
            """ """

        self.assertTrue(self._callFUT(foo))

    def test_function_onearg_named_somethingelse(self):
        def foo(req):
            """ """

        self.assertTrue(self._callFUT(foo))

    def test_function_defaultargs_firstname_not_request(self):
        def foo(context, request=None):
            """ """

        self.assertFalse(self._callFUT(foo))

    def test_function_defaultargs_firstname_request(self):
        def foo(request, foo=1, bar=2):
            """ """

        self.assertTrue(self._callFUT(foo, argname='request'))

    def test_function_noargs(self):
        def foo():
            """ """

        self.assertFalse(self._callFUT(foo))

    def test_instance_toomanyargs(self):
        class Foo:
            def __call__(self, context, request):
                """ """

        foo = Foo()
        self.assertFalse(self._callFUT(foo))

    def test_instance_defaultargs_onearg_named_request(self):
        class Foo:
            def __call__(self, request):
                """ """

        foo = Foo()
        self.assertTrue(self._callFUT(foo))

    def test_instance_defaultargs_onearg_named_somethingelse(self):
        class Foo:
            def __call__(self, req):
                """ """

        foo = Foo()
        self.assertTrue(self._callFUT(foo))

    def test_instance_defaultargs_firstname_not_request(self):
        class Foo:
            def __call__(self, context, request=None):
                """ """

        foo = Foo()
        self.assertFalse(self._callFUT(foo))

    def test_instance_defaultargs_firstname_request(self):
        class Foo:
            def __call__(self, request, foo=1, bar=2):
                """ """

        foo = Foo()
        self.assertTrue(self._callFUT(foo, argname='request'), True)

    def test_instance_nocall(self):
        class Foo:
            pass

        foo = Foo()
        self.assertFalse(self._callFUT(foo))

    def test_method_onearg_named_request(self):
        class Foo:
            def method(self, request):
                """ """

        foo = Foo()
        self.assertTrue(self._callFUT(foo.method))

    def test_function_annotations(self):
        def foo(bar):
            """ """

        # avoid SyntaxErrors in python2, this if effectively nop
        getattr(foo, '__annotations__', {}).update({'bar': 'baz'})
        self.assertTrue(self._callFUT(foo))


class TestSimpleSerializer(unittest.TestCase):
    def _makeOne(self):
        from pyramid.util import SimpleSerializer

        return SimpleSerializer()

    def test_loads(self):
        inst = self._makeOne()
        self.assertEqual(inst.loads(b'abc'), text_('abc'))

    def test_dumps(self):
        inst = self._makeOne()
        self.assertEqual(inst.dumps('abc'), bytes_('abc'))


class TestUnboundMethods(unittest.TestCase):
    class Dummy:
        def run(self):  # pragma: no cover
            return 'OK'

    def _callFUT(self, val):
        from pyramid.util import is_unbound_method

        return is_unbound_method(val)

    def test_bound_method(self):
        self.assertFalse(self._callFUT(self.Dummy().run))

    def test_unbound_method(self):
        self.assertTrue(self._callFUT(self.Dummy.run))

    def test_normal_func_unbound(self):
        def func():  # pragma: no cover
            return 'OK'

        self.assertFalse(self._callFUT(func))


class TestReraise(unittest.TestCase):
    def _callFUT(self, *args):
        from pyramid.util import reraise

        return reraise(*args)

    def test_it(self):
        # tests cribbed from six.py
        def get_next(tb):
            return tb.tb_next.tb_next.tb_next

        e = Exception('blah')
        try:
            raise e
        except Exception:
            tp, val, tb = sys.exc_info()

        try:
            self._callFUT(tp, val, tb)
        except Exception:
            tp2, val2, tb2 = sys.exc_info()
        self.assertIs(tp2, Exception)
        self.assertIs(val2, e)
        self.assertIs(get_next(tb2), tb)

        try:
            self._callFUT(tp, val)
        except Exception:
            tp2, val2, tb2 = sys.exc_info()
        self.assertIs(tp2, Exception)
        self.assertIs(val2, e)
        self.assertIsNot(get_next(tb2), tb)

        try:
            self._callFUT(tp, val, tb2)
        except Exception:
            tp2, val2, tb3 = sys.exc_info()
        self.assertIs(tp2, Exception)
        self.assertIs(val2, e)
        self.assertIs(get_next(tb3), tb2)

        try:
            self._callFUT(tp, None, tb)
        except Exception:
            tp2, val2, tb2 = sys.exc_info()
        self.assertIs(tp2, Exception)
        self.assertIsNot(val2, val)
        self.assertIsInstance(val2, Exception)
        self.assertIs(get_next(tb2), tb)
