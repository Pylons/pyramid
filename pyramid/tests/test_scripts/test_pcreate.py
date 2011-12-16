import unittest

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
        cmd = self._makeOne('-s', 'dummy', 'Distro')
        scaffold = DummyScaffold('dummy')
        cmd.scaffolds = [scaffold]
        result = cmd.run()
        self.assertEqual(result, 0)
        self.assertEqual(
            scaffold.output_dir,
            os.path.normpath(os.path.join(os.getcwd(), 'Distro'))
            )
        self.assertEqual(
            scaffold.vars,
            {'project': 'Distro', 'egg': 'Distro', 'package': 'distro'})

    def test_known_scaffold_absolute_path(self):
        import os
        path = os.path.abspath('Distro')
        cmd = self._makeOne('-s', 'dummy', path)
        scaffold = DummyScaffold('dummy')
        cmd.scaffolds = [scaffold]
        result = cmd.run()
        self.assertEqual(result, 0)
        self.assertEqual(
            scaffold.output_dir,
            os.path.normpath(os.path.join(os.getcwd(), 'Distro'))
            )
        self.assertEqual(
            scaffold.vars,
            {'project': 'Distro', 'egg': 'Distro', 'package': 'distro'})

    def test_known_scaffold_multiple_rendered(self):
        import os
        cmd = self._makeOne('-s', 'dummy1', '-s', 'dummy2', 'Distro')
        scaffold1 = DummyScaffold('dummy1')
        scaffold2 = DummyScaffold('dummy2')
        cmd.scaffolds = [scaffold1, scaffold2]
        result = cmd.run()
        self.assertEqual(result, 0)
        self.assertEqual(
            scaffold1.output_dir,
            os.path.normpath(os.path.join(os.getcwd(), 'Distro'))
            )
        self.assertEqual(
            scaffold1.vars,
            {'project': 'Distro', 'egg': 'Distro', 'package': 'distro'})
        self.assertEqual(
            scaffold2.output_dir,
            os.path.normpath(os.path.join(os.getcwd(), 'Distro'))
            )
        self.assertEqual(
            scaffold2.vars,
            {'project': 'Distro', 'egg': 'Distro', 'package': 'distro'})

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
        
