import os
import unittest


class TestInitializeDB(unittest.TestCase):

    def test_usage(self):
        from tutorial.scripts.initialize_db import main
        with self.assertRaises(SystemExit):
            main(argv=['foo'])
