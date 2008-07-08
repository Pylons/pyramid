from zope.interface import Interface
from zope.interface import implements

import datetime

class IMapping(Interface):
    pass

class IBlog(Interface):
    pass

class Blog(dict):
    implements(IBlog, IMapping)
    def __init__(self, name):
        self.__name__ = name
        dict.__init__(self)

class IBlogEntry(Interface):
    pass

class BlogEntry(object):
    implements(IBlogEntry)
    def __init__(self, name, title, body, author):
        self.__name__ = name
        self.title = title
        self.body =  body
        self.author = author
        self.created = datetime.datetime.now()
