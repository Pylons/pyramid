from pyramid.view import view_config

@view_config(name='subpackage_notinit')
def subpackage_notinit(context, request):
    return 'subpackage_notinit'
