from pyramid.renderers import null_renderer
from pyramid.view import view_config


@view_config(name='pod_notinit', renderer=null_renderer)
def subpackage_notinit(context, request):
    return 'pod_notinit'
