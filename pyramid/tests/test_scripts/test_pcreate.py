import unittest
import os

class TestPCreateCommand(unittest.TestCase):
    def setUp(self):
        from pyramid.compat import NativeIO
        self.out_ = NativeIO()

    def out(self, msg):
        self.out_.write(msg)
        
    def _getTargetClass(self):
        from pyramid.scripts.pcreate import PCreateCommand
        return PCreateCommand

    def _makeOne(self, *args):
        effargs = ['pcreate']
        effargs.extend(args)
        cmd = self._getTargetClass()(effargs)
        cmd.out = self.out
        return cmd

    def test_run_show_scaffolds_exist(self):
        cmd = self._makeOne('-l')
        result = cmd.run()
        self.assertEqual(result, 0)
        out = self.out_.getvalue()
        self.assertTrue(out.startswith('Available scaffolds'))
        
    def test_run_show_scaffolds_none_exist(self):
        cmd = self._makeOne('-l')
        cmd.scaffolds = []
        result = cmd.run()
        self.assertEqual(result, 0)
        out = self.out_.getvalue()
        self.assertTrue(out.startswith('No scaffolds available'))
        
    def test_run_no_scaffold_name(self):
        cmd = self._makeOne()
        result = cmd.run()
        self.assertEqual(result, 2)
        out = self.out_.getvalue()
        self.assertTrue(out.startswith(
            'You must provide at least one scaffold name'))

    def test_no_project_name(self):
        cmd = self._makeOne('-s', 'dummy')
        result = cmd.run()
        self.assertEqual(result, 2)
        out = self.out_.getvalue()
        self.assertTrue(out.startswith('You must provide a project name'))

    def test_unknown_scaffold_name(self):
        cmd = self._makeOne('-s', 'dummyXX', 'distro')
        result = cmd.run()
        self.assertEqual(result, 2)
        out = self.out_.getvalue()
        self.assertTrue(out.startswith('Unavailable scaffolds'))

    def test_known_scaffold_single_rendered(self):
        import os
        cmd = self._makeOne('-s', 'dummy', 'distro')
        scaffold = DummyScaffold('dummy')
        cmd.scaffolds = [scaffold]
        result = cmd.run()
        self.assertEqual(result, 0)
        self.assertEqual(
            scaffold.output_dir,
            os.path.abspath(os.path.normpath('distro'))
            )
        self.assertEqual(
            scaffold.vars,
            {
                'project': 'distro',
                'egg': 'distro',
                'package': 'distro',
                'package_full_name': 'distro'
            })

    def test_known_scaffold_multiple_rendered(self):
        import os
        cmd = self._makeOne('-s', 'dummy1', '-s', 'dummy2', 'distro')
        scaffold1 = DummyScaffold('dummy1')
        scaffold2 = DummyScaffold('dummy2')
        cmd.scaffolds = [scaffold1, scaffold2]
        result = cmd.run()
        self.assertEqual(result, 0)
        self.assertEqual(
            scaffold1.output_dir,
            os.path.abspath(os.path.normpath('distro'))
            )
        self.assertEqual(
            scaffold1.vars,
            {
                'project': 'distro',
                'egg': 'distro',
                'package': 'distro',
                'package_full_name': 'distro'
            })
        self.assertEqual(
            scaffold2.output_dir,
            os.path.abspath(os.path.normpath('distro'))
            )
        self.assertEqual(
            scaffold2.vars,
            {
                'project': 'distro',
                'egg': 'distro',
                'package': 'distro',
                'package_full_name': 'distro'
            })

    def test_customized_output_dir(self):
        import os
        path = 'dummy_customized'
        cmd = self._makeOne('-s', 'dummy', '-d', path, 'distro')
        scaffold = DummyScaffold('dummy')
        cmd.scaffolds = [scaffold]
        result = cmd.run()

        self.assertEqual(result, 0)
        self.assertEqual(
            scaffold.output_dir,
            os.path.abspath(os.path.normpath(path))
            )
        self.assertEqual(
            scaffold.vars,
            {
                'project': 'distro',
                'egg': 'distro',
                'package': 'distro',
                'package_full_name': 'distro'
            })

    def test_customized_output_dir_module(self):
        import os
        path = 'dummy_customized2'
        cmd = self._makeOne('-s', 'dummy', '-d', path, 'distro.distro2')
        scaffold = DummyScaffold('dummy')
        cmd.scaffolds = [scaffold]
        result = cmd.run()

        self.assertEqual(result, 0)
        join_path = os.path.join(path, 'distro')
        self.assertEqual(
            scaffold.output_dir,
            os.path.abspath(os.path.normpath(join_path))
            )
        self.assertEqual(
            scaffold.vars,
            {
                'project': 'distro2',
                'egg': 'distro2',
                'package': 'distro2',
                'package_full_name': 'distro.distro2'
            })

    def test_customized_output_dir_module_dir_based(self):
        import os
        path = 'dummy_customized'
        cmd = self._makeOne('-s', 'dummy', '-d', path, 'distro/Test2')
        scaffold = DummyScaffold('dummy')
        cmd.scaffolds = [scaffold]
        result = cmd.run()

        self.assertEqual(result, 0)
        join_path = os.path.join(path, 'distro')
        self.assertEqual(
            scaffold.output_dir,
            os.path.abspath(os.path.normpath(join_path))
            )
        self.assertEqual(
            scaffold.vars,
            {
                'project': 'Test2',
                'egg': 'Test2',
                'package': 'test2',
                'package_full_name': 'distro.Test2'
            })

    def test_customized_output_dir_abspath(self):
        import os
        path = os.path.abspath('dummy_customized_abspath')
        cmd = self._makeOne('-s', 'dummy', '-d', path, 'distro')
        scaffold = DummyScaffold('dummy')
        cmd.scaffolds = [scaffold]
        result = cmd.run()

        self.assertEqual(result, 0)
        self.assertEqual(
            scaffold.output_dir,
            os.path.abspath(os.path.normpath(path))
            )
        self.assertEqual(
            scaffold.vars,
            {
                'project': 'distro',
                'egg': 'distro',
                'package': 'distro',
                'package_full_name': 'distro'
            })

    def test_customized_output_dir_home(self):
        import os
        path = "~"
        cmd = self._makeOne('-s', 'dummy', '-d', path, 'distro')
        scaffold = DummyScaffold('dummy')
        cmd.scaffolds = [scaffold]
        result = cmd.run()
        user_path = os.path.expanduser('~')
        self.assertEqual(result, 0)
        self.assertEqual(
            scaffold.output_dir,
            os.path.abspath(os.path.normpath(user_path))
            )

    def test_customized_output_dir_root(self):
        import os
        path = "~root"
        cmd = self._makeOne('-s', 'dummy', '-d', path, 'distro/Test2')
        scaffold = DummyScaffold('dummy')
        cmd.scaffolds = [scaffold]
        result = cmd.run()
        self.assertEqual(result, 0)
        join_path = os.path.join(os.path.expanduser("~root"), 'distro')
        self.assertEqual(
            scaffold.output_dir,
            os.path.abspath(os.path.normpath(join_path))
            )
        self.assertEqual(
            scaffold.vars,
            {
                'project': 'Test2',
                'egg': 'Test2',
                'package': 'test2',
                'package_full_name': 'distro.Test2'
            })

    def test_customized_output_dir_non_exist_user(self):
        path = "~__pcreate_test_non_exist_user__"
        cmd = self._makeOne('-s', 'dummy', '-d', path, 'distro')
        scaffold = DummyScaffold('dummy')
        cmd.scaffolds = [scaffold]
        try:
            cmd.run()
        except Exception as e:
            self.assertTrue(str(e) == 'invalid user dir')

    def test_known_scaffold_with_path_as_project_target_rendered(self):
        import os
        cmd = self._makeOne('-s', 'dummy', '/tmp/foo/distro/')
        scaffold = DummyScaffold('dummy')
        cmd.scaffolds = [scaffold]
        result = cmd.run()
        self.assertEqual(result, 0)
        self.assertEqual(
            scaffold.output_dir,
            os.path.abspath(os.path.normpath('/tmp/foo/distro'))
            )
        self.assertEqual(
            scaffold.vars,
            {
                'project': 'distro',
                'egg': 'distro',
                'package': 'distro',
                'package_full_name': 'tmp.foo.distro'
            })
        
    def test__set_args0(self):
        args0 = 'a.b.c.d'
        cmd = self._makeOne('-s', 'dummy', args0)
        result = cmd._set_args0(args0)
        self.assertEqual(result, 'a/b/c/d')

    def test__set_pkg_full_name(self):
        pkg_path = 'a/b/c/d'
        cmd = self._makeOne('-s', 'dummy', pkg_path)
        pkg_full_name = cmd._set_pkg_full_name(pkg_path)
        self.assertEqual(pkg_full_name, 'a.b.c.d')

    def test__set_output_dir(self):
        dir_path = 'a/b/c/d'
        pkg_path = 'e/f'
        cmd = self._makeOne('-s', 'dummy', '-d', dir_path, pkg_path)
        output_dir = cmd._set_output_dir(dir_path, pkg_path)
        assert output_dir == os.path.abspath('a/b/c/d/e')

        dir_path = '~/a/b/c/d'
        pkg_path = 'e/f'
        cmd = self._makeOne('-s', 'dummy', '-d', dir_path, pkg_path)
        output_dir = cmd._set_output_dir(dir_path, pkg_path)
        join_path = os.path.join(os.path.expanduser('~'), 'a/b/c/d', 'e')
        self.assertEqual(
            output_dir,
            os.path.abspath(os.path.normpath(join_path))
            )

        dir_path = '/a/b/c/d'
        pkg_path = 'e/f'
        cmd = self._makeOne('-s', 'dummy', '-d', dir_path, pkg_path)
        output_dir = cmd._set_output_dir(dir_path, pkg_path)
        join_path = os.path.join('/a/b/c/d', 'e')
        self.assertEqual(
            output_dir,
            os.path.abspath(os.path.normpath(join_path))
            )

        dir_path = '/a/b/c/d/'
        pkg_path = '/e/f/'
        cmd = self._makeOne('-s', 'dummy', '-d', dir_path, pkg_path)
        output_dir = cmd._set_output_dir(dir_path, pkg_path)
        join_path = os.path.join('/a/b/c/d', 'e')
        self.assertEqual(
            output_dir,
            os.path.abspath(os.path.normpath(join_path))
            )

class Test_main(unittest.TestCase):
    def _callFUT(self, argv):
        from pyramid.scripts.pcreate import main
        return main(argv, quiet=True)

    def test_it(self):
        result = self._callFUT(['pcreate'])
        self.assertEqual(result, 2)

class DummyScaffold(object):
    def __init__(self, name):
        self.name = name

    def run(self, command, output_dir, vars):
        self.command = command
        self.output_dir = output_dir
        self.vars = vars
        
