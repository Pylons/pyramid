import os


def includeme(config):
    here = here = os.path.dirname(__file__)
    static = os.path.normpath(
        os.path.join(here, '..', '..', 'fixtures', 'static')
    )
    config.add_static_view('/', static)
