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

    def test_no_args(self):
        inst = self._makeOne()
        result = inst.run()
        self.assertEqual(result, None)
        self.assertEqual(self.out_.getvalue(), 'You must give a config file')

    def test_stop_daemon_no_such_pid_file(self):
        path = os.path.join(os.path.dirname(__file__), 'wontexist.pid')
        inst = self._makeOne('--stop-daemon', '--pid-file=%s' % path)
        inst.run()
        self.assertEqual(self.out_.getvalue(),'No PID file exists in %s' % path)
        
    def test_stop_daemon_bad_pid_file(self):
        path = __file__
        inst = self._makeOne('--stop-daemon', '--pid-file=%s' % path)
        inst.run()
        self.assertEqual(
            self.out_.getvalue(),'Not a valid PID file in %s' % path)

