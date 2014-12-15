import optparse
import sys
import textwrap

from pyramid.paster import bootstrap
from pyramid.compat import string_types
from pyramid.interfaces import (
    IRouteRequest,
    IViewClassifier,
    IView,
)
from pyramid.config import not_

from pyramid.scripts.common import parse_vars
from pyramid.static import static_view
from zope.interface import Interface


PAD = 3
ANY_KEY = '*'
UNKNOWN_KEY = '<unknown>'


def main(argv=sys.argv, quiet=False):
    command = PRoutesCommand(argv, quiet)
    return command.run()


def _get_pattern(route):
    pattern = route.pattern

    if not pattern.startswith('/'):
        pattern = '/%s' % pattern
    return pattern


def _get_print_format(max_name, max_pattern, max_view, max_method):
    fmt = '%-{0}s %-{1}s %-{2}s %-{3}s'.format(
        max_name + PAD,
        max_pattern + PAD,
        max_view + PAD,
        max_method + PAD,
    )
    return fmt


def _get_request_methods(route_request_methods, view_request_methods):
    excludes = set()

    if route_request_methods:
        route_request_methods = set(route_request_methods)

    if view_request_methods:
        view_request_methods = set(view_request_methods)

        for method in view_request_methods.copy():
            if method.startswith('!'):
                view_request_methods.remove(method)
                excludes.add(method[1:])

    has_route_methods = route_request_methods is not None
    has_view_methods = len(view_request_methods) > 0
    has_methods = has_route_methods or has_view_methods

    if has_route_methods is False and has_view_methods is False:
        request_methods = [ANY_KEY]
    elif has_route_methods is False and has_view_methods is True:
        request_methods = view_request_methods
    elif has_route_methods is True and has_view_methods is False:
        request_methods = route_request_methods
    else:
        request_methods = route_request_methods.intersection(
            view_request_methods
        )

    request_methods = set(request_methods).difference(excludes)

    if has_methods and not request_methods:
        request_methods = '<route mismatch>'
    elif request_methods:
        if excludes and request_methods == set([ANY_KEY]):
            for exclude in excludes:
                request_methods.add('!%s' % exclude)

        request_methods = ','.join(sorted(request_methods))

    return request_methods


def _get_view_module(view_callable):
    if view_callable is None:
        return UNKNOWN_KEY

    if hasattr(view_callable, '__name__'):
        if hasattr(view_callable, '__original_view__'):
            original_view = view_callable.__original_view__
        else:
            original_view = None

        if isinstance(original_view, static_view):
            if original_view.package_name is not None:
                return '%s:%s' % (
                    original_view.package_name,
                    original_view.docroot
                )
            else:
                return original_view.docroot
        else:
            view_name = view_callable.__name__
    else:
        # Currently only MultiView hits this,
        # we could just not run _get_view_module
        # for them and remove this logic
        view_name = str(view_callable)

    view_module = '%s.%s' % (
        view_callable.__module__,
        view_name,
    )

    # If pyramid wraps something in wsgiapp or wsgiapp2 decorators
    # that is currently returned as pyramid.router.decorator, lets
    # hack a nice name in:
    if view_module == 'pyramid.router.decorator':
        view_module = '<wsgiapp>'

    return view_module


def get_route_data(route, registry):
    pattern = _get_pattern(route)

    request_iface = registry.queryUtility(
        IRouteRequest,
        name=route.name
    )

    route_request_methods = None
    view_request_methods_order = []
    view_request_methods = {}
    view_callable = None

    route_intr = registry.introspector.get(
        'routes', route.name
    )

    if request_iface is None:
        return [
            (route.name, _get_pattern(route), UNKNOWN_KEY, ANY_KEY)
        ]

    view_callable = registry.adapters.lookup(
        (IViewClassifier, request_iface, Interface),
        IView,
        name='',
        default=None
    )
    view_module = _get_view_module(view_callable)

    # Introspectables can be turned off, so there could be a chance
    # that we have no `route_intr` but we do have a route + callable
    if route_intr is None:
        view_request_methods[view_module] = []
        view_request_methods_order.append(view_module)
    else:
        route_request_methods = route_intr['request_methods']

        view_intr = registry.introspector.related(route_intr)

        if view_intr:
            for view in view_intr:
                request_method = view.get('request_methods')

                if request_method is not None:
                    view_callable = view['callable']
                    view_module = _get_view_module(view_callable)

                    if view_module not in view_request_methods:
                        view_request_methods[view_module] = []
                        view_request_methods_order.append(view_module)

                    if isinstance(request_method, string_types):
                        request_method = (request_method,)
                    elif isinstance(request_method, not_):
                        request_method = ('!%s' % request_method.value,)

                    view_request_methods[view_module].extend(request_method)
                else:
                    if view_module not in view_request_methods:
                        view_request_methods[view_module] = []
                        view_request_methods_order.append(view_module)

        else:
            view_request_methods[view_module] = []
            view_request_methods_order.append(view_module)

    final_routes = []

    for view_module in view_request_methods_order:
        methods = view_request_methods[view_module]
        request_methods = _get_request_methods(
            route_request_methods,
            methods
        )

        final_routes.append((
            route.name,
            pattern,
            view_module,
            request_methods,
        ))

    return final_routes


class PRoutesCommand(object):
    description = """\
    Print all URL dispatch routes used by a Pyramid application in the
    order in which they are evaluated.  Each route includes the name of the
    route, the pattern of the route, and the view callable which will be
    invoked when the route is matched.

    This command accepts one positional argument named 'config_uri'.  It
    specifies the PasteDeploy config file to use for the interactive
    shell. The format is 'inifile#name'. If the name is left off, 'main'
    will be assumed.  Example: 'proutes myapp.ini'.

    """
    bootstrap = (bootstrap,)
    stdout = sys.stdout
    usage = '%prog config_uri'

    parser = optparse.OptionParser(
        usage,
        description=textwrap.dedent(description)
    )

    def __init__(self, argv, quiet=False):
        self.options, self.args = self.parser.parse_args(argv[1:])
        self.quiet = quiet

    def out(self, msg):  # pragma: no cover
        if not self.quiet:
            print(msg)

    def _get_mapper(self, registry):
        from pyramid.config import Configurator
        config = Configurator(registry=registry)
        return config.get_routes_mapper()

    def run(self, quiet=False):
        if not self.args:
            self.out('requires a config file argument')
            return 2

        config_uri = self.args[0]
        env = self.bootstrap[0](config_uri, options=parse_vars(self.args[1:]))
        registry = env['registry']
        mapper = self._get_mapper(registry)

        if mapper is None:
            return 0

        max_name = len('Name')
        max_pattern = len('Pattern')
        max_view = len('View')
        max_method = len('Method')

        routes = mapper.get_routes()

        if len(routes) == 0:
            return 0

        mapped_routes = [
            ('Name', 'Pattern', 'View', 'Method'),
            ('----', '-------', '----', '------')
        ]

        for route in routes:
            route_data = get_route_data(route, registry)

            for name, pattern, view, method in route_data:
                if len(name) > max_name:
                    max_name = len(name)

                if len(pattern) > max_pattern:
                    max_pattern = len(pattern)

                if len(view) > max_view:
                    max_view = len(view)

                if len(method) > max_method:
                    max_method = len(method)

                mapped_routes.append((name, pattern, view, method))

        fmt = _get_print_format(max_name, max_pattern, max_view, max_method)

        for route in mapped_routes:
            self.out(fmt % route)

        return 0


if __name__ == '__main__':  # pragma: no cover
    sys.exit(main() or 0)
