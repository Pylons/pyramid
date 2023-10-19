from io import StringIO
import os
import unittest

from . import dummy

here = os.path.abspath(os.path.dirname(__file__))


class TestPServeCommand(unittest.TestCase):
    def setUp(self):
        self.out_ = StringIO()

    def out(self, msg):
        self.out_.write(msg)

    def _getTargetClass(self):
        from pyramid.scripts.pserve import PServeCommand

        return PServeCommand

    def _makeOne(self, *args, **kwargs):
        effargs = ['pserve']
        effargs.extend(args)
        cmd = self._getTargetClass()(effargs, **kwargs)
        cmd.out = self.out
        self.loader = dummy.DummyLoader()
        cmd._get_config_loader = self.loader
        return cmd

    def test_run_no_args(self):
        inst = self._makeOne()
        result = inst.run()
        self.assertEqual(result, 2)
        self.assertEqual(self.out_.getvalue(), 'You must give a config file')

    def test_parse_vars_good(self):
        inst = self._makeOne('development.ini', 'a=1', 'b=2')
        app = dummy.DummyApp()

        def get_app(name, global_conf):
            app.name = name
            app.global_conf = global_conf
            return app

        self.loader.get_wsgi_app = get_app
        self.loader.server = lambda x: x

        inst.run()
        self.assertEqual(app.global_conf, {'a': '1', 'b': '2', '__script__': 'pserve'})

    def test_original_ignore_files(self):
        msg = 'A change to "ignore_files" was detected'

        def get_app(name, global_conf):
            app.name = name
            app.global_conf = global_conf
            return app

        inst = self._makeOne('development.ini')
        app = dummy.DummyApp()
        self.loader.get_wsgi_app = get_app
        self.loader.server = lambda x: x
        self.loader.settings = {'pserve': {'ignore_files': '*.txt'}}
        inst.run()
        self.assertNotIn(msg, self.out_.getvalue())

        inst = self._makeOne(
            'development.ini', original_ignore_files={'*.txt'}
        )
        app = dummy.DummyApp()
        self.loader.get_wsgi_app = get_app
        self.loader.server = lambda x: x
        self.loader.settings = {'pserve': {'ignore_files': 'foo/*.txt'}}
        inst.run()
        self.assertIn(msg, self.out_.getvalue())

    def test_parse_vars_bad(self):
        inst = self._makeOne('development.ini', 'a')
        self.assertRaises(ValueError, inst.run)

    def test_config_file_finds_watch_files(self):
        inst = self._makeOne('development.ini')
        loader = self.loader('/base/path.ini')
        loader.settings = {
            'pserve': {'watch_files': 'foo\n/baz\ntests.test_scripts:*.py'}
        }
        inst.pserve_file_config(loader, global_conf={'a': '1'})
        self.assertEqual(loader.calls[0]['defaults'], {'a': '1'})
        self.assertEqual(
            inst.watch_files,
            {
                os.path.abspath('/base/foo'),
                os.path.abspath('/baz'),
                os.path.abspath(os.path.join(here, '*.py')),
            },
        )

    def test_config_file_finds_open_url(self):
        inst = self._makeOne('development.ini')
        loader = self.loader('/base/path.ini')
        loader.settings = {'pserve': {'open_url': 'http://127.0.0.1:8080/'}}
        inst.pserve_file_config(loader, global_conf={'a': '1'})
        self.assertEqual(loader.calls[0]['defaults'], {'a': '1'})
        self.assertEqual(inst.open_url, 'http://127.0.0.1:8080/')

    def test_guess_server_url(self):
        inst = self._makeOne('development.ini')
        loader = self.loader('/base/path.ini')
        loader.settings = {'server:foo': {'port': '8080'}}
        url = inst.guess_server_url(loader, 'foo', global_conf={'a': '1'})
        self.assertEqual(loader.calls[0]['defaults'], {'a': '1'})
        self.assertEqual(url, 'http://127.0.0.1:8080')

    def test_reload_call_hupper_with_correct_args(self):
        from pyramid.scripts import pserve

        class AttrDict(dict):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.__dict__ = self

        def dummy_start_reloader(*args, **kwargs):
            dummy_start_reloader.args = args
            dummy_start_reloader.kwargs = kwargs

        orig_hupper = pserve.hupper
        try:
            pserve.hupper = AttrDict(
                is_active=lambda: False, start_reloader=dummy_start_reloader
            )

            inst = self._makeOne('--reload', 'development.ini')
            inst.run()
        finally:
            pserve.hupper = orig_hupper

        self.assertEqual(
            dummy_start_reloader.args, ('pyramid.scripts.pserve.main',)
        )
        self.assertEqual(
            dummy_start_reloader.kwargs,
            {
                'reload_interval': 1,
                'verbose': 1,
                'worker_kwargs': {
                    'argv': ['pserve', '--reload', 'development.ini'],
                    'quiet': False,
                    'original_ignore_files': set(),
                },
                'ignore_files': set(),
            },
        )


class Test_main(unittest.TestCase):
    def _callFUT(self, argv):
        from pyramid.scripts.pserve import main

        return main(argv, quiet=True)

    def test_it(self):
        result = self._callFUT(['pserve'])
        self.assertEqual(result, 2)
