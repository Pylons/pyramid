import os
import unittest

class Test_logging_file_config(unittest.TestCase):
    def _callFUT(self, config_file):
        from pyramid.scripts.common import logging_file_config
        dummy_cp = DummyConfigParserModule
        return logging_file_config(config_file, self.fileConfig, dummy_cp)

    def test_it(self):
        config_file, dict = self._callFUT('/abc')
        # use of os.path.abspath here is a sop to Windows
        self.assertEqual(config_file, os.path.abspath('/abc'))
        self.assertEqual(dict['__file__'], os.path.abspath('/abc'))
        self.assertEqual(dict['here'], os.path.abspath('/'))

    def fileConfig(self, config_file, dict):
        return config_file, dict

class DummyConfigParser(object):
    def read(self, x):
        pass

    def has_section(self, name):
        return True

class DummyConfigParserModule(object):
    ConfigParser = DummyConfigParser


