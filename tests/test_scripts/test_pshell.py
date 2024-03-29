import os
import sys
import unittest

from . import dummy


class TestPShellCommand(unittest.TestCase):
    def _getTargetClass(self):
        from pyramid.scripts.pshell import PShellCommand

        return PShellCommand

    def _makeOne(
        self,
        patch_bootstrap=True,
        patch_loader=True,
        patch_args=True,
        patch_options=True,
    ):
        cmd = self._getTargetClass()([])

        if patch_bootstrap:
            self.bootstrap = dummy.DummyBootstrap()
            cmd.bootstrap = self.bootstrap
        if patch_loader:
            self.loader = dummy.DummyLoader()
            cmd.get_config_loader = self.loader
        if patch_args:

            class Args:
                pass

            self.args = Args()
            self.args.config_uri = '/foo/bar/myapp.ini#myapp'
            cmd.args.config_uri = self.args.config_uri
        if patch_options:

            class Options:
                pass

            self.options = Options()
            self.options.python_shell = ''
            self.options.setup = None
            self.options.list = None
            cmd.options = self.options

        # default to None to prevent side-effects from running tests in
        # unknown environments
        cmd.pystartup = None
        return cmd

    def _makeEntryPoints(self, command, shells):
        entry_points = [
            DummyEntryPoint(name, value) for name, value in shells.items()
        ]
        command.importlib_metadata = DummyImportlibMetadata(entry_points)

    def test_command_loads_default_shell(self):
        command = self._makeOne()
        shell = dummy.DummyShell()
        self._makeEntryPoints(command, {})

        command.default_runner = shell
        command.run()
        self.assertEqual(self.bootstrap.a[0], '/foo/bar/myapp.ini#myapp')
        self.assertEqual(
            shell.env,
            {
                'app': self.bootstrap.app,
                'root': self.bootstrap.root,
                'registry': self.bootstrap.registry,
                'request': self.bootstrap.request,
                'root_factory': self.bootstrap.root_factory,
            },
        )
        self.assertTrue(self.bootstrap.closer.called)
        self.assertTrue(shell.help)

    def test_command_errors_with_unknown_shell(self):
        command = self._makeOne()
        out_calls = []

        def out(msg):
            out_calls.append(msg)

        command.out = out

        shell = dummy.DummyShell()

        self._makeEntryPoints(command, {})

        command.default_runner = shell
        command.args.python_shell = 'unknown_python_shell'
        result = command.run()
        self.assertEqual(result, 1)
        self.assertEqual(
            out_calls, ['could not find a shell named "unknown_python_shell"']
        )
        self.assertEqual(self.bootstrap.a[0], '/foo/bar/myapp.ini#myapp')
        self.assertTrue(self.bootstrap.closer.called)

    def test_command_loads_ipython(self):
        command = self._makeOne()
        shell = dummy.DummyShell()
        bad_shell = dummy.DummyShell()
        self._makeEntryPoints(
            command, {'ipython': shell, 'bpython': bad_shell}
        )

        command.args.python_shell = 'ipython'

        command.run()
        self.assertEqual(self.bootstrap.a[0], '/foo/bar/myapp.ini#myapp')
        self.assertEqual(
            shell.env,
            {
                'app': self.bootstrap.app,
                'root': self.bootstrap.root,
                'registry': self.bootstrap.registry,
                'request': self.bootstrap.request,
                'root_factory': self.bootstrap.root_factory,
            },
        )
        self.assertTrue(self.bootstrap.closer.called)
        self.assertTrue(shell.help)

    def test_shell_entry_points(self):
        command = self._makeOne()
        dshell = dummy.DummyShell()

        self._makeEntryPoints(command, {'ipython': dshell, 'bpython': dshell})

        command.default_runner = None
        shell = command.make_shell()
        self.assertEqual(shell, dshell)

    def test_shell_override(self):
        command = self._makeOne()
        ipshell = dummy.DummyShell()
        bpshell = dummy.DummyShell()
        dshell = dummy.DummyShell()

        self._makeEntryPoints(command, {})

        command.default_runner = dshell

        shell = command.make_shell()
        self.assertEqual(shell, dshell)

        command.args.python_shell = 'ipython'
        self.assertRaises(ValueError, command.make_shell)

        self._makeEntryPoints(
            command, {'ipython': ipshell, 'bpython': bpshell, 'python': dshell}
        )

        command.args.python_shell = 'ipython'
        shell = command.make_shell()
        self.assertEqual(shell, ipshell)

        command.args.python_shell = 'bpython'
        shell = command.make_shell()
        self.assertEqual(shell, bpshell)

        command.args.python_shell = 'python'
        shell = command.make_shell()
        self.assertEqual(shell, dshell)

    def test_shell_ordering(self):
        command = self._makeOne()
        ipshell = dummy.DummyShell()
        bpshell = dummy.DummyShell()
        dshell = dummy.DummyShell()

        self._makeEntryPoints(
            command, {'ipython': ipshell, 'bpython': bpshell, 'python': dshell}
        )

        command.default_runner = dshell

        command.preferred_shells = ['ipython', 'bpython']
        shell = command.make_shell()
        self.assertEqual(shell, ipshell)

        command.preferred_shells = ['bpython', 'python']
        shell = command.make_shell()
        self.assertEqual(shell, bpshell)

        command.preferred_shells = ['python', 'ipython']
        shell = command.make_shell()
        self.assertEqual(shell, dshell)

    def test_command_loads_custom_items(self):
        command = self._makeOne()
        model = dummy.Dummy()
        user = dummy.Dummy()
        self.loader.settings = {'pshell': {'m': model, 'User': user}}
        shell = dummy.DummyShell()
        command.run(shell)
        self.assertEqual(self.bootstrap.a[0], '/foo/bar/myapp.ini#myapp')
        self.assertEqual(
            shell.env,
            {
                'app': self.bootstrap.app,
                'root': self.bootstrap.root,
                'registry': self.bootstrap.registry,
                'request': self.bootstrap.request,
                'root_factory': self.bootstrap.root_factory,
                'm': model,
                'User': user,
            },
        )
        self.assertTrue(self.bootstrap.closer.called)
        self.assertTrue(shell.help)

    def test_command_setup(self):
        command = self._makeOne()

        def setup(env):
            env['a'] = 1
            env['root'] = 'root override'
            env['none'] = None

        self.loader.settings = {'pshell': {'setup': setup}}
        shell = dummy.DummyShell()
        command.run(shell)
        self.assertEqual(self.bootstrap.a[0], '/foo/bar/myapp.ini#myapp')
        self.assertEqual(
            shell.env,
            {
                'app': self.bootstrap.app,
                'root': 'root override',
                'registry': self.bootstrap.registry,
                'request': self.bootstrap.request,
                'root_factory': self.bootstrap.root_factory,
                'a': 1,
                'none': None,
            },
        )
        self.assertTrue(self.bootstrap.closer.called)
        self.assertTrue(shell.help)

    def test_command_setup_generator(self):
        command = self._makeOne()
        did_resume_after_yield = {}

        def setup(env):
            env['a'] = 1
            env['root'] = 'root override'
            env['none'] = None
            request = env['request']
            yield
            did_resume_after_yield['result'] = True
            self.assertEqual(request.dummy_attr, 1)

        self.loader.settings = {'pshell': {'setup': setup}}
        shell = dummy.DummyShell()
        command.run(shell)
        self.assertEqual(self.bootstrap.a[0], '/foo/bar/myapp.ini#myapp')
        self.assertEqual(
            shell.env,
            {
                'app': self.bootstrap.app,
                'root': 'root override',
                'registry': self.bootstrap.registry,
                'request': self.bootstrap.request,
                'root_factory': self.bootstrap.root_factory,
                'a': 1,
                'none': None,
            },
        )
        self.assertTrue(did_resume_after_yield['result'])
        self.assertTrue(self.bootstrap.closer.called)
        self.assertTrue(shell.help)

    def test_command_default_shell_option(self):
        command = self._makeOne()
        ipshell = dummy.DummyShell()
        dshell = dummy.DummyShell()
        self._makeEntryPoints(command, {'ipython': ipshell, 'python': dshell})
        self.loader.settings = {
            'pshell': {'default_shell': 'bpython python\nipython'}
        }
        command.run()
        self.assertEqual(self.bootstrap.a[0], '/foo/bar/myapp.ini#myapp')
        self.assertTrue(dshell.called)

    def test_command_loads_check_variable_override_order(self):
        command = self._makeOne()
        model = dummy.Dummy()

        def setup(env):
            env['a'] = 1
            env['m'] = 'model override'
            env['root'] = 'root override'

        self.loader.settings = {'pshell': {'setup': setup, 'm': model}}
        shell = dummy.DummyShell()
        command.run(shell)
        self.assertEqual(self.bootstrap.a[0], '/foo/bar/myapp.ini#myapp')
        self.assertEqual(
            shell.env,
            {
                'app': self.bootstrap.app,
                'root': 'root override',
                'registry': self.bootstrap.registry,
                'request': self.bootstrap.request,
                'root_factory': self.bootstrap.root_factory,
                'a': 1,
                'm': 'model override',
            },
        )
        self.assertTrue(self.bootstrap.closer.called)
        self.assertTrue(shell.help)

    def test_command_loads_setup_from_options(self):
        command = self._makeOne()

        def setup(env):
            env['a'] = 1
            env['root'] = 'root override'

        model = dummy.Dummy()
        self.loader.settings = {'pshell': {'setup': 'abc', 'm': model}}
        command.args.setup = setup
        shell = dummy.DummyShell()
        command.run(shell)
        self.assertEqual(self.bootstrap.a[0], '/foo/bar/myapp.ini#myapp')
        self.assertEqual(
            shell.env,
            {
                'app': self.bootstrap.app,
                'root': 'root override',
                'registry': self.bootstrap.registry,
                'request': self.bootstrap.request,
                'root_factory': self.bootstrap.root_factory,
                'a': 1,
                'm': model,
            },
        )
        self.assertTrue(self.bootstrap.closer.called)
        self.assertTrue(shell.help)

    def test_command_custom_section_override(self):
        command = self._makeOne()
        dummy_ = dummy.Dummy()
        self.loader.settings = {
            'pshell': {
                'app': dummy_,
                'root': dummy_,
                'registry': dummy_,
                'request': dummy_,
            }
        }
        shell = dummy.DummyShell()
        command.run(shell)
        self.assertEqual(self.bootstrap.a[0], '/foo/bar/myapp.ini#myapp')
        self.assertEqual(
            shell.env,
            {
                'app': dummy_,
                'root': dummy_,
                'registry': dummy_,
                'request': dummy_,
                'root_factory': self.bootstrap.root_factory,
            },
        )
        self.assertTrue(self.bootstrap.closer.called)
        self.assertTrue(shell.help)

    def test_command_loads_pythonstartup(self):
        command = self._makeOne()
        command.pystartup = os.path.abspath(
            os.path.join(os.path.dirname(__file__), 'pystartup.txt')
        )
        shell = dummy.DummyShell()
        command.run(shell)
        self.assertEqual(self.bootstrap.a[0], '/foo/bar/myapp.ini#myapp')
        self.assertEqual(
            shell.env,
            {
                'app': self.bootstrap.app,
                'root': self.bootstrap.root,
                'registry': self.bootstrap.registry,
                'request': self.bootstrap.request,
                'root_factory': self.bootstrap.root_factory,
                'foo': 1,
            },
        )
        self.assertTrue(self.bootstrap.closer.called)
        self.assertTrue(shell.help)

    def test_list_shells(self):
        command = self._makeOne()

        dshell = dummy.DummyShell()
        out_calls = []

        def out(msg):
            out_calls.append(msg)

        command.out = out

        self._makeEntryPoints(command, {'ipython': dshell, 'python': dshell})

        command.args.list = True
        result = command.run()
        self.assertEqual(result, 0)
        self.assertEqual(
            out_calls, ['Available shells:', '  ipython', '  python']
        )


class Test_python_shell_runner(unittest.TestCase):
    def _callFUT(self, env, help, interact):
        from pyramid.scripts.pshell import python_shell_runner

        return python_shell_runner(env, help, interact=interact)

    def test_it(self):
        interact = dummy.DummyInteractor()
        self._callFUT({'foo': 'bar'}, 'a help message', interact)
        self.assertEqual(interact.local, {'foo': 'bar'})
        self.assertTrue('a help message' in interact.banner)


class Test_main(unittest.TestCase):
    def _callFUT(self, argv):
        from pyramid.scripts.pshell import main

        return main(argv, quiet=True)

    def test_it(self):
        result = self._callFUT(['pshell'])
        self.assertEqual(result, 2)


class DummyImportlibMetadata:
    def __init__(self, entry_points):
        self._entry_points = entry_points

    def entry_points(self):
        return DummyEntryPoints(self._entry_points)


class DummyEntryPoints:
    def __init__(self, entry_points):
        self._entry_points = entry_points

    if sys.version_info >= (3, 10):

        def select(self, **kw):
            return iter(self._entry_points)

    else:  # pragma no cover

        def get(self, key):
            return list(self._entry_points)


class DummyEntryPoint:
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def load(self):
        return self.value
