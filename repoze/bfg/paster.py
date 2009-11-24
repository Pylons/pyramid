import os
import sys
from code import interact

from paste.deploy import loadapp
from paste.script.command import Command
from paste.script.templates import Template
from paste.util.template import paste_script_template_renderer

from repoze.bfg.scripting import get_root

try:
    from IPython.Shell import IPShell # pragma: no cover
except ImportError:
    IPShell = None # pragma: no cover


class StarterProjectTemplate(Template):
    _template_dir = 'paster_templates/starter'
    summary = 'repoze.bfg starter project'
    template_renderer = staticmethod(paste_script_template_renderer)

class ZODBProjectTemplate(Template):
    _template_dir = 'paster_templates/zodb'
    summary = 'repoze.bfg ZODB starter project'
    template_renderer = staticmethod(paste_script_template_renderer)

class RoutesAlchemyProjectTemplate(Template):
    _template_dir = 'paster_templates/routesalchemy'
    summary = 'repoze.bfg SQLAlchemy project using Routes (no traversal)'
    template_renderer = staticmethod(paste_script_template_renderer)

class AlchemyProjectTemplate(Template):
    _template_dir = 'paster_templates/alchemy'
    summary = 'repoze.bfg SQLAlchemy project using traversal'
    template_renderer = staticmethod(paste_script_template_renderer)

def get_app(config_file, name, loadapp=loadapp):
    """ Return the WSGI application named ``name`` in the PasteDeploy
    config file ``config_file``"""
    config_name = 'config:%s' % config_file
    here_dir = os.getcwd()
    app = loadapp(config_name, name=name, relative_to=here_dir)
    return app

class BFGShellCommand(Command):
    """Open an interactive shell with a repoze.bfg app loaded.

    This command accepts two positional arguments:

    ``config_file`` -- specifies the PasteDeploy config file to use
    for the interactive shell.  

    ``section_name`` -- specifies the section name in the PasteDeploy
    config file that represents the application.

    Example::

        $ paster bfgshell myapp.ini main

    .. note:: You should use a ``section_name`` that refers to the
              actual ``app`` section in the config file that points at
              your BFG app without any middleware wrapping, or this
              command will almost certainly fail.

    """
    summary = "Open an interactive shell with a repoze.bfg app loaded"
    usage = '\n' + __doc__

    min_args = 2
    max_args = 2
    group_name = 'bfg'

    parser = Command.standard_parser(simulate=True)
    parser.add_option('-d', '--disable-ipython',
                      action='store_true',
                      dest='disable_ipython',
                      help="Don't use IPython even if it is available")

    interact = (interact,) # for testing
    loadapp = (loadapp,) # for testing
    IPShell = IPShell # for testing
    verbose = 3

    def command(self):
        cprt =('Type "help" for more information. "root" is the BFG app '
               'root object.')
        banner = "Python %s on %s\n%s" % (sys.version, sys.platform, cprt)
        config_file, section_name = self.args
        app = get_app(config_file, section_name, loadapp=self.loadapp[0])
        root, closer = get_root(app)
        if self.IPShell is not None and not self.options.disable_ipython:
            try:
                shell = self.IPShell(argv=[], user_ns={'root':root})
                shell.IP.BANNER = shell.IP.BANNER + '\n\n' + banner
                shell.mainloop()
            finally:
                closer()
        else:
            try:
                self.interact[0](banner, local={'root':root})
            finally:
                closer()

                
