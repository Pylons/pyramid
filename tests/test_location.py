import unittest
from zope.interface import implementer

from pyramid.interfaces import ILocation


class TestInside(unittest.TestCase):
    def _callFUT(self, one, two):
        from pyramid.location import inside

        return inside(one, two)

    def test_inside(self):
        o1 = Location()
        o2 = Location()
        o2.__parent__ = o1
        o3 = Location()
        o3.__parent__ = o2
        o4 = Location()
        o4.__parent__ = o3

        self.assertEqual(self._callFUT(o1, o1), True)
        self.assertEqual(self._callFUT(o2, o1), True)
        self.assertEqual(self._callFUT(o3, o1), True)
        self.assertEqual(self._callFUT(o4, o1), True)
        self.assertEqual(self._callFUT(o1, o4), False)
        self.assertEqual(self._callFUT(o1, None), False)


class TestLineage(unittest.TestCase):
    def _callFUT(self, context):
        from pyramid.location import lineage

        return lineage(context)

    def test_lineage(self):
        o1 = Location()
        o2 = Location()
        o2.__parent__ = o1
        o3 = Location()
        o3.__parent__ = o2
        o4 = Location()
        o4.__parent__ = o3
        result = list(self._callFUT(o3))
        self.assertEqual(result, [o3, o2, o1])
        result = list(self._callFUT(o1))
        self.assertEqual(result, [o1])


@implementer(ILocation)
class Location:
    __name__ = __parent__ = None
