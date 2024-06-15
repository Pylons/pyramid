from pyramid.response import Response


def aview(request):
    return Response(request.path)


def configure(config):
    # note:
    #   Since the tests using this application evaluate various path
    #   combinations with or without slashes (notably for routes using
    #   pattern='' or pattern='/' explicitly), automatically redirect to any
    #   corresponding trailing slash variation to simplify HTTP requests.
    #   This does not affect how *leading* slashes of 'route_prefix' are
    #   evaluated, since an HTTP request that doesn't start with a '/' path
    #   is immediately rejected.
    config.add_notfound_view(append_slash=True)

    config.add_route('', pattern='/')
    config.add_view(aview, route_name='')
    config.add_view(aview, name='named_view')
    config.commit()

    with config.route_prefix_context(route_prefix='root_ctx_simple'):
        config.add_view(aview, name='root_ctx_simple_named_view')
        config.add_route('root_ctx_simple', pattern='')
        config.add_view(aview, 'root_ctx_simple')
        config.add_route('ctx_simple_view', pattern=config.route_prefix)
        config.add_view(aview, route_name='ctx_simple_view')
        config.include('tests.pkgs.include_routeprefix_app.nested.configure')
    config.commit()

    with config.route_prefix_context(route_prefix='/root_ctx_slash'):
        config.add_view(aview, name='root_ctx_slash_named_view')
        config.add_route('root_ctx_slash', pattern='/')
        config.add_view(aview, 'root_ctx_slash')
        config.add_route('ctx_slash_view', pattern=config.route_prefix)
        config.add_view(aview, route_name='ctx_slash_view')
        config.include('tests.pkgs.include_routeprefix_app.nested.configure')
    config.commit()

    config.include('tests.pkgs.include_routeprefix_app.nested.configure')
    config.include(
        'tests.pkgs.include_routeprefix_app.nested.configure',
        route_prefix='prefix_simple',
    )
    config.include(
        'tests.pkgs.include_routeprefix_app.nested.configure',
        route_prefix='/prefix_slash',
    )
