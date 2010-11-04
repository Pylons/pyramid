from pyramid.configuration import Configurator
from myproject.models import get_root

def app(global_config, **settings):
    """ This function returns a WSGI application.
    
    It is usually called by the PasteDeploy framework during 
    ``paster serve``.
    """
    config = Configurator(root_factory=get_root, settings=settings)
    config.begin()
    config.add_view('myproject.views.my_view',
                    context='myproject.models.MyModel',
                    renderer='myproject:templates/mytemplate.pt')
    config.add_static_view('static', 'myproject:templates/static')
    config.end()
    return config.make_wsgi_app()

