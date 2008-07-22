import urllib

from zope.interface import classProvides
from zope.interface import implements
from zope.location.location import located
from zope.location.location import LocationIterator
from zope.location.interfaces import ILocation

from repoze.bfg.interfaces import ITraverser
from repoze.bfg.interfaces import ITraverserFactory

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
    if name.startswith('@@'):
        return name[2:], default
    if not hasattr(ob, '__getitem__'):
        return name, default
    try:
        return name, ob[name]
    except KeyError:
        return name, default

_marker = ()

class ModelGraphTraverser(object):
    classProvides(ITraverserFactory)
    implements(ITraverser)
    def __init__(self, root, request):
        self.root = root
        self.locatable = ILocation.providedBy(root)
        self.request = request

    def __call__(self, environ):
        path = environ.get('PATH_INFO', '/')
        path = split_path(path)
        root = self.root

        ob = self.root
        name = ''

        while path:
            segment = path.pop(0)
            segment, next = step(ob, segment, _marker)
            if next is _marker:
                name = segment
                break
            if self.locatable:
                next = located(next, ob, segment)
            ob = next

        return ob, name, path

def find_interface(context, interface):
    """ Return an object providing 'interface' anywhere in the parent
    chain of 'context' or None if no object providing that interface
    can be found in the parent chain """
    for location in LocationIterator(context):
        if interface.providedBy(location):
            return location
