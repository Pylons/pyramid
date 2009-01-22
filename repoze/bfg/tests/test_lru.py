import unittest

class LRUCacheTests(unittest.TestCase):
    def _getTargetClass(self):
        from repoze.bfg.lru import LRUCache
        return LRUCache

    def _makeOne(self, size):
        return self._getTargetClass()(size)

    def test_size_lessthan_1(self):
        self.assertRaises(ValueError, self._makeOne, 0)

    def test_it(self):
        cache = self._makeOne(3)
        self.assertEqual(cache.get('a'), None)
        cache.put('a', '1')
        pos, value = cache.data.get('a')
        self.assertEqual(cache.clock[pos]['ref'], True)
        self.assertEqual(cache.clock[pos]['key'], 'a')
        self.assertEqual(value, '1')
        self.assertEqual(cache.get('a'), '1')
        self.assertEqual(cache.hand, pos+1)
        pos, value = cache.data.get('a')
        self.assertEqual(cache.clock[pos]['ref'], True)
        self.assertEqual(cache.hand, pos+1)
        self.assertEqual(len(cache.data), 1)
        cache.put('b', '2')
        pos, value = cache.data.get('b')
        self.assertEqual(cache.clock[pos]['ref'], True)
        self.assertEqual(cache.clock[pos]['key'], 'b')
        self.assertEqual(len(cache.data), 2)
        cache.put('c', '3')
        pos, value = cache.data.get('c')
        self.assertEqual(cache.clock[pos]['ref'], True)
        self.assertEqual(cache.clock[pos]['key'], 'c')
        self.assertEqual(len(cache.data), 3)
        pos, value = cache.data.get('a')
        self.assertEqual(cache.clock[pos]['ref'], True)
        cache.get('a')
        cache.put('d', '4')
        self.assertEqual(len(cache.data), 3)
        self.assertEqual(cache.data.get('b'), None)
        cache.put('e', '5')
        self.assertEqual(len(cache.data), 3)
        self.assertEqual(cache.data.get('c'), None)
        self.assertEqual(cache.get('d'), '4')
        self.assertEqual(cache.get('e'), '5')
        self.assertEqual(cache.get('a'), '1')
        self.assertEqual(cache.get('b'), None)
        self.assertEqual(cache.get('c'), None)
                         
class DecoratorTests(unittest.TestCase):
    def _getTargetClass(self):
        from repoze.bfg.lru import lru_cache
        return lru_cache

    def _makeOne(self, cache):
        return self._getTargetClass()(0, cache)

    def test_it(self):
        cache = DummyLRUCache()
        decorator = self._makeOne(cache)
        def wrapped(k):
            return k
        decorated = decorator(wrapped)
        result = decorated(1)
        self.assertEqual(cache[1], 1)
        self.assertEqual(result, 1)
        self.assertEqual(len(cache), 1)
        result = decorated(2)
        self.assertEqual(cache[2], 2) 
        self.assertEqual(result, 2)
        self.assertEqual(len(cache), 2)
        result = decorated(2)
        self.assertEqual(cache[2], 2) 
        self.assertEqual(result, 2)
        self.assertEqual(len(cache), 2)
   
class DummyLRUCache(dict):
    def put(self, k, v):
        return self.__setitem__(k, v)
    
