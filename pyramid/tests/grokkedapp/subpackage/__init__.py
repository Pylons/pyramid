from pyramid.view import view_config

@view_config(name='subpackage_init')
def subpackage_init(context, request):
    return 'subpackage_init'
