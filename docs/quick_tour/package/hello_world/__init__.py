from pyramid.config import Configurator
from pyramid_jinja2 import renderer_factory
# Start Sphinx Include 1
from pyramid.session import SignedCookieSessionFactory
# End Sphinx Include 1

from hello_world.models import get_root

def main(global_config, **settings):
    """ This function returns a WSGI application.
    
    It is usually called by the PasteDeploy framework during 
    ``paster serve``.
    """
    settings = dict(settings)
    settings.setdefault('jinja2.i18n.domain', 'hello_world')

    # Start Sphinx Include 2
    my_session_factory = SignedCookieSessionFactory('itsaseekreet')
    config = Configurator(root_factory=get_root, settings=settings,
                          session_factory=my_session_factory)
    # End Sphinx Include 2
    config.add_translation_dirs('locale/')
    # Start Include
    config.include('pyramid_jinja2')
    # End Include


    config.add_static_view('static', 'static')
    config.add_view('hello_world.views.my_view',
                    context='hello_world.models.MyModel', 
                    renderer="mytemplate.jinja2")

    return config.make_wsgi_app()
