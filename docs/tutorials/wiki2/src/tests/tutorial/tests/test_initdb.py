import mock
import unittest


class TestInitializeDB(unittest.TestCase):

    @mock.patch('tutorial.scripts.initializedb.sys')
    def test_usage(self, mocked_sys):
        from ..scripts.initializedb import main
        main(argv=['foo'])
        mocked_sys.exit.assert_called_with(1)

    @mock.patch('tutorial.scripts.initializedb.get_tm_session')
    @mock.patch('tutorial.scripts.initializedb.sys')
    def test_run(self, mocked_sys, mocked_session):
        from ..scripts.initializedb import main
        main(argv=['foo', 'development.ini'])
        mocked_session.assert_called_once()


