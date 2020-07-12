import unittest

from pyramid.exceptions import (
    ConfigurationConflictError,
    ConfigurationExecutionError,
)
from pyramid.interfaces import IRequest


class ActionConfiguratorMixinTests(unittest.TestCase):
    def _makeOne(self, *arg, **kw):
        from pyramid.config import Configurator

        config = Configurator(*arg, **kw)
        return config

    def _getViewCallable(
        self,
        config,
        ctx_iface=None,
        request_iface=None,
        name='',
        exception_view=False,
    ):
        from zope.interface import Interface

        from pyramid.interfaces import (
            IExceptionViewClassifier,
            IView,
            IViewClassifier,
        )

        if exception_view:  # pragma: no cover
            classifier = IExceptionViewClassifier
        else:
            classifier = IViewClassifier
        if ctx_iface is None:
            ctx_iface = Interface
        if request_iface is None:
            request_iface = IRequest
        return config.registry.adapters.lookup(
            (classifier, request_iface, ctx_iface),
            IView,
            name=name,
            default=None,
        )

    def test_action_branching_kw_is_None(self):
        config = self._makeOne(autocommit=True)
        self.assertEqual(config.action('discrim'), None)

    def test_action_branching_kw_is_not_None(self):
        config = self._makeOne(autocommit=True)
        self.assertEqual(config.action('discrim', kw={'a': 1}), None)

    def test_action_autocommit_with_introspectables(self):
        from pyramid.config.actions import ActionInfo

        config = self._makeOne(autocommit=True)
        intr = DummyIntrospectable()
        config.action('discrim', introspectables=(intr,))
        self.assertEqual(len(intr.registered), 1)
        self.assertEqual(intr.registered[0][0], config.introspector)
        self.assertEqual(intr.registered[0][1].__class__, ActionInfo)

    def test_action_autocommit_with_introspectables_introspection_off(self):
        config = self._makeOne(autocommit=True)
        config.introspection = False
        intr = DummyIntrospectable()
        config.action('discrim', introspectables=(intr,))
        self.assertEqual(len(intr.registered), 0)

    def test_action_branching_nonautocommit_with_config_info(self):
        config = self._makeOne(autocommit=False)
        config.info = 'abc'
        state = DummyActionState()
        state.autocommit = False
        config.action_state = state
        config.action('discrim', kw={'a': 1})
        self.assertEqual(
            state.actions,
            [
                (
                    (),
                    {
                        'args': (),
                        'callable': None,
                        'discriminator': 'discrim',
                        'includepath': (),
                        'info': 'abc',
                        'introspectables': (),
                        'kw': {'a': 1},
                        'order': 0,
                    },
                )
            ],
        )

    def test_action_branching_nonautocommit_without_config_info(self):
        config = self._makeOne(autocommit=False)
        config.info = ''
        config._ainfo = ['z']
        state = DummyActionState()
        config.action_state = state
        state.autocommit = False
        config.action('discrim', kw={'a': 1})
        self.assertEqual(
            state.actions,
            [
                (
                    (),
                    {
                        'args': (),
                        'callable': None,
                        'discriminator': 'discrim',
                        'includepath': (),
                        'info': 'z',
                        'introspectables': (),
                        'kw': {'a': 1},
                        'order': 0,
                    },
                )
            ],
        )

    def test_action_branching_nonautocommit_with_introspectables(self):
        config = self._makeOne(autocommit=False)
        config.info = ''
        config._ainfo = []
        state = DummyActionState()
        config.action_state = state
        state.autocommit = False
        intr = DummyIntrospectable()
        config.action('discrim', introspectables=(intr,))
        self.assertEqual(state.actions[0][1]['introspectables'], (intr,))

    def test_action_nonautocommit_with_introspectables_introspection_off(self):
        config = self._makeOne(autocommit=False)
        config.info = ''
        config._ainfo = []
        config.introspection = False
        state = DummyActionState()
        config.action_state = state
        state.autocommit = False
        intr = DummyIntrospectable()
        config.action('discrim', introspectables=(intr,))
        self.assertEqual(state.actions[0][1]['introspectables'], ())

    def test_commit_conflict_simple(self):
        config = self._makeOne()

        def view1(request):  # pragma: no cover
            pass

        def view2(request):  # pragma: no cover
            pass

        config.add_view(view1)
        config.add_view(view2)
        self.assertRaises(ConfigurationConflictError, config.commit)

    def test_commit_conflict_resolved_with_include(self):
        config = self._makeOne()

        def view1(request):  # pragma: no cover
            pass

        def view2(request):  # pragma: no cover
            pass

        def includeme(config):
            config.add_view(view2)

        config.add_view(view1)
        config.include(includeme)
        config.commit()
        registeredview = self._getViewCallable(config)
        self.assertEqual(registeredview.__name__, 'view1')

    def test_commit_conflict_with_two_includes(self):
        config = self._makeOne()

        def view1(request):  # pragma: no cover
            pass

        def view2(request):  # pragma: no cover
            pass

        def includeme1(config):
            config.add_view(view1)

        def includeme2(config):
            config.add_view(view2)

        config.include(includeme1)
        config.include(includeme2)
        try:
            config.commit()
        except ConfigurationConflictError as why:
            c1, c2 = _conflictFunctions(why)
            self.assertEqual(c1, 'includeme1')
            self.assertEqual(c2, 'includeme2')
        else:  # pragma: no cover
            raise AssertionError

    def test_commit_conflict_resolved_with_two_includes_and_local(self):
        config = self._makeOne()

        def view1(request):  # pragma: no cover
            pass

        def view2(request):  # pragma: no cover
            pass

        def view3(request):  # pragma: no cover
            pass

        def includeme1(config):
            config.add_view(view1)

        def includeme2(config):
            config.add_view(view2)

        config.include(includeme1)
        config.include(includeme2)
        config.add_view(view3)
        config.commit()
        registeredview = self._getViewCallable(config)
        self.assertEqual(registeredview.__name__, 'view3')

    def test_autocommit_no_conflicts(self):
        from pyramid.renderers import null_renderer

        config = self._makeOne(autocommit=True)

        def view1(request):  # pragma: no cover
            pass

        def view2(request):  # pragma: no cover
            pass

        def view3(request):  # pragma: no cover
            pass

        config.add_view(view1, renderer=null_renderer)
        config.add_view(view2, renderer=null_renderer)
        config.add_view(view3, renderer=null_renderer)
        config.commit()
        registeredview = self._getViewCallable(config)
        self.assertEqual(registeredview.__name__, 'view3')

    def test_conflict_set_notfound_view(self):
        config = self._makeOne()

        def view1(request):  # pragma: no cover
            pass

        def view2(request):  # pragma: no cover
            pass

        config.set_notfound_view(view1)
        config.set_notfound_view(view2)
        try:
            config.commit()
        except ConfigurationConflictError as why:
            c1, c2 = _conflictFunctions(why)
            self.assertEqual(c1, 'test_conflict_set_notfound_view')
            self.assertEqual(c2, 'test_conflict_set_notfound_view')
        else:  # pragma: no cover
            raise AssertionError

    def test_conflict_set_forbidden_view(self):
        config = self._makeOne()

        def view1(request):  # pragma: no cover
            pass

        def view2(request):  # pragma: no cover
            pass

        config.set_forbidden_view(view1)
        config.set_forbidden_view(view2)
        try:
            config.commit()
        except ConfigurationConflictError as why:
            c1, c2 = _conflictFunctions(why)
            self.assertEqual(c1, 'test_conflict_set_forbidden_view')
            self.assertEqual(c2, 'test_conflict_set_forbidden_view')
        else:  # pragma: no cover
            raise AssertionError


class TestActionState(unittest.TestCase):
    def _makeOne(self):
        from pyramid.config.actions import ActionState

        return ActionState()

    def test_it(self):
        c = self._makeOne()
        self.assertEqual(c.actions, [])

    def test_action_simple(self):
        from . import dummyfactory as f

        c = self._makeOne()
        c.actions = []
        c.action(1, f, (1,), {'x': 1})
        self.assertEqual(
            c.actions,
            [
                {
                    'args': (1,),
                    'callable': f,
                    'discriminator': 1,
                    'includepath': (),
                    'info': None,
                    'introspectables': (),
                    'kw': {'x': 1},
                    'order': 0,
                }
            ],
        )
        c.action(None)
        self.assertEqual(
            c.actions,
            [
                {
                    'args': (1,),
                    'callable': f,
                    'discriminator': 1,
                    'includepath': (),
                    'info': None,
                    'introspectables': (),
                    'kw': {'x': 1},
                    'order': 0,
                },
                {
                    'args': (),
                    'callable': None,
                    'discriminator': None,
                    'includepath': (),
                    'info': None,
                    'introspectables': (),
                    'kw': {},
                    'order': 0,
                },
            ],
        )

    def test_action_with_includepath(self):
        c = self._makeOne()
        c.actions = []
        c.action(None, includepath=('abc',))
        self.assertEqual(
            c.actions,
            [
                {
                    'args': (),
                    'callable': None,
                    'discriminator': None,
                    'includepath': ('abc',),
                    'info': None,
                    'introspectables': (),
                    'kw': {},
                    'order': 0,
                }
            ],
        )

    def test_action_with_info(self):
        c = self._makeOne()
        c.action(None, info='abc')
        self.assertEqual(
            c.actions,
            [
                {
                    'args': (),
                    'callable': None,
                    'discriminator': None,
                    'includepath': (),
                    'info': 'abc',
                    'introspectables': (),
                    'kw': {},
                    'order': 0,
                }
            ],
        )

    def test_action_with_includepath_and_info(self):
        c = self._makeOne()
        c.action(None, includepath=('spec',), info='bleh')
        self.assertEqual(
            c.actions,
            [
                {
                    'args': (),
                    'callable': None,
                    'discriminator': None,
                    'includepath': ('spec',),
                    'info': 'bleh',
                    'introspectables': (),
                    'kw': {},
                    'order': 0,
                }
            ],
        )

    def test_action_with_order(self):
        c = self._makeOne()
        c.actions = []
        c.action(None, order=99999)
        self.assertEqual(
            c.actions,
            [
                {
                    'args': (),
                    'callable': None,
                    'discriminator': None,
                    'includepath': (),
                    'info': None,
                    'introspectables': (),
                    'kw': {},
                    'order': 99999,
                }
            ],
        )

    def test_action_with_introspectables(self):
        c = self._makeOne()
        c.actions = []
        intr = DummyIntrospectable()
        c.action(None, introspectables=(intr,))
        self.assertEqual(
            c.actions,
            [
                {
                    'args': (),
                    'callable': None,
                    'discriminator': None,
                    'includepath': (),
                    'info': None,
                    'introspectables': (intr,),
                    'kw': {},
                    'order': 0,
                }
            ],
        )

    def test_processSpec(self):
        c = self._makeOne()
        self.assertTrue(c.processSpec('spec'))
        self.assertFalse(c.processSpec('spec'))

    def test_execute_actions_tuples(self):
        output = []

        def f(*a, **k):
            output.append((a, k))

        c = self._makeOne()
        c.actions = [
            (1, f, (1,)),
            (1, f, (11,), {}, ('x',)),
            (2, f, (2,)),
            (None, None),
        ]
        c.execute_actions()
        self.assertEqual(output, [((1,), {}), ((2,), {})])

    def test_execute_actions_dicts(self):
        output = []

        def f(*a, **k):
            output.append((a, k))

        c = self._makeOne()
        c.actions = [
            {
                'discriminator': 1,
                'callable': f,
                'args': (1,),
                'kw': {},
                'order': 0,
                'includepath': (),
                'info': None,
                'introspectables': (),
            },
            {
                'discriminator': 1,
                'callable': f,
                'args': (11,),
                'kw': {},
                'includepath': ('x',),
                'order': 0,
                'info': None,
                'introspectables': (),
            },
            {
                'discriminator': 2,
                'callable': f,
                'args': (2,),
                'kw': {},
                'order': 0,
                'includepath': (),
                'info': None,
                'introspectables': (),
            },
            {
                'discriminator': None,
                'callable': None,
                'args': (),
                'kw': {},
                'order': 0,
                'includepath': (),
                'info': None,
                'introspectables': (),
            },
        ]
        c.execute_actions()
        self.assertEqual(output, [((1,), {}), ((2,), {})])

    def test_execute_actions_with_introspectables(self):
        output = []

        def f(*a, **k):
            output.append((a, k))

        c = self._makeOne()
        intr = DummyIntrospectable()
        c.actions = [
            {
                'discriminator': 1,
                'callable': f,
                'args': (1,),
                'kw': {},
                'order': 0,
                'includepath': (),
                'info': None,
                'introspectables': (intr,),
            }
        ]
        introspector = object()
        c.execute_actions(introspector=introspector)
        self.assertEqual(output, [((1,), {})])
        self.assertEqual(intr.registered, [(introspector, None)])

    def test_execute_actions_with_introspectable_no_callable(self):
        c = self._makeOne()
        intr = DummyIntrospectable()
        c.actions = [
            {
                'discriminator': 1,
                'callable': None,
                'args': (1,),
                'kw': {},
                'order': 0,
                'includepath': (),
                'info': None,
                'introspectables': (intr,),
            }
        ]
        introspector = object()
        c.execute_actions(introspector=introspector)
        self.assertEqual(intr.registered, [(introspector, None)])

    def test_execute_actions_error(self):
        output = []

        def f(*a, **k):
            output.append(('f', a, k))

        def bad():
            raise NotImplementedError

        c = self._makeOne()
        c.actions = [
            (1, f, (1,)),
            (1, f, (11,), {}, ('x',)),
            (2, f, (2,)),
            (3, bad, (), {}, (), 'oops'),
        ]
        self.assertRaises(ConfigurationExecutionError, c.execute_actions)
        self.assertEqual(output, [('f', (1,), {}), ('f', (2,), {})])

    def test_reentrant_action(self):
        output = []
        c = self._makeOne()

        def f(*a, **k):
            output.append(('f', a, k))
            c.actions.append((3, g, (8,), {}))

        def g(*a, **k):
            output.append(('g', a, k))

        c.actions = [(1, f, (1,))]
        c.execute_actions()
        self.assertEqual(output, [('f', (1,), {}), ('g', (8,), {})])

    def test_reentrant_action_with_deferred_discriminator(self):
        # see https://github.com/Pylons/pyramid/issues/2697
        from pyramid.registry import Deferred

        output = []
        c = self._makeOne()

        def f(*a, **k):
            output.append(('f', a, k))
            c.actions.append((4, g, (4,), {}, (), None, 2))

        def g(*a, **k):
            output.append(('g', a, k))

        def h(*a, **k):
            output.append(('h', a, k))

        def discrim():
            self.assertEqual(output, [('f', (1,), {}), ('g', (2,), {})])
            return 3

        d = Deferred(discrim)
        c.actions = [
            (d, h, (3,), {}, (), None, 1),  # order 1
            (1, f, (1,)),  # order 0
            (2, g, (2,)),  # order 0
        ]
        c.execute_actions()
        self.assertEqual(
            output,
            [
                ('f', (1,), {}),
                ('g', (2,), {}),
                ('h', (3,), {}),
                ('g', (4,), {}),
            ],
        )

    def test_reentrant_action_error(self):
        from pyramid.exceptions import ConfigurationError

        c = self._makeOne()

        def f(*a, **k):
            c.actions.append((3, g, (8,), {}, (), None, -1))

        def g(*a, **k):  # pragma: no cover
            pass

        c.actions = [(1, f, (1,))]
        self.assertRaises(ConfigurationError, c.execute_actions)

    def test_reentrant_action_without_clear(self):
        c = self._makeOne()

        def f(*a, **k):
            c.actions.append((3, g, (8,)))

        def g(*a, **k):
            pass

        c.actions = [(1, f, (1,))]
        c.execute_actions(clear=False)
        self.assertEqual(c.actions, [(1, f, (1,)), (3, g, (8,))])

    def test_executing_conflicting_action_across_orders(self):
        from pyramid.exceptions import ConfigurationConflictError

        c = self._makeOne()

        def f(*a, **k):
            pass

        def g(*a, **k):  # pragma: no cover
            pass

        c.actions = [(1, f, (1,), {}, (), None, -1), (1, g, (2,))]
        self.assertRaises(ConfigurationConflictError, c.execute_actions)

    def test_executing_conflicting_action_across_reentrant_orders(self):
        from pyramid.exceptions import ConfigurationConflictError

        c = self._makeOne()

        def f(*a, **k):
            c.actions.append((1, g, (8,)))

        def g(*a, **k):  # pragma: no cover
            pass

        c.actions = [(1, f, (1,), {}, (), None, -1)]
        self.assertRaises(ConfigurationConflictError, c.execute_actions)


class Test_reentrant_action_functional(unittest.TestCase):
    def _makeConfigurator(self, *arg, **kw):
        from pyramid.config import Configurator

        config = Configurator(*arg, **kw)
        return config

    def test_functional(self):
        def add_auto_route(config, name, view):
            def register():
                config.add_view(route_name=name, view=view)
                config.add_route(name, '/' + name)

            config.action(('auto route', name), register, order=-30)

        config = self._makeConfigurator()
        config.add_directive('add_auto_route', add_auto_route)

        def my_view(request):  # pragma: no cover
            return request.response

        config.add_auto_route('foo', my_view)
        config.commit()
        from pyramid.interfaces import IRoutesMapper

        mapper = config.registry.getUtility(IRoutesMapper)
        routes = mapper.get_routes()
        route = routes[0]
        self.assertEqual(len(routes), 1)
        self.assertEqual(route.name, 'foo')
        self.assertEqual(route.path, '/foo')

    def test_deferred_discriminator(self):
        # see https://github.com/Pylons/pyramid/issues/2697
        from pyramid.config import PHASE0_CONFIG

        config = self._makeConfigurator()

        def deriver(view, info):
            return view

        deriver.options = ('foo',)
        config.add_view_deriver(deriver, 'foo_view')
        # add_view uses a deferred discriminator and will fail if executed
        # prior to add_view_deriver executing its action
        config.add_view(lambda r: r.response, name='', foo=1)

        def dummy_action():
            # trigger a re-entrant action
            config.action(None, lambda: None)

        config.action(None, dummy_action, order=PHASE0_CONFIG)
        config.commit()


class Test_resolveConflicts(unittest.TestCase):
    def _callFUT(self, actions):
        from pyramid.config.actions import resolveConflicts

        return resolveConflicts(actions)

    def test_it_success_tuples(self):
        from . import dummyfactory as f

        result = self._callFUT(
            [
                (None, f),
                (1, f, (1,), {}, (), 'first'),
                (1, f, (2,), {}, ('x',), 'second'),
                (1, f, (3,), {}, ('y',), 'third'),
                (4, f, (4,), {}, ('y',), 'should be last', 99999),
                (3, f, (3,), {}, ('y',)),
                (None, f, (5,), {}, ('y',)),
            ]
        )
        result = list(result)
        self.assertEqual(
            result,
            [
                {
                    'info': None,
                    'args': (),
                    'callable': f,
                    'introspectables': (),
                    'kw': {},
                    'discriminator': None,
                    'includepath': (),
                    'order': 0,
                },
                {
                    'info': 'first',
                    'args': (1,),
                    'callable': f,
                    'introspectables': (),
                    'kw': {},
                    'discriminator': 1,
                    'includepath': (),
                    'order': 0,
                },
                {
                    'info': None,
                    'args': (3,),
                    'callable': f,
                    'introspectables': (),
                    'kw': {},
                    'discriminator': 3,
                    'includepath': ('y',),
                    'order': 0,
                },
                {
                    'info': None,
                    'args': (5,),
                    'callable': f,
                    'introspectables': (),
                    'kw': {},
                    'discriminator': None,
                    'includepath': ('y',),
                    'order': 0,
                },
                {
                    'info': 'should be last',
                    'args': (4,),
                    'callable': f,
                    'introspectables': (),
                    'kw': {},
                    'discriminator': 4,
                    'includepath': ('y',),
                    'order': 99999,
                },
            ],
        )

    def test_it_success_dicts(self):
        from . import dummyfactory as f

        result = self._callFUT(
            [
                (None, f),
                (1, f, (1,), {}, (), 'first'),
                (1, f, (2,), {}, ('x',), 'second'),
                (1, f, (3,), {}, ('y',), 'third'),
                (4, f, (4,), {}, ('y',), 'should be last', 99999),
                (3, f, (3,), {}, ('y',)),
                (None, f, (5,), {}, ('y',)),
            ]
        )
        result = list(result)
        self.assertEqual(
            result,
            [
                {
                    'info': None,
                    'args': (),
                    'callable': f,
                    'introspectables': (),
                    'kw': {},
                    'discriminator': None,
                    'includepath': (),
                    'order': 0,
                },
                {
                    'info': 'first',
                    'args': (1,),
                    'callable': f,
                    'introspectables': (),
                    'kw': {},
                    'discriminator': 1,
                    'includepath': (),
                    'order': 0,
                },
                {
                    'info': None,
                    'args': (3,),
                    'callable': f,
                    'introspectables': (),
                    'kw': {},
                    'discriminator': 3,
                    'includepath': ('y',),
                    'order': 0,
                },
                {
                    'info': None,
                    'args': (5,),
                    'callable': f,
                    'introspectables': (),
                    'kw': {},
                    'discriminator': None,
                    'includepath': ('y',),
                    'order': 0,
                },
                {
                    'info': 'should be last',
                    'args': (4,),
                    'callable': f,
                    'introspectables': (),
                    'kw': {},
                    'discriminator': 4,
                    'includepath': ('y',),
                    'order': 99999,
                },
            ],
        )

    def test_it_conflict(self):
        from . import dummyfactory as f

        result = self._callFUT(
            [
                (None, f),
                (1, f, (2,), {}, ('x',), 'eek'),  # will conflict
                (1, f, (3,), {}, ('y',), 'ack'),  # will conflict
                (4, f, (4,), {}, ('y',)),
                (3, f, (3,), {}, ('y',)),
                (None, f, (5,), {}, ('y',)),
            ]
        )
        self.assertRaises(ConfigurationConflictError, list, result)

    def test_it_with_actions_grouped_by_order(self):
        from . import dummyfactory as f

        result = self._callFUT(
            [
                (None, f),  # X
                (1, f, (1,), {}, (), 'third', 10),  # X
                (1, f, (2,), {}, ('x',), 'fourth', 10),
                (1, f, (3,), {}, ('y',), 'fifth', 10),
                (2, f, (1,), {}, (), 'sixth', 10),  # X
                (3, f, (1,), {}, (), 'seventh', 10),  # X
                (5, f, (4,), {}, ('y',), 'eighth', 99999),  # X
                (4, f, (3,), {}, (), 'first', 5),  # X
                (4, f, (5,), {}, ('y',), 'second', 5),
            ]
        )
        result = list(result)
        self.assertEqual(len(result), 6)
        # resolved actions should be grouped by (order, i)
        self.assertEqual(
            result,
            [
                {
                    'info': None,
                    'args': (),
                    'callable': f,
                    'introspectables': (),
                    'kw': {},
                    'discriminator': None,
                    'includepath': (),
                    'order': 0,
                },
                {
                    'info': 'first',
                    'args': (3,),
                    'callable': f,
                    'introspectables': (),
                    'kw': {},
                    'discriminator': 4,
                    'includepath': (),
                    'order': 5,
                },
                {
                    'info': 'third',
                    'args': (1,),
                    'callable': f,
                    'introspectables': (),
                    'kw': {},
                    'discriminator': 1,
                    'includepath': (),
                    'order': 10,
                },
                {
                    'info': 'sixth',
                    'args': (1,),
                    'callable': f,
                    'introspectables': (),
                    'kw': {},
                    'discriminator': 2,
                    'includepath': (),
                    'order': 10,
                },
                {
                    'info': 'seventh',
                    'args': (1,),
                    'callable': f,
                    'introspectables': (),
                    'kw': {},
                    'discriminator': 3,
                    'includepath': (),
                    'order': 10,
                },
                {
                    'info': 'eighth',
                    'args': (4,),
                    'callable': f,
                    'introspectables': (),
                    'kw': {},
                    'discriminator': 5,
                    'includepath': ('y',),
                    'order': 99999,
                },
            ],
        )

    def test_override_success_across_orders(self):
        from . import dummyfactory as f

        result = self._callFUT(
            [
                (1, f, (2,), {}, ('x',), 'eek', 0),
                (1, f, (3,), {}, ('x', 'y'), 'ack', 10),
            ]
        )
        result = list(result)
        self.assertEqual(
            result,
            [
                {
                    'info': 'eek',
                    'args': (2,),
                    'callable': f,
                    'introspectables': (),
                    'kw': {},
                    'discriminator': 1,
                    'includepath': ('x',),
                    'order': 0,
                }
            ],
        )

    def test_conflicts_across_orders(self):
        from . import dummyfactory as f

        result = self._callFUT(
            [
                (1, f, (2,), {}, ('x', 'y'), 'eek', 0),
                (1, f, (3,), {}, ('x'), 'ack', 10),
            ]
        )
        self.assertRaises(ConfigurationConflictError, list, result)


class TestActionInfo(unittest.TestCase):
    def _getTargetClass(self):
        from pyramid.config.actions import ActionInfo

        return ActionInfo

    def _makeOne(self, filename, lineno, function, linerepr):
        return self._getTargetClass()(filename, lineno, function, linerepr)

    def test_class_conforms(self):
        from zope.interface.verify import verifyClass

        from pyramid.interfaces import IActionInfo

        verifyClass(IActionInfo, self._getTargetClass())

    def test_instance_conforms(self):
        from zope.interface.verify import verifyObject

        from pyramid.interfaces import IActionInfo

        verifyObject(IActionInfo, self._makeOne('f', 0, 'f', 'f'))

    def test_ctor(self):
        inst = self._makeOne('filename', 10, 'function', 'src')
        self.assertEqual(inst.file, 'filename')
        self.assertEqual(inst.line, 10)
        self.assertEqual(inst.function, 'function')
        self.assertEqual(inst.src, 'src')

    def test___str__(self):
        inst = self._makeOne('filename', 0, 'function', '   linerepr  ')
        self.assertEqual(
            str(inst), "Line 0 of file filename:\n       linerepr  "
        )


def _conflictFunctions(e):
    conflicts = e._conflicts.values()
    for conflict in conflicts:
        for confinst in conflict:
            yield confinst.function


class DummyActionState:
    autocommit = False
    info = ''

    def __init__(self):
        self.actions = []

    def action(self, *arg, **kw):
        self.actions.append((arg, kw))


class DummyIntrospectable:
    def __init__(self):
        self.registered = []

    def register(self, introspector, action_info):
        self.registered.append((introspector, action_info))
