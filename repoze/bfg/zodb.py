from zope.interface import implements

from repoze.zodbconn.middleware import get_conn

from repoze.bfg.interfaces import IPolicy

class ZODBGetitemPolicy:

    implements(IPolicy)

    def __init__(self, dbname, prefix=()):
        self.dbname = dbname
        self.prefix = prefix
        self.get_conn = get_conn
        
    def __call__(self, environ):
        conn = self.get_conn(environ, self.dbname)
        if conn is None:
            raise ValueError('No such connection %s' % self.dbname)

        path = environ['PATH_INFO'].split('/')
        path = list(self.prefix) + path
        
        ob = conn.open()

        name = ''
        while path:
            element = path.pop(0)
            try:
                ob = ob[element]
            except AttributeError, what:
                raise AttributeError(str(what[0]) + ' (element: '+element+')')
            except KeyError:
                if path:
                    name = path.pop(0)
                break

        return ob, name, path
            
