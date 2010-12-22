from zope.interface import implements

from pyramid.interfaces import IFlashMessages

# flash message categories
DEBUG = 'debug' # development messages
INFO = 'info' # informational messages
SUCCESS = 'success' # a message indicating success
WARNING = 'warning' # not an error, but not a success
ERROR = 'error' # an action was unsuccessful

class FlashMessages(dict):
    implements(IFlashMessages)
    def custom(self, name):
        messages = self.get(name, [])
        return messages

    def debug(self):
        return self.get(DEBUG, [])
    
    def info(self):
        return self.get(INFO, [])

    def success(self):
        return self.get(SUCCESS, [])

    def warning(self):
        return self.get(WARNING, [])

    def error(self):
        return self.get(ERROR, [])

