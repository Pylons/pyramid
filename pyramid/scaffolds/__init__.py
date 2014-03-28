import binascii
import os
import re
from textwrap import dedent

from pyramid.compat import native_

from pyramid.scaffolds.template import Template # API

class PyramidTemplate(Template):
    """
     A class that can be used as a base class for Pyramid scaffolding
     templates.
    """
    def pre(self, command, output_dir, vars):
        """ Overrides :meth:`pyramid.scaffolds.template.Template.pre`, adding
        several variables to the default variables list (including
        ``random_string``, and ``package_logger``).  It also prevents common
        misnamings (such as naming a package "site" or naming a package
        logger "root".

        package_full_path as the full path of the package/module
        package_parent_path as the parent dir path of the package/module

        If we do pcreate -s {template} -d a/b c/d/e:
            package: e
            package_full_name: c.d.e
            package_logger: e
            package_full_path: c/d/e
            package_parent_path: c/d (dirname of package_full_path)
            package_parent_name: c.d
            package_root_name: c (first in the list of package_full_name separated by .)
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

        vars['package_full_path'] = vars['package_full_name'].replace('.', os.path.sep)
        vars['package_parent_path'] = os.path.dirname(vars['package_full_path'])
        vars['package_parent_name'] = vars['package_parent_path'].replace(os.path.sep, '.')
        vars['package_root_name'] = vars['package_full_name'].split('.')[0]

        return Template.pre(self, command, output_dir, vars)

    def post(self, command, output_dir, vars): # pragma: no cover
        """ Overrides :meth:`pyramid.scaffolds.template.Template.post`, to
        print "Welcome to Pyramid.  Sorry for the convenience." after a
        successful scaffolding rendering."""

        separator = "=" * 79
        msg = dedent(
            """
            %(separator)s
            Tutorials: http://docs.pylonsproject.org/projects/pyramid_tutorials
            Documentation: http://docs.pylonsproject.org/projects/pyramid

            Twitter (tips & updates): http://twitter.com/pylons
            Mailing List: http://groups.google.com/group/pylons-discuss

            Welcome to Pyramid.  Sorry for the convenience.
            %(separator)s
        """ % {'separator': separator})

        self.out(msg)
        return Template.post(self, command, output_dir, vars)

    def out(self, msg): # pragma: no cover (replaceable testing hook)
        print(msg)

class StarterProjectTemplate(PyramidTemplate):
    _template_dir = 'starter'
    summary = 'Pyramid starter project'

class ZODBProjectTemplate(PyramidTemplate):
    _template_dir = 'zodb'
    summary = 'Pyramid ZODB project using traversal'

class AlchemyProjectTemplate(PyramidTemplate):
    _template_dir = 'alchemy'
    summary = 'Pyramid SQLAlchemy project using url dispatch'

class SimpleModuleTemplate(PyramidTemplate):
    _template_dir = 'simple_module'
    summary = 'Pyramid simple module'

class SimplePkgTemplate(PyramidTemplate):
    _template_dir = 'simple_pkg'
    summary = 'Pyramid simple pkg'
