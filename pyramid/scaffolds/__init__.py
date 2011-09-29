import binascii
import os

from pyramid.compat import (
    print_,
    native_
    )

from glue.template import Template

class PyramidTemplate(Template):
    def pre(self, command, output_dir, vars):
        vars['random_string'] = native_(binascii.hexlify(os.urandom(20)))
        package_logger = vars['package']
        if package_logger == 'root':
            # Rename the app logger in the rare case a project is named 'root'
            package_logger = 'app'
        vars['package_logger'] = package_logger
        return Template.pre(self, command, output_dir, vars)

    def post(self, command, output_dir, vars):
        self.out('Welcome to Pyramid.  Sorry for the convenience.')
        return Template.post(self, command, output_dir, vars)

    def out(self, msg): # pragma: no cover (replaceable testing hook)
        print_(msg)

class StarterProjectTemplate(PyramidTemplate):
    _template_dir = 'starter'
    summary = 'pyramid starter project'

class ZODBProjectTemplate(PyramidTemplate):
    _template_dir = 'zodb'
    summary = 'pyramid ZODB starter project'

class RoutesAlchemyProjectTemplate(PyramidTemplate):
    _template_dir = 'routesalchemy'
    summary = 'pyramid SQLAlchemy project using url dispatch (no traversal)'

class AlchemyProjectTemplate(PyramidTemplate):
    _template_dir = 'alchemy'
    summary = 'pyramid SQLAlchemy project using traversal'

