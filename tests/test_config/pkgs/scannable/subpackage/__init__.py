from pyramid.renderers import null_renderer
from pyramid.view import view_config


@view_config(name='subpackage_init', renderer=null_renderer)
def subpackage_init(context, request):
    return 'subpackage_init'
