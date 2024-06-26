from pyramid.config import Configurator
from pyramid.session import SignedCookieSessionFactory

from .security import SecurityPolicy


def main(global_config, **settings):
    my_session_factory = SignedCookieSessionFactory('itsaseekreet')
    config = Configurator(
        settings=settings,
        root_factory='.resources.Root',
        session_factory=my_session_factory,
    )
    config.include('pyramid_chameleon')

    config.set_security_policy(
        SecurityPolicy(
            secret=settings['tutorial.secret'],
        ),
    )

    config.add_route('home', '/')
    config.add_route('hello', '/howdy')
    config.add_route('login', '/login')
    config.add_route('logout', '/logout')
    config.scan('.views')
    return config.make_wsgi_app()
