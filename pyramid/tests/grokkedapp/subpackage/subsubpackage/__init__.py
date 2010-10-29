from pyramid.view import view_config

@view_config(name='subsubpackage_init')
def subpackage_init(context, request):
    return 'subsubpackage_init'
