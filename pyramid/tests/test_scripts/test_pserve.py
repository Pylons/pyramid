import os
import unittest
from pyramid.tests.test_scripts import dummy

class TestPServeCommand(unittest.TestCase):
    def setUp(self):
        from pyramid.compat import NativeIO
        self.out_ = NativeIO()
        self.config_factory = dummy.DummyConfigParserFactory()

    def out(self, msg):
        self.out_.write(msg)

    def _get_server(*args, **kwargs):
        def server(app):
            return ''
        return server

    def _getTargetClass(self):
        from pyramid.scripts.pserve import PServeCommand
        return PServeCommand

    def _makeOne(self, *args):
        effargs = ['pserve']
        effargs.extend(args)
        cmd = self._getTargetClass()(effargs)
        cmd.out = self.out
        cmd.ConfigParser = self.config_factory
        return cmd

    def test_run_no_args(self):
        inst = self._makeOne()
        result = inst.run()
        self.assertEqual(result, 2)
        self.assertEqual(self.out_.getvalue(), 'You must give a config file')

    def test_get_options_no_command(self):
        inst = self._makeOne()
        inst.args = ['foo', 'a=1', 'b=2']
        result = inst.get_options()
        self.assertEqual(result, {'a': '1', 'b': '2'})

    def test_parse_vars_good(self):
        inst = self._makeOne('development.ini', 'a=1', 'b=2')
        inst.loadserver = self._get_server

        app = dummy.DummyApp()
        def get_app(*args, **kwargs):
            app.global_conf = kwargs.get('global_conf', None)
        inst.loadapp = get_app

        inst.run()
        self.assertEqual(app.global_conf, {'a': '1', 'b': '2'})

    def test_parse_vars_bad(self):
        inst = self._makeOne('development.ini', 'a')
        inst.loadserver = self._get_server
        self.assertRaises(ValueError, inst.run)

    def test_config_file_finds_watch_files(self):
        inst = self._makeOne('development.ini')
        self.config_factory.items = [('watch_files', 'foo\nbar\n/baz')]
        inst.pserve_file_config('/base/path.ini')
        self.assertEqual(inst.watch_files, [
            os.path.normpath('/base/foo'),
            os.path.normpath('/base/bar'),
            os.path.normpath('/baz'),
        ])

class Test_main(unittest.TestCase):
    def _callFUT(self, argv):
        from pyramid.scripts.pserve import main
        return main(argv, quiet=True)

    def test_it(self):
        result = self._callFUT(['pserve'])
        self.assertEqual(result, 2)
