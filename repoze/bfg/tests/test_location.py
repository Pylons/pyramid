import unittest

class TestLocation(unittest.TestCase):
    def test_inside(self):
        o1 = Location()
        o2 = Location(); o2.__parent__ = o1
        o3 = Location(); o3.__parent__ = o2
        o4 = Location(); o4.__parent__ = o3

        from repoze.bfg.location import inside
        self.assertEqual(inside(o1, o1), True)
        self.assertEqual(inside(o2, o1), True)
        self.assertEqual(inside(o3, o1), True)
        self.assertEqual(inside(o4, o1), True)
        self.assertEqual(inside(o1, o4), False)
        self.assertEqual(inside(o1, None), False)

    def test_locate(self):
        from repoze.bfg.location import locate
        from repoze.bfg.location import LocationProxy
        
        a = Location()
        parent = Location()
        a_located = locate(a, parent, 'a')
        self.failUnless(a_located is a)
        self.failUnless(a_located.__parent__ is parent)
        self.assertEqual(a_located.__name__, 'a')
        # If we locate the object again, nothing special happens:

        a_located_2 = locate(a_located, parent, 'a')
        self.failUnless(a_located_2 is a_located)

        # If the object does not provide ILocation a LocationProxy is returned:

        l = [1, 2, 3]
        parent = Location()
        l_located = locate(l, parent, 'l')
        self.assertEqual(l_located, [1, 2, 3])
        self.failUnless(l_located.__parent__ is parent)
        self.assertEqual(l_located.__name__, 'l')
        self.failIf(l_located is l)
        self.assertEqual(type(l_located), LocationProxy)

        l_located_2 = locate(l_located, parent, 'l')
        self.failUnless(l_located_2 is l_located)
        # When changing the name, we still do not get a different proxied
        # object:

        l_located_3 = locate(l_located, parent, 'new-name')
        self.failUnless(l_located_3 is l_located_2)

    def test_LocationProxy(self):
        from repoze.bfg.location import LocationProxy
        from repoze.bfg.interfaces import ILocation
        l = [1, 2, 3]
        self.assertEqual(ILocation.providedBy(l), False)
        p = LocationProxy(l, "Dad", "p")
        self.assertEqual(p, [1, 2, 3])
        self.assertEqual(ILocation.providedBy(p), True)
        self.assertEqual(p.__parent__, 'Dad')
        self.assertEqual(p.__name__, 'p')
        import pickle
        self.assertRaises(TypeError, pickle.dumps, p)
        # Proxies should get their doc strings from the object they proxy:
        self.assertEqual(p.__doc__, l.__doc__)

    def test_lineage(self):
        from repoze.bfg.location import lineage
        o1 = Location()
        o2 = Location(); o2.__parent__ = o1
        o3 = Location(); o3.__parent__ = o2
        o4 = Location(); o4.__parent__ = o3
        result = list(lineage(o3))
        self.assertEqual(result, [o3, o2, o1])
        result = list(lineage(o1))
        self.assertEqual(result, [o1])

from repoze.bfg.interfaces import ILocation
from zope.interface import implements
class Location(object):
    implements(ILocation)
    __name__ = __parent__ = None
