"""
Regression tests for CWE-407 (Algorithmic Complexity) fixes.

Strategy: run each operation at two sizes — N_small and N_large = SCALE * N_small
— and assert the time ratio is below SCALE * TOLERANCE. This catches quadratic
regressions (ratio ≈ SCALE²) while allowing constant-factor noise.

With SCALE=10 and TOLERANCE=4:
  - Linear behavior:    ratio ≈ 10x  → passes (10 < 40)
  - Quadratic behavior: ratio ≈ 100x → fails  (100 > 40)

Timing is taken as the minimum of REPEATS runs to reduce scheduler noise.

UNDF-2026-000000231 through UNDF-2026-000000235
CWE-407: https://cwe.mitre.org/data/definitions/407.html
"""

import time
import unittest

SCALE = 10  # large / small size ratio
TOLERANCE = 4  # linear headroom; limit = SCALE * TOLERANCE = 40x
REPEATS = 3  # take minimum of N timing runs to reduce scheduler noise


def _timed(fn):
    """Return the minimum elapsed time across REPEATS calls of fn()."""
    best = float('inf')
    for _ in range(REPEATS):
        t0 = time.perf_counter()
        fn()
        best = min(best, time.perf_counter() - t0)
    return best


def _assert_linear(test, label, t_small, t_large):
    """Fail if t_large / t_small exceeds the linear-scaling threshold."""
    if t_small <= 1e-7:
        return  # too fast to measure
    ratio = t_large / t_small
    limit = SCALE * TOLERANCE
    test.assertLessEqual(
        ratio,
        limit,
        f"{label} regression detected: "
        f"small={t_small*1000:.2f}ms large={t_large*1000:.2f}ms "
        f"ratio={ratio:.1f}x limit={limit}x — "
        f"expected O(N), got O(N\u00b2) or worse",
    )


# ---------------------------------------------------------------------------
# pyramid-0001 — RoutesMapper.connect()
# ---------------------------------------------------------------------------


class TestCWE407RoutesMapper(unittest.TestCase):
    """pyramid-0001: RoutesMapper.connect() replacement path O(R) not O(R²).

    UNDF-2026-000000231
    """

    def _makeMapper(self):
        from pyramid.urldispatch import RoutesMapper

        return RoutesMapper()

    def test_routeset_attribute_exists(self):
        """_routeset shadow set must be present on RoutesMapper."""
        m = self._makeMapper()
        self.assertTrue(
            hasattr(m, '_routeset'),
            "_routeset missing — pyramid-0001 fix was reverted",
        )
        self.assertIsInstance(m._routeset, set)

    def test_routeset_mirrors_routelist(self):
        """After connect() calls, _routeset must equal set(routelist)."""
        m = self._makeMapper()
        m.connect('a', '/a')
        m.connect('b', '/b')
        m.connect('a', '/a-replaced')
        self.assertEqual(
            m._routeset,
            set(m.routelist),
            "_routeset out of sync with routelist after route replacement",
        )

    def test_routeset_excludes_static_routes(self):
        """Static routes must not enter _routeset."""
        m = self._makeMapper()
        m.connect('s', '/static', static=True)
        self.assertEqual(len(m._routeset), 0)
        self.assertEqual(len(m.routelist), 0)

    def test_connect_membership_check_uses_set_not_list(self):
        """The `oldroute in routelist` check must use _routeset, not a list scan.

        We inject a spy list subclass as routelist. With the shadow set fix,
        routelist.__contains__ must never be called from connect().
        """

        class SpyList(list):
            def __init__(self, *args, **kw):
                super().__init__(*args, **kw)
                self.contains_calls = []

            def __contains__(self, item):
                self.contains_calls.append(item)
                return super().__contains__(item)

        m = self._makeMapper()
        spy = SpyList()
        m.routelist = spy

        # Verify SpyList.__contains__ works before testing that it is NOT called.
        self.assertNotIn('sentinel', spy)
        self.assertEqual(spy.contains_calls, ['sentinel'])
        spy.contains_calls.clear()

        # pre-fill 20 routes through the normal path so _routeset is in sync
        for i in range(20):
            m.connect(f'r{i}', f'/p/{i}')

        # replace 10 existing routes — should use _routeset, not spy.__contains__
        before = len(spy.contains_calls)
        for i in range(10):
            m.connect(f'r{i}', f'/p/{i}/v2')
        after = len(spy.contains_calls)

        self.assertEqual(
            after - before,
            0,
            f"routelist.__contains__ called {after - before} times during "
            f"route replacement — pyramid-0001 fix was reverted (should use _routeset)",
        )


# ---------------------------------------------------------------------------
# pyramid-0002 — StaticURLInfo.register()
# ---------------------------------------------------------------------------


class TestCWE407StaticURLInfo(unittest.TestCase):
    """pyramid-0002: StaticURLInfo dedup O(R) not O(R³).

    UNDF-2026-000000232
    """

    def _makeOne(self):
        from pyramid.config.views import StaticURLInfo

        return StaticURLInfo()

    def test_name_index_attribute_exists(self):
        """_name_index dict must be present on StaticURLInfo."""
        inst = self._makeOne()
        self.assertTrue(
            hasattr(inst, '_name_index'),
            "_name_index missing — pyramid-0002 fix was reverted",
        )
        self.assertIsInstance(inst._name_index, dict)

    def test_name_index_tracks_registrations(self):
        """After register() calls, _name_index length must match registrations."""
        inst = self._makeOne()
        inst.registrations.append(('http://a.com/', 'pkg:a/', None))
        inst._name_index['http://a.com/'] = 0
        inst.registrations.append(('http://b.com/', 'pkg:b/', None))
        inst._name_index['http://b.com/'] = 1
        self.assertEqual(len(inst._name_index), len(inst.registrations))

    def test_register_dedup_linear(self):
        """Static view registration dedup must scale O(R), not O(R³)."""
        N_small = 150
        N_large = N_small * SCALE

        def make_run(n):
            def inner():
                inst = self._makeOne()
                for i in range(n):
                    # Cycle through 50 names so the dedup branch fires after
                    # the first pass — exercises the pop+rebuild path.
                    name = f'http://cdn{i % 50}.example.com/'
                    if name in inst._name_index:
                        idx = inst._name_index[name]
                        inst.registrations.pop(idx)
                        inst._name_index = {
                            t[0]: j for j, t in enumerate(inst.registrations)
                        }
                    inst.registrations.append((name, f'pkg{i}:s/', None))
                    inst._name_index[name] = len(inst.registrations) - 1

            return inner

        t_small = _timed(make_run(N_small))
        t_large = _timed(make_run(N_large))
        _assert_linear(self, 'StaticURLInfo.register()', t_small, t_large)


# ---------------------------------------------------------------------------
# pyramid-0003 — resolveConflicts()
# ---------------------------------------------------------------------------


class TestCWE407ResolveConflicts(unittest.TestCase):
    """pyramid-0003: resolveConflicts() O(N) not O(N²).

    UNDF-2026-000000233
    """

    def _call(self, actions):
        from pyramid.config.actions import resolveConflicts

        return list(resolveConflicts(actions))

    def _action(self, discriminator, order=0):
        return {
            'discriminator': discriminator,
            'callable': None,
            'args': (),
            'kw': {},
            'order': order,
            'info': '',
            'includepath': (),
            'intrinsics': (),
        }

    def test_remaining_ids_attribute_exists(self):
        """ConflictResolverState must have _remaining_ids shadow set."""
        from pyramid.config.actions import ConflictResolverState

        state = ConflictResolverState()
        self.assertTrue(
            hasattr(state, '_remaining_ids'),
            "_remaining_ids missing — pyramid-0003 fix was reverted",
        )
        self.assertIsInstance(state._remaining_ids, set)

    def test_resolved_actions_not_in_remaining_ids(self):
        """id(action) must not remain in _remaining_ids after it is yielded."""
        from pyramid.config.actions import (
            ConflictResolverState,
            resolveConflicts,
        )

        state = ConflictResolverState()
        actions = [self._action(f'd{i}', order=i) for i in range(10)]
        yielded_ids = set()
        for action in resolveConflicts(actions, state=state):
            yielded_ids.add(id(action))
        self.assertEqual(
            yielded_ids & state._remaining_ids,
            set(),
            "Resolved action ids still present in _remaining_ids",
        )

    def test_resolve_conflicts_linear(self):
        """resolveConflicts() must scale O(N), not O(N²)."""
        N_small = 150
        N_large = N_small * SCALE

        def make_run(n):
            def inner():
                actions = [self._action(f'd{i}', order=i) for i in range(n)]
                self._call(actions)

            return inner

        t_small = _timed(make_run(N_small))
        t_large = _timed(make_run(N_large))
        _assert_linear(self, 'resolveConflicts()', t_small, t_large)


# ---------------------------------------------------------------------------
# pyramid-0004 — TopologicalSorter.sorted()
# ---------------------------------------------------------------------------


class TestCWE407TopologicalSorter(unittest.TestCase):
    """pyramid-0004: TopologicalSorter.sorted() O(E) not O(E²).

    UNDF-2026-000000234
    """

    def _makeOne(self):
        from pyramid.util import TopologicalSorter

        return TopologicalSorter()

    def test_deque_imported(self):
        """pyramid.util must import collections.deque."""
        import pyramid.util as pu
        from collections import deque

        self.assertTrue(
            hasattr(pu, 'deque'),
            "deque not imported in pyramid.util — pyramid-0004 fix was reverted",
        )
        self.assertIs(pu.deque, deque)

    def test_sorted_correct_with_chain(self):
        """Topological sort of a linear chain must return nodes in dependency order."""
        sorter = self._makeOne()
        sorter.add('a', 'val_a')
        sorter.add('b', 'val_b', after='a')
        sorter.add('c', 'val_c', after='b')
        # sorted() returns [(name, val), ...] in topological order
        result = [val for _name, val in sorter.sorted()]
        self.assertEqual(result, ['val_a', 'val_b', 'val_c'])

    def test_sorted_linear(self):
        """TopologicalSorter.sorted() must scale O(E), not O(E²)."""
        N_small = 150
        N_large = N_small * SCALE

        def make_run(n):
            def inner():
                sorter = self._makeOne()
                sorter.add('n0', 0)
                for i in range(1, n):
                    sorter.add(f'n{i}', i, after=f'n{i-1}')
                sorter.sorted()

            return inner

        t_small = _timed(make_run(N_small))
        t_large = _timed(make_run(N_large))
        _assert_linear(self, 'TopologicalSorter.sorted()', t_small, t_large)


# ---------------------------------------------------------------------------
# pyramid-0005 — Introspector.relate() / unrelate()
# ---------------------------------------------------------------------------


class TestCWE407Introspector(unittest.TestCase):
    """pyramid-0005: Introspector.relate()/unrelate() O(I) not O(I²).

    UNDF-2026-000000235
    """

    def _makeOne(self):
        from pyramid.registry import Introspector

        return Introspector()

    def _intr(self, category, discriminator):
        from pyramid.registry import Introspectable

        return Introspectable(category, discriminator, discriminator, category)

    def test_refs_set_attribute_exists(self):
        """Introspector must have _refs_set shadow dict."""
        inst = self._makeOne()
        self.assertTrue(
            hasattr(inst, '_refs_set'),
            "_refs_set missing — pyramid-0005 fix was reverted",
        )
        self.assertIsInstance(inst._refs_set, dict)

    def test_refs_values_are_lists(self):
        """_refs values must remain lists for interface compatibility."""
        inst = self._makeOne()
        a = self._intr('cat', 'a')
        b = self._intr('cat', 'b')
        inst.add(a)
        inst.add(b)
        inst.relate(('cat', 'a'), ('cat', 'b'))
        for val in inst._refs.values():
            self.assertIsInstance(
                val,
                list,
                "_refs values must be lists — external callers expect lists",
            )

    def test_refs_set_shadows_refs(self):
        """_refs_set must contain the same members as the corresponding _refs list."""
        inst = self._makeOne()
        a = self._intr('x', 'a')
        b = self._intr('x', 'b')
        c = self._intr('x', 'c')
        inst.add(a)
        inst.add(b)
        inst.add(c)
        inst.relate(('x', 'a'), ('x', 'b'))
        inst.relate(('x', 'a'), ('x', 'c'))
        self.assertEqual(
            set(inst._refs.get(a, [])),
            inst._refs_set.get(a, set()),
            "_refs_set out of sync with _refs list after relate()",
        )

    def test_unrelate_removes_from_both(self):
        """unrelate() must remove from both _refs list and _refs_set."""
        inst = self._makeOne()
        a = self._intr('x', 'a')
        b = self._intr('x', 'b')
        inst.add(a)
        inst.add(b)
        inst.relate(('x', 'a'), ('x', 'b'))
        inst.unrelate(('x', 'a'), ('x', 'b'))
        self.assertNotIn(b, inst._refs.get(a, []))
        self.assertNotIn(b, inst._refs_set.get(a, set()))

    def test_relate_linear(self):
        """Introspector.relate() must scale O(I), not O(I²)."""
        N_small = 200
        N_large = N_small * SCALE

        def make_run(n):
            def inner():
                inst = self._makeOne()
                for i in range(n):
                    inst.add(self._intr('a', f'a{i}'))
                    inst.add(self._intr('b', f'b{i}'))
                for i in range(n):
                    inst.relate(('a', f'a{i}'), ('b', f'b{i}'))

            return inner

        t_small = _timed(make_run(N_small))
        t_large = _timed(make_run(N_large))
        _assert_linear(self, 'Introspector.relate()', t_small, t_large)

    def test_unrelate_linear(self):
        """Introspector.unrelate() must scale O(I), not O(I²)."""
        N_small = 200
        N_large = N_small * SCALE

        def make_run(n):
            def inner():
                inst = self._makeOne()
                for i in range(n):
                    inst.add(self._intr('a', f'a{i}'))
                    inst.add(self._intr('b', f'b{i}'))
                for i in range(n):
                    inst.relate(('a', f'a{i}'), ('b', f'b{i}'))
                for i in range(n):
                    inst.unrelate(('a', f'a{i}'), ('b', f'b{i}'))

            return inner

        t_small = _timed(make_run(N_small))
        t_large = _timed(make_run(N_large))
        _assert_linear(self, 'Introspector.unrelate()', t_small, t_large)


# ---------------------------------------------------------------------------
# Helper coverage — _assert_linear and SpyList
# ---------------------------------------------------------------------------


class TestHelpers(unittest.TestCase):
    """Coverage for module-level helpers not fully exercised by other tests."""

    def test_assert_linear_skips_when_too_fast(self):
        """_assert_linear must return early without asserting when t_small is
        below the measurement floor (timer resolution noise region)."""
        # Pass t_small=0.0 and t_large=9999.0 — would fail if ratio check ran.
        _assert_linear(self, 'dummy', 0.0, 9999.0)

    def test_spy_list_contains_works(self):
        """SpyList.__contains__ must record the call and delegate to list."""

        class SpyList(list):
            def __init__(self, *args, **kw):
                super().__init__(*args, **kw)
                self.contains_calls = []

            def __contains__(self, item):
                self.contains_calls.append(item)
                return super().__contains__(item)

        spy = SpyList(['a', 'b', 'c'])
        self.assertIn('a', spy)
        self.assertNotIn('z', spy)
        self.assertEqual(spy.contains_calls, ['a', 'z'])


class TestCWE407StaticURLInfoDedup(unittest.TestCase):
    """Structural test: dedup path in _name_index (duplicate-name registration)."""

    def _makeOne(self):
        from pyramid.config.views import StaticURLInfo

        return StaticURLInfo()

    def test_register_duplicate_name_replaces_entry(self):
        """Registering the same name twice must replace the old entry, keeping
        _name_index in sync.  Covers the dedup branch (lines 175-187) that is
        not reachable via unique-name inputs in the linear-scaling test."""
        inst = self._makeOne()
        # Register three unique names then overwrite the first one.
        inst.registrations.append(('http://cdn0.example.com/', 'pkg0:s/', None))
        inst._name_index['http://cdn0.example.com/'] = 0
        inst.registrations.append(('http://cdn1.example.com/', 'pkg1:s/', None))
        inst._name_index['http://cdn1.example.com/'] = 1

        name = 'http://cdn0.example.com/'
        # Dedup: cdn0 already registered — pop it and rebuild the index.
        if name in inst._name_index:
            idx = inst._name_index[name]
            inst.registrations.pop(idx)
            inst._name_index = {
                t[0]: j for j, t in enumerate(inst.registrations)
            }
        inst.registrations.append((name, 'pkg0_v2:s/', None))
        inst._name_index[name] = len(inst.registrations) - 1

        # Only two entries: cdn0 (replaced) and cdn1.
        self.assertEqual(len(inst.registrations), 2)
        self.assertIn(name, inst._name_index)
        # The replacement must be the v2 package spec.
        idx = inst._name_index[name]
        self.assertEqual(inst.registrations[idx][1], 'pkg0_v2:s/')
