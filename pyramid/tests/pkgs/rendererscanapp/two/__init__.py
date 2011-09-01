from pyramid.view import view_config

@view_config(name='two', renderer='two.pt')
def two(request):
    return {'nameagain':'Two!'}

