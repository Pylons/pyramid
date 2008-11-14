from zope.interface import Interface
from zope.interface import implements

class IMyModel(Interface):
    pass

class MyModel(object):
    implements(IMyModel)

root = MyModel()

def get_root(environ):
    return root
