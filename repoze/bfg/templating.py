from zope.deprecation import deprecated

from repoze.bfg.renderers import template_renderer_factory

deprecated('renderer_from_cache',
           'The repoze.bfg.templating.renderer_from_cache function has '
           'been deprecated.  As of repoze.bfg version 1.1, you should use the '
           'repoze.bfg.renderers.template_renderer_factory function instead. '
           'Note however that neither the "renderer_from_cache" function '
           'nor the "template_renderer_factory" function is a documented '
           'BFG API.  You shouldn\'t be importing either of these unless '
           'you are willing to deal with incompatibilities introduced in '
           'future BFG versions.')

def renderer_from_cache(path, impl, level=4, **kw):
    return template_renderer_factory(path, impl, level)
