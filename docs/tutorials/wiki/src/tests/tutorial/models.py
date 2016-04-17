from persistent import Persistent
from persistent.mapping import PersistentMapping

from pyramid.security import (
    Allow,
    Everyone,
    )

class Wiki(PersistentMapping):
    __name__ = None
    __parent__ = None
    __acl__ = [ (Allow, Everyone, 'view'),
                (Allow, 'group:editors', 'edit') ]

class Page(Persistent):
    def __init__(self, data):
        self.data = data

def appmaker(zodb_root):
    if 'app_root' not in zodb_root:
        app_root = Wiki()
        frontpage = Page('This is the front page')
        app_root['FrontPage'] = frontpage
        frontpage.__name__ = 'FrontPage'
        frontpage.__parent__ = app_root
        zodb_root['app_root'] = app_root
        import transaction
        transaction.commit()
    return zodb_root['app_root']
