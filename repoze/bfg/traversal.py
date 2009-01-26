import urllib

from zope.deferredimport import deprecated
   
from zope.interface import classProvides
from zope.interface import implements

from repoze.bfg.location import LocationProxy
from repoze.bfg.location import lineage

from repoze.bfg.lru import lru_cache

from repoze.bfg.interfaces import ILocation
from repoze.bfg.interfaces import ITraverser
from repoze.bfg.interfaces import ITraverserFactory

deprecated(
    "('from repoze.bfg.traversal import model_url' is now "
    "deprecated; instead use 'from repoze.bfg.url import model_url')",
    model_url = "repoze.bfg.url:model_url",
    )

# ``split_path`` wasn't actually ever an API but people were using it
# anyway.  I turned it into the ``traversal_path`` API in 0.6.5, and
# generate the below deprecation to give folks a heads up.
deprecated(
    "('from repoze.bfg.traversal import split_path' is now deprecated; "
    "instead use 'from repoze.bfg.traversal import traversal_path')",
    split_path = "repoze.bfg.traversal:traversal_path",
    )

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

@lru_cache(500)
def traversal_path(path):
    """ Given a PATH_INFO string (slash-separated path elements),
    return a tuple representing that path which can be used to
    traverse a graph.  The PATH_INFO is split on slashes, creating a
    list of segments.  Each segment is URL-unquoted, and decoded into
    Unicode. Each segment is assumed to be encoded using the UTF-8
    encoding (or a subset, such as ASCII); a TypeError is raised if a
    segment cannot be decoded.  If a segment name is empty or if it is
    ``.``, it is ignored.  If a segment name is ``..``, the previous
    segment is deleted, and the ``..`` is ignored.  Examples:

    ``/``

        ()

    ``/foo/bar/baz``

        (u'foo', u'bar', u'baz')

    ``foo/bar/baz``

        (u'foo', u'bar', u'baz')

    ``/foo/bar/baz/``

        (u'foo', u'bar', u'baz')

    ``/foo//bar//baz/``

        (u'foo', u'bar', u'baz')

    ``/foo/bar/baz/..``

        (u'foo', u'bar')

    ``/my%20archives/hello``

        (u'my archives', u'hello')

    ``/archives/La%20Pe%C3%B1a``

        (u'archives', u'<unprintable unicode>')

    """
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
            try:
                segment = segment.decode('utf-8')
            except UnicodeDecodeError:
                raise TypeError('Could not decode path segment %r using the '
                                'UTF-8 decoding scheme' % segment)
            clean.append(segment)
    return tuple(clean)

_marker = object()

class ModelGraphTraverser(object):
    classProvides(ITraverserFactory)
    implements(ITraverser)
    def __init__(self, root):
        self.root = root
        self.locatable = ILocation.providedBy(root)

    def __call__(self, environ, _marker=_marker):
        try:
            path = environ['PATH_INFO']
        except KeyError:
            path = '/'
        path = list(traversal_path(path))
        locatable = self.locatable
        step = self._step

        ob = self.root
        name = ''

        while path:
            segment = path.pop(0)
            segment, next = step(ob, segment, _marker)
            if next is _marker:
                name = segment
                break
            if locatable and (not ILocation.providedBy(next)):
                next = LocationProxy(next, ob, segment)
            ob = next

        return ob, name, path

    def _step(self, ob, name, default):
        if name.startswith('@@'):
            return name[2:], default
        if not hasattr(ob, '__getitem__'):
            return name, default
        try:
            return name, ob[name]
        except KeyError:
            return name, default

class RoutesModelTraverser(object):
    classProvides(ITraverserFactory)
    implements(ITraverser)
    def __init__(self, context):
        self.context = context

    def __call__(self, environ):
        # the traverser *wants* to get routing args from the environ
        # as of 0.6.5; the rest of this stuff is for backwards
        # compatibility
        try:
            # 0.6.5 +
            routing_args = environ['wsgiorg.routing_args'][1]
        except KeyError:
            # <= 0.6.4
            routing_args = self.context.__dict__
        try:
            view_name = routing_args['view_name']
        except KeyError:
            # b/w compat < 0.6.3
            try:
                view_name = routing_args['controller']
            except KeyError:
                view_name = ''
        try:
            subpath = routing_args['subpath']
            subpath = filter(None, subpath.split('/'))
        except KeyError:
            # b/w compat < 0.6.5
            subpath = []

        return self.context, view_name, subpath
