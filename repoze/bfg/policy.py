import urllib

from zope.interface import implements

from repoze.bfg.interfaces import IPolicy

def split_path(path):
    if path.startswith('/'):
        path = path[1:]
    if path.endswith('/'):
        path = path[:-1]
    clean=[]
    for item in path.split('/'):
        item = urllib.unquote(item) # deal with spaces in path segment
        if not item or item=='.':
            continue
        elif item == '..':
            del clean[-1]
        else:
            clean.append(item)
    return clean

class NaivePolicy:

    implements(IPolicy)

    def __call__(self, environ, root):
        path = split_path(environ['PATH_INFO'])
        
        ob = root
        name = ''
        while path:
            element = pop(path)
            try:
                ob = ob[element]
            except KeyError:
                if path:
                    name = pop(path)
                break
            
        return ob, name, path
            
def pop(path):
    return path.pop(0)

