import os
import sys

from zope.component import queryUtility
from zope.component.interfaces import ComponentLookupError
from zope.component import getSiteManager

from zope.interface import classProvides
from zope.interface import implements

from webob import Response

from repoze.bfg.interfaces import IView
from repoze.bfg.interfaces import INodeView
from repoze.bfg.interfaces import ITemplateFactory

class Z3CPTTemplateFactory(object):
    classProvides(ITemplateFactory)
    implements(IView)

    def __init__(self, path):
        from z3c.pt import PageTemplateFile
        self.template = PageTemplateFile(path)

    def __call__(self, *arg, **kw):
        result = self.template.render(**kw)
        response = Response(result)
        return response

class XSLTemplateFactory(object):
    classProvides(ITemplateFactory)
    implements(INodeView)

    def __init__(self, path):
        self.path = path

    def __call__(self, node, **kw):
        processor = get_processor(self.path)
        result = str(processor(node, **kw))
        response = Response(result)
        return response

# Manage XSLT processors on a per-thread basis
import threading
from lxml import etree
xslt_pool = threading.local()
def get_processor(xslt_fn):
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

def package_path(package):
    return os.path.abspath(os.path.dirname(package.__file__))

def registerTemplate(template, path):
    try:
        sm = getSiteManager()
    except ComponentLookupError:
        pass
    else:
        sm.registerUtility(template, IView, name=path)

def render_template(path, **kw):
    """ Render a z3c.pt (ZPT) template at the package-relative path
    (may also be absolute) using the kwargs in ``*kw`` as top-level
    names and return a Response object. """
    # XXX use pkg_resources

    if not os.path.isabs(path):
        package_globals = sys._getframe(1).f_globals
        package_name = package_globals['__name__']
        package = sys.modules[package_name]
        prefix = package_path(package)
        path = os.path.join(prefix, path)

    template = queryUtility(IView, path)

    if template is None:
        if not os.path.exists(path):
            raise ValueError('Missing template file: %s' % path)
        template = Z3CPTTemplateFactory(path)
        registerTemplate(template, path)

    return template(**kw)

def render_transform(path, node, **kw):
    """ Render a XSL template at the package-relative path (may also
    be absolute) using the kwargs in ``*kw`` as top-level names and
    return a Response object."""
    # Render using XSLT

    if not os.path.isabs(path):
        package_globals = sys._getframe(1).f_globals
        package_name = package_globals['__name__']
        package = sys.modules[package_name]
        prefix = package_path(package)
        path = os.path.join(prefix, path)

    template = queryUtility(IView, path)
    if template is None:
        if not os.path.exists(path):
            raise ValueError('Missing template file: %s' % path)
        template = XSLTemplateFactory(path)
        registerTemplate(template, path)

    return template(node, **kw)
