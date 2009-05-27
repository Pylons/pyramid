import os
import sys

from code import interact

from paste.deploy import loadapp

from paste.script.templates import Template
from paste.script.command import Command
from paste.script.command import BadCommand

from paste.util.template import paste_script_template_renderer

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
    environ = {}
    interact = (interact,) # for testing
    loadapp = (loadapp,) # for testing
    verbose = 3

    def __init__(self, name):
        Command.__init__(self, name)

    def command(self):
        cprt =('Type "help" for more information. "root" is the BFG app '
               'root object.')
        banner = "Python %s on %s\n%s" % (sys.version, sys.platform, cprt)

        config_file, section_name = self.args
        config_name = 'config:%s' % config_file
        here_dir = os.getcwd()

        app = self.loadapp[0](config_name,
                              name=section_name, relative_to=here_dir)
        registry = app.registry
        threadlocals = {'registry':registry, 'request':None}
        try:
            app.threadlocal_manager.push(threadlocals)
            root = app.root_factory(self.environ)
            self.interact[0](banner, local={'root':root})
        finally:
            app.threadlocal_manager.pop()
            
