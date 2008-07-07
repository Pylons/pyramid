from zope.interface import Interface
from zope.interface import Attribute
from zope.interface import implements

class IBlogModel(Interface):
    id = Attribute('id')

class BlogModel(object):
    implements(IBlogModel)
    def __init__(self, id):
        self.id = id

