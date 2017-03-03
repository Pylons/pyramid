import os
import unittest
from pyramid.tests.test_scripts import dummy


here = os.path.abspath(os.path.dirname(__file__))


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

    def test_config_vars_no_command(self):
        inst = self._makeOne()
        inst.args.config_uri = 'foo'
        inst.args.config_vars = ['a=1', 'b=2']
        result = inst.get_config_vars()
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
        self.config_factory.items = [(
            'watch_files',
            'foo\n/baz\npyramid.tests.test_scripts:*.py',
        )]
        inst.pserve_file_config('/base/path.ini', global_conf={'a': '1'})
        self.assertEqual(self.config_factory.defaults, {
            'a': '1',
            'here': os.path.abspath('/base'),
        })
        self.assertEqual(inst.watch_files, [
            os.path.abspath('/base/foo'),
            os.path.abspath('/baz'),
            os.path.abspath(os.path.join(here, '*.py')),
        ])

    def test_reload_call_hupper_with_correct_args(self):
        from pyramid.scripts import pserve

        class AttrDict(dict):
            def __init__(self, *args, **kwargs):
                super(AttrDict, self).__init__(*args, **kwargs)
                self.__dict__ = self

        def dummy_start_reloader(*args, **kwargs):
            dummy_start_reloader.args = args
            dummy_start_reloader.kwargs = kwargs

        orig_hupper = pserve.hupper
        try:
            pserve.hupper = AttrDict(is_active=lambda: False,
                                     start_reloader=dummy_start_reloader)

            inst = self._makeOne('--reload', 'development.ini')
            inst.run()
        finally:
            pserve.hupper = orig_hupper

        self.assertEquals(dummy_start_reloader.args, ('pyramid.scripts.pserve.main',))
        self.assertEquals(dummy_start_reloader.kwargs, {
            'reload_interval': 1,
            'verbose': 1,
            'worker_kwargs': {'argv': ['pserve', '--reload', 'development.ini'],
                              'quiet': False}})


class Test_main(unittest.TestCase):
    def _callFUT(self, argv):
        from pyramid.scripts.pserve import main
        return main(argv, quiet=True)

    def test_it(self):
        result = self._callFUT(['pserve'])
        self.assertEqual(result, 2)
