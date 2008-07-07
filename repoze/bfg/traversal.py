import urllib

from zope.interface import classProvides
from zope.interface import implements

from repoze.bfg.interfaces import IPublishTraverser
from repoze.bfg.interfaces import IPublishTraverserFactory

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

def step(ob, name, default):
    if not hasattr(ob, '__getitem__'):
        return default
    try:
        return ob[name]
    except KeyError:
        return default

_marker = ()

class NaivePublishTraverser:
    classProvides(IPublishTraverserFactory)
    implements(IPublishTraverser)
    def __init__(self, root, request):
        self.root = root
        self.request = request

    def __call__(self, path):
        path = split_path(path)

        ob = self.root
        name = ''

        while path:
            segment = path.pop(0)
            next = step(ob, segment, _marker)
            if next is _marker:
                name = segment
                break
            ob = next

        return ob, name, path


