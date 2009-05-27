import threading
from zope.component import getGlobalSiteManager

class ThreadLocalManager(threading.local):
    def __init__(self, default):
        self.stack = []
        self.default = default
        
    def push(self, info):
        self.stack.append(info)

    set = push # b/c

    def pop(self):
        if self.stack:
            return self.stack.pop()

    def get(self):
        try:
            return self.stack[-1]
        except IndexError:
            return self.default()

    def clear(self):
        self.stack[:] = []

def defaults():
    defaults = {'request':None}
    gsm = getGlobalSiteManager()
    defaults['registry'] = gsm
    return defaults

manager = ThreadLocalManager(defaults)

def setManager(new_manager): # for unit tests
    global manager
    old_manager = manager
    manager = new_manager
    return old_manager
