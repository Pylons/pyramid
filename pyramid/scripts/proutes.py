import optparse
import sys
import textwrap

from pyramid.paster import bootstrap

def main(argv=sys.argv, quiet=False):
    command = PRoutesCommand(argv, quiet)
    return command.run()

class PRoutesCommand(object):
    description = """\
    Print all URL dispatch routes used by a Pyramid application in the
    order in which they are evaluated.  Each route includes the name of the
    route, the pattern of the route, and the view callable which will be
    invoked when the route is matched.

    This command accepts one positional argument named "config_uri".  It
    specifies the PasteDeploy config file to use for the interactive
    shell. The format is "inifile#name". If the name is left off, "main"
    will be assumed.  Example: "proutes myapp.ini".

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

    def _get_mapper(self, registry):
        from pyramid.config import Configurator
        config = Configurator(registry = registry)
        return config.get_routes_mapper()

    def out(self, msg): # pragma: no cover
        if not self.quiet:
            print(msg)
    
    def run(self, quiet=False):
        if not self.args:
            self.out('requires a config file argument')
            return 2
        from pyramid.interfaces import IRouteRequest
        from pyramid.interfaces import IViewClassifier
        from pyramid.interfaces import IView
        from zope.interface import Interface
        config_uri = self.args[0]
        env = self.bootstrap[0](config_uri)
        registry = env['registry']
        mapper = self._get_mapper(registry)
        if mapper is not None:
            routes = mapper.get_routes()
            fmt = '%-15s %-30s %-25s'
            if not routes:
                return 0
            self.out(fmt % ('Name', 'Pattern', 'View'))
            self.out(
                fmt % ('-'*len('Name'), '-'*len('Pattern'), '-'*len('View')))
            for route in routes:
                pattern = route.pattern
                if not pattern.startswith('/'):
                    pattern = '/' + pattern
                request_iface = registry.queryUtility(IRouteRequest,
                                                      name=route.name)
                view_callable = None
                if (request_iface is None) or (route.factory is not None):
                    self.out(fmt % (route.name, pattern, '<unknown>'))
                else:
                    view_callable = registry.adapters.lookup(
                        (IViewClassifier, request_iface, Interface),
                        IView, name='', default=None)
                    self.out(fmt % (route.name, pattern, view_callable))
        return 0

