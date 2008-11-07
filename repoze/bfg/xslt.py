import os

from webob import Response

from zope.component import queryUtility
from zope.component import getSiteManager
from zope.component.interfaces import ComponentLookupError
from zope.deprecation import deprecated

from zope.interface import classProvides
from zope.interface import implements

from repoze.bfg.path import caller_path

from repoze.bfg.interfaces import INodeTemplateRenderer
from repoze.bfg.interfaces import ITemplateRendererFactory

def get_transform(path, node):
    """ Return a callable transform object.  When called, the
    transform will return a string.  The ``path`` argument should be a
    package-relative path (also may be absolute) to an XSLT file.
    When called, the transform will use the kwargs in ``*kw`` as top
    level names and the lxml node at ``node``."""
    # Render using XSLT
    path = caller_path(path)

    renderer = queryUtility(INodeTemplateRenderer, path)
    if renderer is None:
        if not os.path.exists(path):
            raise ValueError('Missing template file: %s' % path)
        renderer = XSLTemplateRenderer(path)
        try:
            sm = getSiteManager()
        except ComponentLookupError:
            pass
        else:
            sm.registerUtility(renderer, INodeTemplateRenderer, name=path)
    return renderer

def render_transform(path, node, **kw):
    """ Render a XSL template at the package-relative path (may also
    be absolute) using the kwargs in ``*kw`` as top-level names and
    the lxml node at ``node`` and return a string."""
    path = caller_path(path)
    template = get_transform(path, node)
    return template(node, **kw)

def render_transform_to_response(path, node, **kw):
    """ Render a XSL template at the package-relative path (may also
    be absolute) using the kwargs in ``*kw`` as top-level names and
    the lxml node at ``node`` and return a Response object."""
    path = caller_path(path)
    result = render_transform(path, node, **kw)
    return Response(result)

class XSLTemplateRenderer(object):
    classProvides(ITemplateRendererFactory)
    implements(INodeTemplateRenderer)

    def __init__(self, path, auto_reload=False):
        self.path = path
        self.auto_reload = auto_reload

    def __call__(self, node, **kw):
        processor = get_processor(self.path, self.auto_reload)
        result = str(processor(node, **kw))
        return result

XSLTemplateFactory = XSLTemplateRenderer
deprecated('ZPTTemplateFactory',
           ('repoze.bfg.xslt.XSLTemplateFactory should now be '
            'imported as repoze.bfg.xslt.XSLTTemplateRenderer'))


# Manage XSLT processors on a per-thread basis
import threading
from lxml import etree
xslt_pool = threading.local()
def get_processor(xslt_fn, auto_reload=False):
    if not auto_reload:
        try:
            return xslt_pool.processors[xslt_fn]
        except AttributeError:
            xslt_pool.processors = {}
        except KeyError:
            pass

    # Make a processor and add it to the pool
    source = etree.ElementTree(file=xslt_fn)
    proc = etree.XSLT(source)
    xslt_pool.processors[xslt_fn] = proc
    return proc
