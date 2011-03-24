def includeme(config):
    config.add_route('rdf',
                     'licenses/:license_code/:license_version/rdf',
                     '.views.rdf_view')
    config.add_route('juri',
                     'licenses/:license_code/:license_version/:jurisdiction',
                     '.views.juri_view')
