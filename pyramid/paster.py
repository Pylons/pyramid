import os
import sys
from code import interact

from paste.deploy import loadapp
from paste.script.command import Command
from paste.script.templates import Template
from paste.util.template import paste_script_template_renderer

from pyramid.scripting import get_root

class StarterProjectTemplate(Template):
    egg_plugins = [ 'Pyramid' ]
    _template_dir = 'paster_templates/starter'
    summary = 'pyramid starter project'
    template_renderer = staticmethod(paste_script_template_renderer)

class StarterZCMLProjectTemplate(Template):
    egg_plugins = [ 'Pyramid' ]
    _template_dir = 'paster_templates/starter_zcml'
    summary = 'pyramid starter project (ZCML)'
    template_renderer = staticmethod(paste_script_template_renderer)

class ZODBProjectTemplate(Template):
    egg_plugins = [ 'Pyramid' ]
    _template_dir = 'paster_templates/zodb'
    summary = 'pyramid ZODB starter project'
    template_renderer = staticmethod(paste_script_template_renderer)

class RoutesAlchemyProjectTemplate(Template):
    egg_plugins = [ 'Pyramid' ]
    _template_dir = 'paster_templates/routesalchemy'
    summary = 'pyramid SQLAlchemy project using Routes (no traversal)'
    template_renderer = staticmethod(paste_script_template_renderer)

class AlchemyProjectTemplate(Template):
    egg_plugins = [ 'Pyramid' ]
    _template_dir = 'paster_templates/alchemy'
    summary = 'pyramid SQLAlchemy project using traversal'
    template_renderer = staticmethod(paste_script_template_renderer)

class PylonsBasicProjectTemplate(Template):
    egg_plugins = [ 'Pyramid' ]
    _template_dir = 'paster_templates/pylons_basic'
    summary = 'Pylons basic project'
    template_renderer = staticmethod(paste_script_template_renderer)

class PylonsMinimalProjectTemplate(Template):
    egg_plugins = [ 'Pyramid' ]
    _template_dir = 'paster_templates/pylons_minimal'
    summary = 'Pylons minimal project'
    template_renderer = staticmethod(paste_script_template_renderer)

class PylonsSQLAlchemyProjectTemplate(Template):
    egg_plugins = [ 'Pyramid' ]
    _template_dir = 'paster_templates/pylons_sqla'
    summary = 'Pylons SQLAlchemy project'
    template_renderer = staticmethod(paste_script_template_renderer)

def get_app(config_file, name, loadapp=loadapp):
    """ Return the WSGI application named ``name`` in the PasteDeploy
    config file ``config_file``"""
    config_name = 'config:%s' % config_file
    here_dir = os.getcwd()
    app = loadapp(config_name, name=name, relative_to=here_dir)
    return app

_marker = object()
class PShellCommand(Command):
    """Open an interactive shell with a :mod:`pyramid` app loaded.

    This command accepts two positional arguments:

    ``config_file`` -- specifies the PasteDeploy config file to use
    for the interactive shell.  

    ``section_name`` -- specifies the section name in the PasteDeploy
    config file that represents the application.

    Example::

        $ paster pshell myapp.ini main

    .. note:: You should use a ``section_name`` that refers to the
              actual ``app`` section in the config file that points at
              your Pyramid app without any middleware wrapping, or this
              command will almost certainly fail.

    """
    summary = "Open an interactive shell with a pyramid app loaded"

    min_args = 2
    max_args = 2
    group_name = 'pyramid'

    parser = Command.standard_parser(simulate=True)
    parser.add_option('-d', '--disable-ipython',
                      action='store_true',
                      dest='disable_ipython',
                      help="Don't use IPython even if it is available")

    interact = (interact,) # for testing
    loadapp = (loadapp,) # for testing
    get_app = staticmethod(get_app) # hook point
    get_root = staticmethod(get_root) # hook point
    verbose = 3

    def __init__(self, *arg, **kw):
        # needs to be in constructor to support Jython (used to be at class
        # scope as ``usage = '\n' + __doc__``.
        self.usage = '\n' + self.__doc__
        Command.__init__(self, *arg, **kw)

    def command(self, IPShell=_marker):
        if IPShell is _marker:
            try: #pragma no cover
                from IPython.Shell import IPShell
            except ImportError: #pragma no cover
                IPShell = None
        cprt =('Type "help" for more information. "root" is the Pyramid app '
               'root object.')
        banner = "Python %s on %s\n%s" % (sys.version, sys.platform, cprt)
        config_file, section_name = self.args
        self.logging_file_config(config_file)
        app = self.get_app(config_file, section_name, loadapp=self.loadapp[0])
        root, closer = self.get_root(app)
        if IPShell is not None and not self.options.disable_ipython:
            try:
                shell = IPShell(argv=[], user_ns={'root':root})
                shell.IP.BANNER = shell.IP.BANNER + '\n\n' + banner
                shell.mainloop()
            finally:
                closer()
        else:
            try:
                self.interact[0](banner, local={'root':root})
            finally:
                closer()

BFGShellCommand = PShellCommand # b/w compat forever
