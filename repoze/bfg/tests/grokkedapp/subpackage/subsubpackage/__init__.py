from repoze.bfg.view import bfg_view

@bfg_view(name='subsubpackage_init')
def subpackage_init(context, request):
    return 'subsubpackage_init'
