from repoze.bfg.view import bfg_view

@bfg_view(name='subpackage_notinit')
def subpackage_notinit(context, request):
    return 'subpackage_notinit'
