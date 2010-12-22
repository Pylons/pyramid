import unittest

class TestFlashMessages(unittest.TestCase):
    def _getTargetClass(self):
        from pyramid.flash import FlashMessages
        return FlashMessages
        
    def _makeOne(self, *arg, **kw):
        cls = self._getTargetClass()
        return cls(*arg, **kw)

    def test_class_conforms(self):
        from zope.interface.verify import verifyClass
        from pyramid.interfaces import IFlashMessages
        verifyClass(IFlashMessages, self._getTargetClass())

    def test_instance_conforms(self):
        from zope.interface.verify import verifyObject
        from pyramid.interfaces import IFlashMessages
        messages = self._makeOne()
        verifyObject(IFlashMessages, messages)

    def test_debug_filled(self):
        from pyramid import flash
        expected = ['one', 'two']
        messages = self._makeOne({flash.DEBUG:expected})
        self.assertEqual(messages.debug(), expected)
        
    def test_debug_empty(self):
        messages = self._makeOne()
        self.assertEqual(messages.debug(), [])
        
    def test_info_filled(self):
        from pyramid import flash
        expected = ['one', 'two']
        messages = self._makeOne({flash.INFO:expected})
        self.assertEqual(messages.info(), expected)
        
    def test_info_empty(self):
        messages = self._makeOne()
        self.assertEqual(messages.info(), [])
                      
    def test_success_filled(self):
        from pyramid import flash
        expected = ['one', 'two']
        messages = self._makeOne({flash.SUCCESS:expected})
        self.assertEqual(messages.success(), expected)
        
    def test_success_empty(self):
        messages = self._makeOne()
        self.assertEqual(messages.success(), [])

    def test_warning_filled(self):
        from pyramid import flash
        expected = ['one', 'two']
        messages = self._makeOne({flash.WARNING:expected})
        self.assertEqual(messages.warning(), expected)
        
    def test_warning_empty(self):
        messages = self._makeOne()
        self.assertEqual(messages.warning(), [])

    def test_error_filled(self):
        from pyramid import flash
        expected = ['one', 'two']
        messages = self._makeOne({flash.ERROR:expected})
        self.assertEqual(messages.error(), expected)
        
    def test_error_empty(self):
        messages = self._makeOne()
        self.assertEqual(messages.error(), [])

    def test_custom_filled(self):
        expected = ['one', 'two']
        messages = self._makeOne({'custom':expected})
        self.assertEqual(messages.custom('custom'), expected)
        
    def test_custom_empty(self):
        messages = self._makeOne()
        self.assertEqual(messages.custom('custom'), [])

