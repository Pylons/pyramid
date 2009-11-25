from repoze.bfg.view import bfg_view

@bfg_view(name='pod_notinit')
def subpackage_notinit(context, request):
    return 'pod_notinit'
