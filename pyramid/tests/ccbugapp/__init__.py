def includeme(config):
    config.add_route('rdf', 'licenses/:license_code/:license_version/rdf')
    config.add_route('juri',
                     'licenses/:license_code/:license_version/:jurisdiction')
    config.add_view('.views.rdf_view', route_name='rdf')
    config.add_view('.views.juri_view', route_name='juri')


