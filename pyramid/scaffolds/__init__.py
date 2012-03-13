import binascii
import os
import sys

from pyramid.compat import native_

from pyramid.scaffolds.template import Template # API

class PyramidTemplate(Template):
    """
     A class that can be used as a base class for Pyramid scaffolding
     templates.
    """
    def pre(self, command, output_dir, vars):
        """ Overrides :meth:`pyramid.scaffold.template.Template.pre`, adding
        several variables to the default variables list (including
        ``random_string``, and ``package_logger``).  It also prevents common
        misnamings (such as naming a package "site" or naming a package
        logger "root".
        """
        if vars['package'] == 'site':
            raise ValueError('Sorry, you may not name your package "site". '
                             'The package name "site" has a special meaning in '
                             'Python.  Please name it anything except "site".')
        vars['random_string'] = native_(binascii.hexlify(os.urandom(20)))
        package_logger = vars['package']
        if package_logger == 'root':
            # Rename the app logger in the rare case a project is named 'root'
            package_logger = 'app'
        vars['package_logger'] = package_logger
        return Template.pre(self, command, output_dir, vars)

    def post(self, command, output_dir, vars): # pragma: no cover
        """ Overrides :meth:`pyramid.scaffold.template.Template.post`, to
        print "Welcome to Pyramid.  Sorry for the convenience." after a
        successful scaffolding rendering."""
        self.out('Welcome to Pyramid.  Sorry for the convenience.')
        return Template.post(self, command, output_dir, vars)

    def out(self, msg): # pragma: no cover (replaceable testing hook)
        print(msg)


_DEBUGTOOLBAR_URL_FMT = ('http://docs.pylonsproject.org/projects/'
                         'pyramid_debugtoolbar/en/%(version)s/#settings')
_LOGGING_URL_FMT = ('http://docs.pylonsproject.org/projects/'
                    'pyramid/en/%(version)s/narr/logging.html')
_SETTINGS_URL_FMT = ('http://docs.pylonsproject.org/projects/'
                     'pyramid/en/%(version)s/narr/environment.html')

def _get_version(name, pkg_resources=None):
    """ Get the version of a package or None."""
    try:
        if pkg_resources is None: # pragma: no cover
            import pkg_resources
        pkg = pkg_resources.get_distribution(name)
        return pkg.parsed_version
    except (ImportError, ValueError):
        pass

def _make_pylons_link(name, pkg_resources=None):
    """ Create a link to the pyramid documentation."""
    v = _get_version(name, pkg_resources=pkg_resources)
    try:
        return '%s.%s-branch' % (int(v[0]), int(v[1]))
    except:
        return 'latest'

def _add_ini_urls(vars, pkg_resources=None):
    """ Add some basic URLs to the template vars for use in INI comments."""
    pyramid_version = _make_pylons_link('pyramid', pkg_resources=pkg_resources)
    debugtoolbar_version = 'latest'
    vars['settings_url'] = _SETTINGS_URL_FMT % {'version': pyramid_version}
    vars['logging_url'] = _LOGGING_URL_FMT % {'version': pyramid_version}
    vars['debugtoolbar_url'] = _DEBUGTOOLBAR_URL_FMT % {'version':
                                                        debugtoolbar_version}

class StarterProjectTemplate(PyramidTemplate):
    _template_dir = 'starter'
    summary = 'Pyramid starter project'

    def pre(self, command, output_dir, vars):
        _add_ini_urls(vars)
        return PyramidTemplate.pre(self, command, output_dir, vars)

class ZODBProjectTemplate(PyramidTemplate):
    _template_dir = 'zodb'
    summary = 'Pyramid ZODB project using traversal'

    def pre(self, command, output_dir, vars):
        _add_ini_urls(vars)
        return PyramidTemplate.pre(self, command, output_dir, vars)

class AlchemyProjectTemplate(PyramidTemplate):
    _template_dir = 'alchemy'
    summary = 'Pyramid SQLAlchemy project using url dispatch'

    def pre(self, command, output_dir, vars):
        _add_ini_urls(vars)
        return PyramidTemplate.pre(self, command, output_dir, vars)

    def post(self, command, output_dir, vars): # pragma: no cover
        val = PyramidTemplate.post(self, command, output_dir, vars)
        vars = vars.copy()
        vars['output_dir'] = output_dir
        vars['pybin'] = os.path.join(sys.exec_prefix, 'bin')
        self.out('')
        self.out('Please run the "populate_%(project)s" script to set up the '
                 'SQL database after\ninstalling (but before starting) the '
                 'application.\n\n For example:\n\ncd %(output_dir)s\n'
                 '%(pybin)s/python setup.py develop\n'
                 '%(pybin)s/populate_%(project)s development.ini'
                 % vars)
        return val
