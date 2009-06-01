from repoze.bfg.security import Allow
from repoze.bfg.security import Everyone

class RoutesContextFactory(object):
    __acl__ = [ (Allow, Everyone, 'view'), (Allow, 'editor', 'edit') ]
    def __init__(self, **kw):
        self.__dict__.update(kw)



