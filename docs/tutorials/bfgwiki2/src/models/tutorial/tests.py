import unittest
from repoze.bfg import testing

def _initTestingDB():
    from tutorial.models import initialize_sql
    session = initialize_sql('sqlite://')
    return session

class TestMyView(unittest.TestCase):
    def setUp(self):
        _initTestingDB()
        
    def _callFUT(self, request):
        from tutorial.views import my_view
        return my_view(request)

    def test_it(self):
        request = testing.DummyRequest()
        info = self._callFUT(request)
        self.assertEqual(info['root'].name, 'root')
        self.assertEqual(info['project'], 'tutorial')
