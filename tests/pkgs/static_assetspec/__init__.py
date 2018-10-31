def includeme(config):
    config.add_static_view('/', 'tests:fixtures')
