import urllib

from zope.component import queryUtility
from zope.deferredimport import deprecated
   
from zope.interface import classProvides
from zope.interface import implements
from repoze.bfg.location import LocationProxy
from repoze.bfg.location import lineage

from repoze.bfg.interfaces import ILocation
from repoze.bfg.interfaces import ITraverser
from repoze.bfg.interfaces import ITraverserFactory
from repoze.bfg.interfaces import ISettings

deprecated(
    "('from repoze.bfg.traversal import model_url' is now "
    "deprecated; instead use 'from repoze.bfg.url import model_url')",
    model_url = "repoze.bfg.url:model_url",
    )

def split_path(path):
    while path.startswith('/'):
        path = path[1:]
    while path.endswith('/'):
        path = path[:-1]
    clean = []
    for segment in path.split('/'):
        segment = urllib.unquote(segment) # deal with spaces in path segment
        if not segment or segment=='.':
            continue
        elif segment == '..':
            del clean[-1]
        else:
            clean.append(segment)
    return clean

def step(ob, name, default, as_unicode=True):
    if as_unicode:
        try:
            name = name.decode('utf-8')
        except UnicodeDecodeError:
            raise TypeError('Could not decode path segment "%s" using the '
                            'UTF-8 decoding scheme' % name)
    if name.startswith('@@'):
        return name[2:], default
    if not hasattr(ob, '__getitem__'):
        return name, default
    try:
        return name, ob[name]
    except KeyError:
        return name, default

_marker = []

class ModelGraphTraverser(object):
    classProvides(ITraverserFactory)
    implements(ITraverser)
    def __init__(self, root):
        self.root = root
        self.locatable = ILocation.providedBy(root)
        self.unicode_path_segments = True
        settings = queryUtility(ISettings)
        if settings is not None:
            self.unicode_path_segments = settings.unicode_path_segments

    def __call__(self, environ):
        unicode_path_segments = self.unicode_path_segments
        path = environ.get('PATH_INFO', '/')
        path = split_path(path)
        ob = self.root

        name = ''

        while path:
            segment = path.pop(0)
            segment, next = step(ob, segment, _marker, unicode_path_segments)
            if next is _marker:
                name = segment
                break
            if (self.locatable) and (not ILocation.providedBy(next)):
                next = LocationProxy(next, ob, segment)
            ob = next

        return ob, name, path

def find_root(model):
    """ Find the root node in the graph to which ``model``
    belongs. Note that ``model`` should be :term:`location`-aware.
    Note that the root node is available in the request object by
    accessing the ``request.root`` attribute.
    """
    for location in lineage(model):
        if location.__parent__ is None:
            model = location
            break
    return model

def find_model(model, path):
    """ Given a model object and a string representing a path
    reference (a set of names delimited by forward-slashes, such as
    the return value of ``model_path``), return an context in this
    application's model graph at the specified path.  If the path
    starts with a slash, the path is considered absolute and the graph
    traversal will start at the root object.  If the path does not
    start with a slash, the path is considered relative and graph
    traversal will begin at the model object supplied to the function.
    In either case, if the path cannot be resolved, a KeyError will be
    thrown. Note that the model passed in should be
    :term:`location`-aware."""

    if path.startswith('/'):
        model = find_root(model)

    if path.__class__ is unicode:
        # the traverser factory expects PATH_INFO to be a string,
        # not unicode (it's the same traverser which accepts PATH_INFO
        # from user agents; user agents always send strings).
        path = path.encode('utf-8')

    ob, name, path = ITraverserFactory(model)({'PATH_INFO':path})
    if name:
        raise KeyError('%r has no subelement %s' % (ob, name))
    return ob

def find_interface(model, interface):
    """
    Return the first object found which provides the interface
    ``interface`` in the parent chain of ``model`` or ``None`` if no
    object providing ``interface`` can be found in the parent chain.
    The ``model`` passed in should be :term:`location`-aware.
    """
    for location in lineage(model):
        if interface.providedBy(location):
            return location

def model_path(model, *elements):
    """ Return a string representing the absolute path of the model
    object based on its position in the model graph, e.g ``/foo/bar``.
    This function is the inverse of ``find_model``: it can be used to
    generate paths that can later be resolved via ``find_model``.  Any
    positional arguments passed in as ``elements`` will be joined by
    slashes and appended to the generated path.  The ``model`` passed
    in must be :term:`location`-aware.

    Note that the way this function treats path segments is not
    equivalent to how the ``repoze.bfg.url.model_url`` API treats path
    segments: individual segments that make up the path are not quoted
    in any way.  Thus, to ensure that this function generates paths
    that can later be resolved to models via ``find_model``, you
    should ensure that your model __name__ attributes do not contain
    any forward slashes.

    The path returned may be a unicode object if any model name in the
    model graph is a unicode object; otherwise it will be a string.
    """
    rpath = []
    for location in lineage(model):
        if location.__name__:
            rpath.append(location.__name__)
    path = '/' + '/'.join(reversed(rpath))
    if elements: # never have a trailing slash
        suffix = '/'.join(elements)
        path = '/'.join([path, suffix])
    return path

