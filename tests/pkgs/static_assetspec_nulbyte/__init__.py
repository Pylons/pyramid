def includeme(config):
    config.add_static_view('/', 'tests:fixtures/static')
    config.add_static_view('/sub', 'tests:fixtures/static/subdir')
    config.override_asset('tests:fixtures/static/subdir',
                          'tests:fixtures/static')
