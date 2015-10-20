from code import interact
import optparse
import os
import sys
import textwrap
import pkg_resources

from pyramid.compat import configparser
from pyramid.compat import exec_
from pyramid.util import DottedNameResolver
from pyramid.paster import bootstrap

from pyramid.paster import setup_logging

from pyramid.settings import aslist

from pyramid.scripts.common import parse_vars

def main(argv=sys.argv, quiet=False):
    command = PShellCommand(argv, quiet)
    return command.run()


class PShellCommand(object):
    usage = '%prog config_uri'
    description = """\
    Open an interactive shell with a Pyramid app loaded.  This command
    accepts one positional argument named "config_uri" which specifies the
    PasteDeploy config file to use for the interactive shell. The format is
    "inifile#name". If the name is left off, the Pyramid default application
    will be assumed.  Example: "pshell myapp.ini#main"

    If you do not point the loader directly at the section of the ini file
    containing your Pyramid application, the command will attempt to
    find the app for you. If you are loading a pipeline that contains more
    than one Pyramid application within it, the loader will use the
    last one.
    """
    bootstrap = (bootstrap,)  # for testing
    pkg_resources = pkg_resources  # for testing

    parser = optparse.OptionParser(
        usage,
        description=textwrap.dedent(description)
        )
    parser.add_option('-p', '--python-shell',
                      action='store', type='string', dest='python_shell',
                      default='',
                      help=('Select the shell to use. A list of possible '
                            'shells is available using the --list-shells '
                            'option.'))
    parser.add_option('-l', '--list-shells',
                      dest='list',
                      action='store_true',
                      help='List all available shells.')
    parser.add_option('--setup',
                      dest='setup',
                      help=("A callable that will be passed the environment "
                            "before it is made available to the shell. This "
                            "option will override the 'setup' key in the "
                            "[pshell] ini section."))

    ConfigParser = configparser.ConfigParser # testing

    loaded_objects = {}
    object_help = {}
    preferred_shells = []
    setup = None
    pystartup = os.environ.get('PYTHONSTARTUP')

    def __init__(self, argv, quiet=False):
        self.quiet = quiet
        self.options, self.args = self.parser.parse_args(argv[1:])

    def pshell_file_config(self, filename):
        config = self.ConfigParser()
        config.optionxform = str
        config.read(filename)
        try:
            items = config.items('pshell')
        except configparser.NoSectionError:
            return

        resolver = DottedNameResolver(None)
        self.loaded_objects = {}
        self.object_help = {}
        self.setup = None
        for k, v in items:
            if k == 'setup':
                self.setup = v
            elif k == 'default_shell':
                self.preferred_shells = [x.lower() for x in aslist(v)]
            else:
                self.loaded_objects[k] = resolver.maybe_resolve(v)
                self.object_help[k] = v

    def out(self, msg): # pragma: no cover
        if not self.quiet:
            print(msg)

    def run(self, shell=None):
        if self.options.list:
            return self.show_shells()
        if not self.args:
            self.out('Requires a config file argument')
            return 2
        config_uri = self.args[0]
        config_file = config_uri.split('#', 1)[0]
        setup_logging(config_file)
        self.pshell_file_config(config_file)

        # bootstrap the environ
        env = self.bootstrap[0](config_uri, options=parse_vars(self.args[1:]))

        # remove the closer from the env
        self.closer = env.pop('closer')

        # setup help text for default environment
        env_help = dict(env)
        env_help['app'] = 'The WSGI application.'
        env_help['root'] = 'Root of the default resource tree.'
        env_help['registry'] = 'Active Pyramid registry.'
        env_help['request'] = 'Active request object.'
        env_help['root_factory'] = (
            'Default root factory used to create `root`.')

        # override use_script with command-line options
        if self.options.setup:
            self.setup = self.options.setup

        if self.setup:
            # store the env before muddling it with the script
            orig_env = env.copy()

            # call the setup callable
            resolver = DottedNameResolver(None)
            setup = resolver.maybe_resolve(self.setup)
            setup(env)

            # remove any objects from default help that were overidden
            for k, v in env.items():
                if k not in orig_env or env[k] != orig_env[k]:
                    if getattr(v, '__doc__', False):
                        env_help[k] = v.__doc__.replace("\n", " ")
                    else:
                        env_help[k] = v

        # load the pshell section of the ini file
        env.update(self.loaded_objects)

        # eliminate duplicates from env, allowing custom vars to override
        for k in self.loaded_objects:
            if k in env_help:
                del env_help[k]

        # generate help text
        help = ''
        if env_help:
            help += 'Environment:'
            for var in sorted(env_help.keys()):
                help += '\n  %-12s %s' % (var, env_help[var])

        if self.object_help:
            help += '\n\nCustom Variables:'
            for var in sorted(self.object_help.keys()):
                help += '\n  %-12s %s' % (var, self.object_help[var])

        if shell is None:
            try:
                shell = self.make_shell()
            except ValueError as e:
                self.out(str(e))
                self.closer()
                return 1

        if self.pystartup and os.path.isfile(self.pystartup):
            with open(self.pystartup, 'rb') as fp:
                exec_(fp.read().decode('utf-8'), env)
            if '__builtins__' in env:
                del env['__builtins__']

        try:
            shell(env, help)
        finally:
            self.closer()

    def show_shells(self):
        shells = self.find_all_shells()
        sorted_shells = sorted(shells.items(), key=lambda x: x[0].lower())
        max_name = max([len(s) for s in shells])

        self.out('Available shells:')
        for name, factory in sorted_shells:
            shell = factory()
            if shell is not None:
                self.out('  %s' % (name,))
            else:
                self.out('  %s%s  [not available]' % (
                    name,
                    ' ' * (max_name - len(name))))
        return 0

    def find_all_shells(self):
        shells = {}
        for ep in self.pkg_resources.iter_entry_points('pyramid.pshell'):
            name = ep.name
            shell_factory = ep.load()
            shells[name] = shell_factory
        return shells

    def make_shell(self):
        shells = self.find_all_shells()

        shell = None
        user_shell = self.options.python_shell.lower()

        if not user_shell:
            preferred_shells = self.preferred_shells
            if not preferred_shells:
                # by default prioritize all shells above python
                preferred_shells = [k for k in shells.keys() if k != 'python']
            max_weight = len(preferred_shells)
            def order(x):
                # invert weight to reverse sort the list
                # (closer to the front is higher priority)
                try:
                    return preferred_shells.index(x[0].lower()) - max_weight
                except ValueError:
                    return 1
            sorted_shells = sorted(shells.items(), key=order)
            for name, factory in sorted_shells:
                shell = factory()

                if shell is not None:
                    break
        else:
            factory = shells.get(user_shell)

            if factory is not None:
                shell = factory()

            if shell is None:
                raise ValueError(
                    'could not find a shell named "%s"' % user_shell
                )

        if shell is None:
            shell = self.make_default_shell()

        return shell

    @classmethod
    def make_python_shell(cls, interact=interact):
        def shell(env, help):
            cprt = 'Type "help" for more information.'
            banner = "Python %s on %s\n%s" % (sys.version, sys.platform, cprt)
            banner += '\n\n' + help + '\n'
            interact(banner, local=env)
        return shell

    make_default_shell = make_python_shell

    @classmethod
    def make_bpython_shell(cls, BPShell=None):
        if BPShell is None: # pragma: no cover
            try:
                from bpython import embed
                BPShell = embed
            except ImportError:
                return None
        def shell(env, help):
            BPShell(locals_=env, banner=help + '\n')
        return shell

    @classmethod
    def make_ipython_shell(cls, IPShellFactory=None):
        if IPShellFactory is None: # pragma: no cover
            try:
                from IPython.terminal.embed import (
                    InteractiveShellEmbed)
                IPShellFactory = InteractiveShellEmbed
            except ImportError:
                return None
        def shell(env, help):
            IPShell = IPShellFactory(banner2=help + '\n', user_ns=env)
            IPShell()
        return shell


if __name__ == '__main__': # pragma: no cover
    sys.exit(main() or 0)
