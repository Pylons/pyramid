# (c) 2005 Ian Bicking and contributors; written for Paste
# (http://pythonpaste.org) Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license.php

import argparse
import os
import os.path
import pkg_resources
import re
import sys
from pyramid.compat import input_

_bad_chars_re = re.compile('[^a-zA-Z0-9_]')


def main(argv=sys.argv, quiet=False):
    command = PCreateCommand(argv, quiet)
    try:
        return command.run()
    except KeyboardInterrupt:  # pragma: no cover
        return 1


class PCreateCommand(object):
    verbosity = 1  # required
    parser = argparse.ArgumentParser(
        description="""\
Render Pyramid scaffolding to an output directory.

Note: As of Pyramid 1.8, this command is deprecated. Use a specific
cookiecutter instead:
https://github.com/Pylons/?q=cookiecutter
""",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument('-s', '--scaffold',
                        dest='scaffold_name',
                        action='append',
                        help=("Add a scaffold to the create process "
                              "(multiple -s args accepted)"))
    parser.add_argument('-t', '--template',
                        dest='scaffold_name',
                        action='append',
                        help=('A backwards compatibility alias for '
                              '-s/--scaffold.  Add a scaffold to the '
                              'create process (multiple -t args accepted)'))
    parser.add_argument('-l', '--list',
                        dest='list',
                        action='store_true',
                        help="List all available scaffold names")
    parser.add_argument('--list-templates',
                        dest='list',
                        action='store_true',
                        help=("A backwards compatibility alias for -l/--list. "
                              "List all available scaffold names."))
    parser.add_argument('--package-name',
                        dest='package_name',
                        action='store',
                        help='Package name to use. The name provided is '
                             'assumed to be a valid Python package name, and '
                             'will not be validated. By default the package '
                             'name is derived from the value of '
                             'output_directory.')
    parser.add_argument('--simulate',
                        dest='simulate',
                        action='store_true',
                        help='Simulate but do no work')
    parser.add_argument('--overwrite',
                        dest='overwrite',
                        action='store_true',
                        help='Always overwrite')
    parser.add_argument('--interactive',
                        dest='interactive',
                        action='store_true',
                        help='When a file would be overwritten, interrogate '
                             '(this is the default, but you may specify it to '
                             'override --overwrite)')
    parser.add_argument('--ignore-conflicting-name',
                        dest='force_bad_name',
                        action='store_true',
                        default=False,
                        help='Do create a project even if the chosen name '
                             'is the name of an already existing / importable '
                             'package.')
    parser.add_argument('output_directory',
                        nargs='?',
                        default=None,
                        help='The directory where the project will be '
                             'created.')

    pyramid_dist = pkg_resources.get_distribution("pyramid")

    def __init__(self, argv, quiet=False):
        self.quiet = quiet
        self.args = self.parser.parse_args(argv[1:])
        if not self.args.interactive and not self.args.overwrite:
            self.args.interactive = True
        self.scaffolds = self.all_scaffolds()

    def run(self):
        if self.args.list:
            return self.show_scaffolds()
        if not self.args.scaffold_name and not self.args.output_directory:
            if not self.quiet:  # pragma: no cover
                self.parser.print_help()
                self.out('')
                self.show_scaffolds()
            return 2

        if not self.validate_input():
            return 2
        self._warn_pcreate_deprecated()

        return self.render_scaffolds()

    @property
    def output_path(self):
        return os.path.abspath(os.path.normpath(self.args.output_directory))

    @property
    def project_vars(self):
        output_dir = self.output_path
        project_name = os.path.basename(os.path.split(output_dir)[1])
        if self.args.package_name is None:
            pkg_name = _bad_chars_re.sub(
                '', project_name.lower().replace('-', '_'))
            safe_name = pkg_resources.safe_name(project_name)
        else:
            pkg_name = self.args.package_name
            safe_name = pkg_name
        egg_name = pkg_resources.to_filename(safe_name)

        # get pyramid package version
        pyramid_version = self.pyramid_dist.version

        # map pyramid package version of the documentation branch ##
        # if version ends with 'dev' then docs version is 'master'
        if self.pyramid_dist.version[-3:] == 'dev':
            pyramid_docs_branch = 'master'
        else:
            # if not version is not 'dev' find the version.major_version string
            # and combine it with '-branch'
            version_match = re.match(r'(\d+\.\d+)', self.pyramid_dist.version)
            if version_match is not None:
                pyramid_docs_branch = "%s-branch" % version_match.group()
            # if can not parse the version then default to 'latest'
            else:
                pyramid_docs_branch = 'latest'

        return {
            'project': project_name,
            'package': pkg_name,
            'egg': egg_name,
            'pyramid_version': pyramid_version,
            'pyramid_docs_branch': pyramid_docs_branch,
        }

    def render_scaffolds(self):
        props = self.project_vars
        output_dir = self.output_path
        for scaffold_name in self.args.scaffold_name:
            for scaffold in self.scaffolds:
                if scaffold.name == scaffold_name:
                    scaffold.run(self, output_dir, props)
        return 0

    def show_scaffolds(self):
        scaffolds = sorted(self.scaffolds, key=lambda x: x.name)
        if scaffolds:
            max_name = max([len(t.name) for t in scaffolds])
            self.out('Available scaffolds:')
            for scaffold in scaffolds:
                self.out('  %s:%s  %s' % (
                    scaffold.name,
                    ' ' * (max_name - len(scaffold.name)), scaffold.summary))
        else:
            self.out('No scaffolds available')
        return 0

    def all_scaffolds(self):
        scaffolds = []
        eps = list(pkg_resources.iter_entry_points('pyramid.scaffold'))
        for entry in eps:
            try:
                scaffold_class = entry.load()
                scaffold = scaffold_class(entry.name)
                scaffolds.append(scaffold)
            except Exception as e:  # pragma: no cover
                self.out('Warning: could not load entry point %s (%s: %s)' % (
                    entry.name, e.__class__.__name__, e))
        return scaffolds

    def out(self, msg):  # pragma: no cover
        if not self.quiet:
            print(msg)

    def validate_input(self):
        if not self.args.scaffold_name:
            self.out('You must provide at least one scaffold name: '
                     '-s <scaffold name>')
            self.out('')
            self.show_scaffolds()
            return False
        if not self.args.output_directory:
            self.out('You must provide a project name')
            return False
        available = [x.name for x in self.scaffolds]
        diff = set(self.args.scaffold_name).difference(available)
        if diff:
            self.out('Unavailable scaffolds: %s' % ", ".join(sorted(diff)))
            return False

        pkg_name = self.project_vars['package']

        if pkg_name == 'site' and not self.args.force_bad_name:
            self.out('The package name "site" has a special meaning in '
                     'Python. Are you sure you want to use it as your '
                     'project\'s name?')
            return self.confirm_bad_name('Really use "{0}"?: '.format(
                pkg_name))

        # check if pkg_name can be imported (i.e. already exists in current
        # $PYTHON_PATH, if so - let the user confirm
        pkg_exists = True
        try:
            # use absolute imports
            __import__(pkg_name, globals(), locals(), [], 0)
        except ImportError as error:
            pkg_exists = False
        if not pkg_exists:
            return True

        if self.args.force_bad_name:
            return True
        self.out('A package named "{0}" already exists, are you sure you want '
                 'to use it as your project\'s name?'.format(pkg_name))
        return self.confirm_bad_name('Really use "{0}"?: '.format(pkg_name))

    def confirm_bad_name(self, prompt):  # pragma: no cover
        answer = input_('{0} [y|N]: '.format(prompt))
        return answer.strip().lower() == 'y'

    def _warn_pcreate_deprecated(self):
        self.out('''\
Note: As of Pyramid 1.8, this command is deprecated. Use a specific
cookiecutter instead:
https://github.com/pylons/?query=cookiecutter
''')

if __name__ == '__main__':  # pragma: no cover
    sys.exit(main() or 0)
