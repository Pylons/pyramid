from zope.interface import Interface
from zope.interface import implements
from zope.location.interfaces import ILocation
from zope.location.location import Location

from repoze.bfg.security import Everyone
from repoze.bfg.security import Allow

import datetime

class IMapping(Interface):
    pass

class IBlog(Interface):
    pass

class Blog(dict, Location):
    __acl__ = [ (Allow, Everyone, 'view'), (Allow, 'group:editors', 'add'),
                (Allow, 'group:managers', 'manage') ]
    implements(IBlog, IMapping, ILocation)

class IBlogEntry(Interface):
    pass

class BlogEntry(object):
    implements(IBlogEntry)
    def __init__(self, title, body, author):
        self.title = title
        self.body =  body
        self.author = author
        self.created = datetime.datetime.now()

blog = Blog()
blog['sample'] = BlogEntry('Sample Blog Entry',
                           '<p>This is a sample blog entry</p>',
                           'chrism')
def get_root(environ):
    return blog

