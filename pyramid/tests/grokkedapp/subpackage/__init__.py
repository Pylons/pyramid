from pyramid.view import bfg_view

@bfg_view(name='subpackage_init')
def subpackage_init(context, request):
    return 'subpackage_init'
