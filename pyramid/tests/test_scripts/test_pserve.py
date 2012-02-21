import unittest
import os

class TestPServeCommand(unittest.TestCase):
    def setUp(self):
        from pyramid.compat import NativeIO
        self.out_ = NativeIO()

    def out(self, msg):
        self.out_.write(msg)
        
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

    def test_run_stop_daemon_no_such_pid_file(self):
        path = os.path.join(os.path.dirname(__file__), 'wontexist.pid')
        inst = self._makeOne('--stop-daemon', '--pid-file=%s' % path)
        inst.run()
        self.assertEqual(self.out_.getvalue(),'No PID file exists in %s' %
                         path)
        
    def test_run_stop_daemon_bad_pid_file(self):
        path = __file__
        inst = self._makeOne('--stop-daemon', '--pid-file=%s' % path)
        inst.run()
        self.assertEqual(
            self.out_.getvalue(),'Not a valid PID file in %s' % path)

    def test_run_stop_daemon_invalid_pid_in_file(self):
        import tempfile
        tmp = tempfile.NamedTemporaryFile()
        tmp.write(b'9999999')
        tmp.flush()
        tmpname = tmp.name
        inst = self._makeOne('--stop-daemon', '--pid-file=%s' % tmpname)
        inst.run()
        try:
            tmp.close()
        except:
            pass
        self.assertEqual(self.out_.getvalue(),
                         'PID in %s is not valid (deleting)' % tmpname)

    def test_parse_vars_good(self):
        vars = ['a=1', 'b=2']
        inst = self._makeOne('development.ini')
        result = inst.parse_vars(vars)
        self.assertEqual(result, {'a': '1', 'b': '2'})
        
    def test_parse_vars_bad(self):
        vars = ['a']
        inst = self._makeOne('development.ini')
        self.assertRaises(ValueError, inst.parse_vars, vars)

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
        import tempfile
        filename = tempfile.mktemp()
        try:
            inst = self._makeOne(filename)
            fp = inst.open()
            self.assertEqual(fp.name, filename)
            fp.close()
        finally:
            os.remove(filename)
        
    def test_write(self):
        import tempfile
        filename = tempfile.mktemp()
        try:
            inst = self._makeOne(filename)
            inst.write('hello')
        finally:
            with open(filename) as f:
                data = f.read()
                self.assertEqual(data, 'hello')
            os.remove(filename)

    def test_writeline(self):
        import tempfile
        filename = tempfile.mktemp()
        try:
            inst = self._makeOne(filename)
            inst.writelines('hello')
        finally:
            with open(filename) as f:
                data = f.read()
                self.assertEqual(data, 'hello')
            os.remove(filename)

    def test_flush(self):
        import tempfile
        filename = tempfile.mktemp()
        try:
            inst = self._makeOne(filename)
            inst.flush()
            fp = inst.fileobj
            self.assertEqual(fp.name, filename)
            fp.close()
        finally:
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
        
        
        
