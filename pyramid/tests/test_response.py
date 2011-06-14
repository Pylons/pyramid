import unittest

class TestResponse(unittest.TestCase):
    def _getTargetClass(self):
        from pyramid.response import Response
        return Response
        
    def test_implements_IResponse(self):
        from pyramid.interfaces import IResponse
        cls = self._getTargetClass()
        self.failUnless(IResponse.implementedBy(cls))

    def test_provides_IResponse(self):
        from pyramid.interfaces import IResponse
        inst = self._getTargetClass()()
        self.failUnless(IResponse.providedBy(inst))

