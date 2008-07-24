from zope.interface import implements
from zope.interface import Attribute
from zope.interface import Interface

class IMyModel(Interface):
    __name__ = Attribute('Name of the model instance')

class MyModel(dict):
    implements(IMyModel)
    def __init__(self, name):
        self.__name__ = name

root = MyModel('site')
root['a'] = MyModel('a')
root['b'] = MyModel('b')

def get_root(environ):
    return root
