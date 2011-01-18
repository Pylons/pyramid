def includeme(config):
    config.add_view('.views.maybe')
    config.add_view('.views.no', context='.models.NotAnException')
    config.add_view('.views.yes', context=".models.AnException")
    config.add_view('.views.raise_exception', name='raise_exception')
    config.add_route('route_raise_exception', 'route_raise_exception',
                    view='.views.raise_exception')
    config.add_route('route_raise_exception2',
                     'route_raise_exception2',
                     view='.views.raise_exception',
                     factory='.models.route_factory')
    config.add_route('route_raise_exception3',
                    'route_raise_exception3',
                    view='.views.raise_exception',
                    factory='.models.route_factory2')
    config.add_view('.views.whoa', context='.models.AnException',
                    route_name='route_raise_exception3')
    config.add_route('route_raise_exception4', 'route_raise_exception4',
                     view='.views.raise_exception')
    config.add_view('.views.whoa', context='.models.AnException',
                    route_name='route_raise_exception4')
