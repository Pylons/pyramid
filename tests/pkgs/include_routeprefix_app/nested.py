from pyramid.response import Response


def aview(request):
    return Response(request.path)


def configure(config):
    # note:
    #   In order to reuse similar routes for prefix and non-prefixed includes,
    #   we must add a prefix to the names as well to avoid conflicts.
    current_prefix = config.route_prefix or ''

    # note:
    #   The following definition is equivalent to doing an 'add.route'
    #   followed by 'config.add_view' with an empty pattern or only '/'
    #   (i.e.: exactly like the next block definition).
    #   However, the resolved path will depend on the parent including this
    #   configuration. If it contains a 'route_prefix', it will be equal to it.
    #   Otherwise, this would become the equal to the 'root' path.
    name = current_prefix + 'nested_root_named_view'
    config.add_view(aview, name=name)

    name = current_prefix + 'nested_route_simple'
    config.add_route(name, pattern='nested_route_simple')
    config.add_view(aview, route_name=name)

    name = current_prefix + 'nested_route_slash'
    config.add_route(name, pattern='/nested_route_slash')
    config.add_view(aview, route_name=name)

    config.commit()

    with config.route_prefix_context(route_prefix='nested_ctx_simple'):
        current_prefix = config.route_prefix or ''

        # note:
        #   Since the following pattern is empty and is always within a context,
        #   it is equivalent to simply doing 'config.add_view(view, name=...)'.
        name = current_prefix + 'nested_ctx_simple_view'
        config.add_route(name, pattern='')
        config.add_view(aview, route_name=name)

        name = current_prefix + 'nested_ctx_route_simple'
        config.add_route(name, pattern='nested_ctx_route_simple')
        config.add_view(aview, route_name=name)

        name = current_prefix + 'nested_ctx_route_slash'
        config.add_route(name, pattern='/nested_ctx_route_slash')
        config.add_view(aview, route_name=name)
    config.commit()

    with config.route_prefix_context(route_prefix='/nested_ctx_slash'):
        current_prefix = config.route_prefix or ''

        # note:
        #   Since the following pattern is empty and is always within a context,
        #   it is equivalent to simply doing 'config.add_view(view, name=...)'.
        name = current_prefix + 'nested_ctx_slash_view'
        config.add_route(name, pattern='/')
        config.add_view(aview, route_name=name)

        name = current_prefix + 'nested_ctx_route_simple'
        config.add_route(name, pattern='nested_ctx_route_simple')
        config.add_view(aview, route_name=name)

        name = current_prefix + 'nested_ctx_route_slash'
        config.add_route(name, pattern='/nested_ctx_route_slash')
        config.add_view(aview, route_name=name)
    config.commit()
