import functools
import itertools
import operator
import sys
import traceback
from zope.interface import implementer

from pyramid.exceptions import (
    ConfigurationConflictError,
    ConfigurationError,
    ConfigurationExecutionError,
)
from pyramid.interfaces import IActionInfo
from pyramid.registry import undefer
from pyramid.util import is_nonstr_iter, reraise


class ActionConfiguratorMixin:
    @property
    def action_info(self):
        info = self.info  # usually a ZCML action (ParserInfo) if self.info
        if not info:
            # Try to provide more accurate info for conflict reports
            if self._ainfo:
                info = self._ainfo[0]
            else:
                info = ActionInfo(None, 0, '', '')
        return info

    def action(
        self,
        discriminator,
        callable=None,
        args=(),
        kw=None,
        order=0,
        introspectables=(),
        **extra,
    ):
        """Register an action which will be executed when
        :meth:`pyramid.config.Configurator.commit` is called (or executed
        immediately if ``autocommit`` is ``True``).

        .. warning:: This method is typically only used by :app:`Pyramid`
           framework extension authors, not by :app:`Pyramid` application
           developers.

        The ``discriminator`` uniquely identifies the action.  It must be
        given, but it can be ``None``, to indicate that the action never
        conflicts.  It must be a hashable value.

        The ``callable`` is a callable object which performs the task
        associated with the action when the action is executed.  It is
        optional.

        ``args`` and ``kw`` are tuple and dict objects respectively, which
        are passed to ``callable`` when this action is executed.  Both are
        optional.

        ``order`` is a grouping mechanism; an action with a lower order will
        be executed before an action with a higher order (has no effect when
        autocommit is ``True``).

        ``introspectables`` is a sequence of :term:`introspectable` objects
        (or the empty sequence if no introspectable objects are associated
        with this action).  If this configurator's ``introspection``
        attribute is ``False``, these introspectables will be ignored.

        ``extra`` provides a facility for inserting extra keys and values
        into an action dictionary.
        """
        # catch nonhashable discriminators here; most unit tests use
        # autocommit=False, which won't catch unhashable discriminators
        assert hash(discriminator)

        if kw is None:
            kw = {}

        autocommit = self.autocommit
        action_info = self.action_info

        if not self.introspection:
            # if we're not introspecting, ignore any introspectables passed
            # to us
            introspectables = ()

        if autocommit:
            # callables can depend on the side effects of resolving a
            # deferred discriminator
            self.begin()
            try:
                undefer(discriminator)
                if callable is not None:
                    callable(*args, **kw)
                for introspectable in introspectables:
                    introspectable.register(self.introspector, action_info)
            finally:
                self.end()

        else:
            action = extra
            action.update(
                dict(
                    discriminator=discriminator,
                    callable=callable,
                    args=args,
                    kw=kw,
                    order=order,
                    info=action_info,
                    includepath=self.includepath,
                    introspectables=introspectables,
                )
            )
            self.action_state.action(**action)

    def _get_action_state(self):
        registry = self.registry
        try:
            state = registry.action_state
        except AttributeError:
            state = ActionState()
            registry.action_state = state
        return state

    def _set_action_state(self, state):
        self.registry.action_state = state

    action_state = property(_get_action_state, _set_action_state)

    _ctx = action_state  # bw compat

    def commit(self):
        """
        Commit any pending configuration actions. If a configuration
        conflict is detected in the pending configuration actions, this method
        will raise a :exc:`ConfigurationConflictError`; within the traceback
        of this error will be information about the source of the conflict,
        usually including file names and line numbers of the cause of the
        configuration conflicts.

        .. warning::
           You should think very carefully before manually invoking
           ``commit()``. Especially not as part of any reusable configuration
           methods. Normally it should only be done by an application author at
           the end of configuration in order to override certain aspects of an
           addon.

        """
        self.begin()
        try:
            self.action_state.execute_actions(introspector=self.introspector)
        finally:
            self.end()
        self.action_state = ActionState()  # old actions have been processed


# this class is licensed under the ZPL (stolen from Zope)
class ActionState:
    def __init__(self):
        # NB "actions" is an API, dep'd upon by pyramid_zcml's load_zcml func
        self.actions = []
        self._seen_files = set()

    def processSpec(self, spec):
        """Check whether a callable needs to be processed.  The ``spec``
        refers to a unique identifier for the callable.

        Return True if processing is needed and False otherwise. If
        the callable needs to be processed, it will be marked as
        processed, assuming that the caller will process the callable if
        it needs to be processed.
        """
        if spec in self._seen_files:
            return False
        self._seen_files.add(spec)
        return True

    def action(
        self,
        discriminator,
        callable=None,
        args=(),
        kw=None,
        order=0,
        includepath=(),
        info=None,
        introspectables=(),
        **extra,
    ):
        """Add an action with the given discriminator, callable, and
        arguments"""
        if kw is None:
            kw = {}
        action = extra
        action.update(
            dict(
                discriminator=discriminator,
                callable=callable,
                args=args,
                kw=kw,
                includepath=includepath,
                info=info,
                order=order,
                introspectables=introspectables,
            )
        )
        self.actions.append(action)

    def execute_actions(self, clear=True, introspector=None):
        """Execute the configuration actions

        This calls the action callables after resolving conflicts

        For example:

        >>> output = []
        >>> def f(*a, **k):
        ...    output.append(('f', a, k))
        >>> context = ActionState()
        >>> context.actions = [
        ...   (1, f, (1,)),
        ...   (1, f, (11,), {}, ('x', )),
        ...   (2, f, (2,)),
        ...   ]
        >>> context.execute_actions()
        >>> output
        [('f', (1,), {}), ('f', (2,), {})]

        If the action raises an error, we convert it to a
        ConfigurationExecutionError.

        >>> output = []
        >>> def bad():
        ...    bad.xxx
        >>> context.actions = [
        ...   (1, f, (1,)),
        ...   (1, f, (11,), {}, ('x', )),
        ...   (2, f, (2,)),
        ...   (3, bad, (), {}, (), 'oops')
        ...   ]
        >>> try:
        ...    v = context.execute_actions()
        ... except ConfigurationExecutionError, v:
        ...    pass
        >>> print(v)
        exceptions.AttributeError: 'function' object has no attribute 'xxx'
          in:
          oops

        Note that actions executed before the error still have an effect:

        >>> output
        [('f', (1,), {}), ('f', (2,), {})]

        The execution is re-entrant such that actions may be added by other
        actions with the one caveat that the order of any added actions must
        be equal to or larger than the current action.

        >>> output = []
        >>> def f(*a, **k):
        ...   output.append(('f', a, k))
        ...   context.actions.append((3, g, (8,), {}))
        >>> def g(*a, **k):
        ...    output.append(('g', a, k))
        >>> context.actions = [
        ...   (1, f, (1,)),
        ...   ]
        >>> context.execute_actions()
        >>> output
        [('f', (1,), {}), ('g', (8,), {})]

        """
        try:
            all_actions = []
            executed_actions = []
            action_iter = iter([])
            conflict_state = ConflictResolverState()

            while True:
                # We clear the actions list prior to execution so if there
                # are some new actions then we add them to the mix and resolve
                # conflicts again. This orders the new actions as well as
                # ensures that the previously executed actions have no new
                # conflicts.
                if self.actions:
                    all_actions.extend(self.actions)
                    action_iter = resolveConflicts(
                        self.actions, state=conflict_state
                    )
                    self.actions = []

                action = next(action_iter, None)
                if action is None:
                    # we are done!
                    break

                callable = action['callable']
                args = action['args']
                kw = action['kw']
                info = action['info']
                # we use "get" below in case an action was added via a ZCML
                # directive that did not know about introspectables
                introspectables = action.get('introspectables', ())

                try:
                    if callable is not None:
                        callable(*args, **kw)
                except Exception:
                    t, v, tb = sys.exc_info()
                    try:
                        reraise(
                            ConfigurationExecutionError,
                            ConfigurationExecutionError(t, v, info),
                            tb,
                        )
                    finally:
                        del t, v, tb

                if introspector is not None:
                    for introspectable in introspectables:
                        introspectable.register(introspector, info)

                executed_actions.append(action)

            self.actions = all_actions
            return executed_actions

        finally:
            if clear:
                self.actions = []


class ConflictResolverState:
    def __init__(self):
        # keep a set of resolved discriminators to test against to ensure
        # that a new action does not conflict with something already executed
        self.resolved_ainfos = {}

        # actions left over from a previous iteration
        self.remaining_actions = []

        # after executing an action we memoize its order to avoid any new
        # actions sending us backward
        self.min_order = None

        # unique tracks the index of the action so we need it to increase
        # monotonically across invocations to resolveConflicts
        self.start = 0


# this function is licensed under the ZPL (stolen from Zope)
def resolveConflicts(actions, state=None):
    """Resolve conflicting actions

    Given an actions list, identify and try to resolve conflicting actions.
    Actions conflict if they have the same non-None discriminator.

    Conflicting actions can be resolved if the include path of one of
    the actions is a prefix of the includepaths of the other
    conflicting actions and is unequal to the include paths in the
    other conflicting actions.

    Actions are resolved on a per-order basis because some discriminators
    cannot be computed until earlier actions have executed. An action in an
    earlier order may execute successfully only to find out later that it was
    overridden by another action with a smaller include path. This will result
    in a conflict as there is no way to revert the original action.

    ``state`` may be an instance of ``ConflictResolverState`` that
    can be used to resume execution and resolve the new actions against the
    list of executed actions from a previous call.

    """
    if state is None:
        state = ConflictResolverState()

    # pick up where we left off last time, but track the new actions as well
    state.remaining_actions.extend(normalize_actions(actions))
    actions = state.remaining_actions

    def orderandpos(v):
        n, v = v
        return (v['order'] or 0, n)

    def orderonly(v):
        n, v = v
        return v['order'] or 0

    sactions = sorted(enumerate(actions, start=state.start), key=orderandpos)
    for order, actiongroup in itertools.groupby(sactions, orderonly):
        # "order" is an integer grouping. Actions in a lower order will be
        # executed before actions in a higher order.  All of the actions in
        # one grouping will be executed (its callable, if any will be called)
        # before any of the actions in the next.
        output = []
        unique = {}

        # error out if we went backward in order
        if state.min_order is not None and order < state.min_order:
            r = [
                'Actions were added to order={} after execution had moved '
                'on to order={}. Conflicting actions: '.format(
                    order, state.min_order
                )
            ]
            for i, action in actiongroup:
                for line in str(action['info']).rstrip().split('\n'):
                    r.append("  " + line)
            raise ConfigurationError('\n'.join(r))

        for i, action in actiongroup:
            # Within an order, actions are executed sequentially based on
            # original action ordering ("i").

            # "ainfo" is a tuple of (i, action) where "i" is an integer
            # expressing the relative position of this action in the action
            # list being resolved, and "action" is an action dictionary.  The
            # purpose of an ainfo is to associate an "i" with a particular
            # action; "i" exists for sorting after conflict resolution.
            ainfo = (i, action)

            # wait to defer discriminators until we are on their order because
            # the discriminator may depend on state from a previous order
            discriminator = undefer(action['discriminator'])
            action['discriminator'] = discriminator

            if discriminator is None:
                # The discriminator is None, so this action can never conflict.
                # We can add it directly to the result.
                output.append(ainfo)
                continue

            L = unique.setdefault(discriminator, [])
            L.append(ainfo)

        # Check for conflicts
        conflicts = {}
        for discriminator, ainfos in unique.items():
            # We use (includepath, i) as a sort key because we need to
            # sort the actions by the paths so that the shortest path with a
            # given prefix comes first.  The "first" action is the one with the
            # shortest include path.  We break sorting ties using "i".
            def bypath(ainfo):
                path, i = ainfo[1]['includepath'], ainfo[0]
                return path, order, i

            ainfos.sort(key=bypath)
            ainfo, rest = ainfos[0], ainfos[1:]
            _, action = ainfo

            # ensure this new action does not conflict with a previously
            # resolved action from an earlier order / invocation
            prev_ainfo = state.resolved_ainfos.get(discriminator)
            if prev_ainfo is not None:
                _, paction = prev_ainfo
                basepath, baseinfo = paction['includepath'], paction['info']
                includepath = action['includepath']
                # if the new action conflicts with the resolved action then
                # note the conflict, otherwise drop the action as it's
                # effectively overriden by the previous action
                if (
                    includepath[: len(basepath)] != basepath
                    or includepath == basepath
                ):
                    L = conflicts.setdefault(discriminator, [baseinfo])
                    L.append(action['info'])

            else:
                output.append(ainfo)

            basepath, baseinfo = action['includepath'], action['info']
            for _, action in rest:
                includepath = action['includepath']
                # Test whether path is a prefix of opath
                if (
                    includepath[: len(basepath)] != basepath
                    or includepath == basepath  # not a prefix
                ):
                    L = conflicts.setdefault(discriminator, [baseinfo])
                    L.append(action['info'])

        if conflicts:
            raise ConfigurationConflictError(conflicts)

        # sort resolved actions by "i" and yield them one by one
        for i, action in sorted(output, key=operator.itemgetter(0)):
            # do not memoize the order until we resolve an action inside it
            state.min_order = action['order']
            state.start = i + 1
            state.remaining_actions.remove(action)
            state.resolved_ainfos[action['discriminator']] = (i, action)
            yield action


def normalize_actions(actions):
    """Convert old-style tuple actions to new-style dicts."""
    result = []
    for v in actions:
        if not isinstance(v, dict):
            v = expand_action_tuple(*v)
        result.append(v)
    return result


def expand_action_tuple(
    discriminator,
    callable=None,
    args=(),
    kw=None,
    includepath=(),
    info=None,
    order=0,
    introspectables=(),
):
    if kw is None:
        kw = {}
    return dict(
        discriminator=discriminator,
        callable=callable,
        args=args,
        kw=kw,
        includepath=includepath,
        info=info,
        order=order,
        introspectables=introspectables,
    )


@implementer(IActionInfo)
class ActionInfo:
    def __init__(self, file, line, function, src):
        self.file = file
        self.line = line
        self.function = function
        self.src = src

    def __str__(self):
        srclines = self.src.split('\n')
        src = '\n'.join('    %s' % x for x in srclines)
        return 'Line %s of file %s:\n%s' % (self.line, self.file, src)


def action_method(wrapped):
    """Wrapper to provide the right conflict info report data when a method
    that calls Configurator.action calls another that does the same.  Not a
    documented API but used by some external systems."""

    def wrapper(self, *arg, **kw):
        if self._ainfo is None:
            self._ainfo = []
        info = kw.pop('_info', None)
        # backframes for outer decorators to actionmethods
        backframes = kw.pop('_backframes', 0) + 2
        if is_nonstr_iter(info) and len(info) == 4:
            # _info permitted as extract_stack tuple
            info = ActionInfo(*info)
        if info is None:
            try:
                f = traceback.extract_stack(limit=4)
                info = ActionInfo(*f[-backframes])
            except Exception:  # pragma: no cover
                info = ActionInfo(None, 0, '', '')
        self._ainfo.append(info)
        try:
            result = wrapped(self, *arg, **kw)
        finally:
            self._ainfo.pop()
        return result

    if hasattr(wrapped, '__name__'):
        functools.update_wrapper(wrapper, wrapped)
    wrapper.__docobj__ = wrapped
    return wrapper
