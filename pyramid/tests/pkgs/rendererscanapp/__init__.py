from pyramid.view import view_config

@view_config(name='one', renderer='one.pt')
def one(request):
    return {'name':'One!'}

def includeme(config):
    config.scan()
    
