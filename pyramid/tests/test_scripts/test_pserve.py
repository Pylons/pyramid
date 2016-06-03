import os
import tempfile
import unittest

class TestPServeCommand(unittest.TestCase):
    def setUp(self):
        from pyramid.compat import NativeIO
        self.out_ = NativeIO()

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
        from pyramid.tests.test_scripts.dummy import DummyApp

        inst = self._makeOne('development.ini', 'a=1', 'b=2')
        inst.loadserver = self._get_server


        app = DummyApp()

        def get_app(*args, **kwargs):
            app.global_conf = kwargs.get('global_conf', None)

        inst.loadapp = get_app
        inst.run()

        self.assertEqual(app.global_conf, {'a': '1', 'b': '2'})

    def test_parse_vars_bad(self):
        inst = self._makeOne('development.ini', 'a')
        inst.loadserver = self._get_server
        self.assertRaises(ValueError, inst.run)

class Test_main(unittest.TestCase):
    def _callFUT(self, argv):
        from pyramid.scripts.pserve import main
        return main(argv, quiet=True)

    def test_it(self):
        result = self._callFUT(['pserve'])
        self.assertEqual(result, 2)

class TestLazyWriter(unittest.TestCase):
    def _makeOne(self, filename, mode='w'):
        from pyramid.scripts.pserve import LazyWriter
        return LazyWriter(filename, mode)

    def test_open(self):
        filename = tempfile.mktemp()
        try:
            inst = self._makeOne(filename)
            fp = inst.open()
            self.assertEqual(fp.name, filename)
        finally:
            fp.close()
            os.remove(filename)

    def test_write(self):
        filename = tempfile.mktemp()
        try:
            inst = self._makeOne(filename)
            inst.write('hello')
        finally:
            with open(filename) as f:
                data = f.read()
                self.assertEqual(data, 'hello')
            inst.close()
            os.remove(filename)

    def test_writeline(self):
        filename = tempfile.mktemp()
        try:
            inst = self._makeOne(filename)
            inst.writelines('hello')
        finally:
            with open(filename) as f:
                data = f.read()
                self.assertEqual(data, 'hello')
            inst.close()
            os.remove(filename)

    def test_flush(self):
        filename = tempfile.mktemp()
        try:
            inst = self._makeOne(filename)
            inst.flush()
            fp = inst.fileobj
            self.assertEqual(fp.name, filename)
        finally:
            fp.close()
            os.remove(filename)

class Test__methodwrapper(unittest.TestCase):
    def _makeOne(self, func, obj, type):
        from pyramid.scripts.pserve import _methodwrapper
        return _methodwrapper(func, obj, type)

    def test___call__succeed(self):
        def foo(self, cls, a=1): return 1
        class Bar(object): pass
        wrapper = self._makeOne(foo, Bar, None)
        result = wrapper(a=1)
        self.assertEqual(result, 1)

    def test___call__fail(self):
        def foo(self, cls, a=1): return 1
        class Bar(object): pass
        wrapper = self._makeOne(foo, Bar, None)
        self.assertRaises(AssertionError, wrapper, cls=1)
