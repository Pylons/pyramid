import urllib

from zope.interface import implements

from repoze.bfg.interfaces import ITraversalPolicy
from repoze.bfg.interfaces import ITraverser

def split_path(path):
    if path.startswith('/'):
        path = path[1:]
    if path.endswith('/'):
        path = path[:-1]
    clean=[]
    for segment in path.split('/'):
        segment = urllib.unquote(segment) # deal with spaces in path segment
        if not segment or segment=='.':
            continue
        elif segment == '..':
            del clean[-1]
        else:
            clean.append(segment)
    return clean

class NaiveTraversalPolicy:
    implements(ITraversalPolicy)

    def __call__(self, environ, root):
        path = split_path(environ['PATH_INFO'])
        
        ob = root
        name = ''

        while path:
            segment = pop(path)
            traverser = ITraverser(ob)
            next = traverser(environ, segment)
            if next is None:
                if path:
                    name = pop(path)
                break
            ob = next

        return ob, name, path

def pop(path):
    return path.pop(0)

