from collections import OrderedDict
import unittest


class TestBWCompat(unittest.TestCase):
    def test_bwcompat_notfound(self):
        from pyramid.exceptions import NotFound as one
        from pyramid.httpexceptions import HTTPNotFound as two

        self.assertTrue(one is two)

    def test_bwcompat_forbidden(self):
        from pyramid.exceptions import Forbidden as one
        from pyramid.httpexceptions import HTTPForbidden as two

        self.assertTrue(one is two)


class TestBadCSRFOrigin(unittest.TestCase):
    def test_response_equivalence(self):
        from pyramid.exceptions import BadCSRFOrigin
        from pyramid.httpexceptions import HTTPBadRequest

        self.assertTrue(isinstance(BadCSRFOrigin(), HTTPBadRequest))
        self.assertEqual(BadCSRFOrigin().status, HTTPBadRequest().status)


class TestBadCSRFToken(unittest.TestCase):
    def test_response_equivalence(self):
        from pyramid.exceptions import BadCSRFToken
        from pyramid.httpexceptions import HTTPBadRequest

        self.assertTrue(isinstance(BadCSRFToken(), HTTPBadRequest))
        self.assertEqual(BadCSRFToken().status, HTTPBadRequest().status)


class TestNotFound(unittest.TestCase):
    def _makeOne(self, message):
        from pyramid.exceptions import NotFound

        return NotFound(message)

    def test_it(self):
        from pyramid.interfaces import IExceptionResponse

        e = self._makeOne('notfound')
        self.assertTrue(IExceptionResponse.providedBy(e))
        self.assertEqual(e.status, '404 Not Found')
        self.assertEqual(e.message, 'notfound')

    def test_response_equivalence(self):
        from pyramid.exceptions import NotFound
        from pyramid.httpexceptions import HTTPNotFound

        self.assertTrue(NotFound is HTTPNotFound)


class TestForbidden(unittest.TestCase):
    def _makeOne(self, message):
        from pyramid.exceptions import Forbidden

        return Forbidden(message)

    def test_it(self):
        from pyramid.interfaces import IExceptionResponse

        e = self._makeOne('forbidden')
        self.assertTrue(IExceptionResponse.providedBy(e))
        self.assertEqual(e.status, '403 Forbidden')
        self.assertEqual(e.message, 'forbidden')

    def test_response_equivalence(self):
        from pyramid.exceptions import Forbidden
        from pyramid.httpexceptions import HTTPForbidden

        self.assertTrue(Forbidden is HTTPForbidden)


class TestPredicateMismatch(unittest.TestCase):
    def _makeOne(self, *args, **kwargs):
        from pyramid.exceptions import PredicateMismatch

        return PredicateMismatch(*args, **kwargs)

    def test_predicate_default_none(self):
        exc = self._makeOne('mismatch')
        self.assertIsNone(exc.predicate)

    def test_predicate_stored(self):
        sentinel = object()
        exc = self._makeOne('mismatch', predicate=sentinel)
        self.assertIs(exc.predicate, sentinel)

    def test_mismatches_default_none(self):
        exc = self._makeOne('mismatch')
        self.assertIsNone(exc.mismatches)

    def test_mismatches_stored(self):
        mismatches = [('view1', 'pred1'), ('view2', 'pred2')]
        exc = self._makeOne('mismatch', mismatches=mismatches)
        self.assertIs(exc.mismatches, mismatches)

    def test_raise_if_specialized_empty_returns(self):
        from pyramid.exceptions import PredicateMismatch

        result = PredicateMismatch.raise_if_specialized([])
        self.assertIsNone(result)

    def test_raise_if_specialized_none_predicate_returns(self):
        from pyramid.exceptions import PredicateMismatch

        result = PredicateMismatch.raise_if_specialized([('view1', None)])
        self.assertIsNone(result)

    def test_raise_if_specialized_all_method_raises_405(self):
        from pyramid.exceptions import PredicateMismatch
        from pyramid.httpexceptions import HTTPMethodNotAllowed
        from pyramid.predicates import RequestMethodPredicate

        pred = RequestMethodPredicate(('GET',), None)
        with self.assertRaises(HTTPMethodNotAllowed) as cm:
            PredicateMismatch.raise_if_specialized([('view1', pred)])
        self.assertIn('GET', cm.exception.headers['Allow'])

    def test_raise_if_specialized_all_accept_raises_406(self):
        from pyramid.exceptions import PredicateMismatch
        from pyramid.httpexceptions import HTTPNotAcceptable
        from pyramid.predicates import AcceptPredicate

        pred = AcceptPredicate('text/html', None)
        with self.assertRaises(HTTPNotAcceptable):
            PredicateMismatch.raise_if_specialized([('view1', pred)])

    def test_raise_if_specialized_mixed_returns(self):
        from pyramid.exceptions import PredicateMismatch
        from pyramid.predicates import AcceptPredicate, RequestMethodPredicate

        method_pred = RequestMethodPredicate(('GET',), None)
        accept_pred = AcceptPredicate('text/html', None)
        result = PredicateMismatch.raise_if_specialized(
            [('view1', method_pred), ('view2', accept_pred)]
        )
        self.assertIsNone(result)

    def test_raise_if_specialized_with_all_views(self):
        from pyramid.exceptions import PredicateMismatch
        from pyramid.httpexceptions import HTTPMethodNotAllowed
        from pyramid.predicates import RequestMethodPredicate

        get_pred = RequestMethodPredicate(('GET',), None)
        post_pred = RequestMethodPredicate(('POST',), None)

        class DummyView:
            __predicates__ = (post_pred,)

        mismatches = [('view1', get_pred)]
        all_views = [(0, DummyView, 'phash')]
        with self.assertRaises(HTTPMethodNotAllowed) as cm:
            PredicateMismatch.raise_if_specialized(mismatches, all_views)
        self.assertIn('POST', cm.exception.headers['Allow'])


class TestConfigurationConflictError(unittest.TestCase):
    def _makeOne(self, conflicts):
        from pyramid.exceptions import ConfigurationConflictError

        return ConfigurationConflictError(conflicts)

    def test_str(self):
        conflicts = OrderedDict()
        conflicts['a'] = ('1', '2', '3')
        conflicts['b'] = ('4', '5', '6')
        exc = self._makeOne(conflicts)
        self.assertEqual(
            str(exc),
            """\
Conflicting configuration actions
  For: a
    1
    2
    3
  For: b
    4
    5
    6""",
        )

    def test_non_sortable_discriminators_in_str(self):
        conflicts = OrderedDict()
        conflicts['a'] = ('1', '2', '3')
        conflicts[None] = ('4', '5', '6')
        exc = self._makeOne(conflicts)
        self.assertEqual(
            str(exc),
            """\
Conflicting configuration actions
  For: a
    1
    2
    3
  For: None
    4
    5
    6""",
        )


class TestConfigurationExecutionError(unittest.TestCase):
    def _makeOne(self, etype, evalue, info):
        from pyramid.exceptions import ConfigurationExecutionError

        return ConfigurationExecutionError(etype, evalue, info)

    def test_str(self):
        exc = self._makeOne('etype', 'evalue', 'info')
        self.assertEqual(str(exc), 'etype: evalue\n  in:\n  info')


class TestCyclicDependencyError(unittest.TestCase):
    def _makeOne(self, cycles):
        from pyramid.exceptions import CyclicDependencyError

        return CyclicDependencyError(cycles)

    def test___str__(self):
        exc = self._makeOne({'a': ['c', 'd'], 'c': ['a']})
        result = str(exc)
        self.assertTrue("'a' sorts before ['c', 'd']" in result)
        self.assertTrue("'c' sorts before ['a']" in result)
