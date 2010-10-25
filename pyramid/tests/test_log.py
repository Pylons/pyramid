import unittest

class TestFunctions(unittest.TestCase):
    def test_make_stream_logger(self):
        from repoze.bfg.log import make_stream_logger
        import logging
        import sys
        logger = make_stream_logger('foo', sys.stderr, levelname='DEBUG',
                                    fmt='%(message)s')
        self.assertEqual(logger.name, 'foo')
        self.assertEqual(logger.handlers[0].stream, sys.stderr)
        self.assertEqual(logger.handlers[0].formatter._fmt, '%(message)s')
        self.assertEqual(logger.level, logging.DEBUG)
        
        

