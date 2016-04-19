from pyramid.config import Configurator
from hello_world.resources import get_root
from pyramid.session import SignedCookieSessionFactory


def main(global_config, **settings):
    """ This function returns a WSGI application.
    
    It is usually called by the PasteDeploy framework during 
    ``paster serve``.
    """
    settings = dict(settings)
    settings.setdefault('jinja2.i18n.domain', 'hello_world')

    my_session_factory = SignedCookieSessionFactory('itsaseekreet')
    config = Configurator(root_factory=get_root, settings=settings,
                          session_factory=my_session_factory)
    config.add_translation_dirs('locale/')
    config.include('pyramid_jinja2')

    config.add_static_view('static', 'static')
    config.add_view('hello_world.views.my_view',
                    context='hello_world.resources.MyResource', 
                    renderer="templates/mytemplate.jinja2")

    return config.make_wsgi_app()
