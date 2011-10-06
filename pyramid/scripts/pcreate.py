# (c) 2005 Ian Bicking and contributors; written for Paste
# (http://pythonpaste.org) Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license.php

import optparse
import os
import pkg_resources
import re
import sys

_bad_chars_re = re.compile('[^a-zA-Z0-9_]')

def main(argv=sys.argv):
    command = PCreateCommand(argv)
    return command.run()

class PCreateCommand(object):
    verbose = True
    interactive = False
    simulate = False
    usage = "usage: %prog [options] distribution_name"
    parser = optparse.OptionParser(usage)
    parser.add_option('-s', '--scaffold',
                      dest='scaffold_name',
                      action='append',
                      help=("Add a scaffold to the create process "
                            "(multiple -s args accepted)"))
    parser.add_option('-l', '--list',
                      dest='list',
                      action='store_true',
                      help="List all available scaffold names")
    parser.add_option('--simulate',
                      dest='simulate',
                      action='store_true',
                      help='Simulate but do no work')
    parser.add_option('--overwrite',
                      dest='overwrite',
                      action='store_true',
                      help='Always overwrite')
    parser.add_option('-q', '--quiet',
                      dest='quiet',
                      action='store_true',
                      help='Dont emit any output')

    def __init__(self, argv):
        self.options, self.args = self.parser.parse_args(argv[1:])
        self.scaffolds = self.all_scaffolds()

    def run(self):
        if self.options.list:
            return self.show_scaffolds()
        if not self.options.scaffold_name:
            self.out('You must provide at least one scaffold name')
            return
        if not self.args:
            self.out('You must provide a project name')
            return
        available = [x.name for x in self.scaffolds]
        diff = set(self.options.scaffold_name).difference(available)
        if diff:
            self.out('Unavailable scaffolds: %s' % list(diff))
            return
        return self.render_scaffolds()

    def render_scaffolds(self):
        options = self.options
        args = self.args
        project_name = args[0].lstrip(os.path.sep)
        output_dir = os.path.normpath(os.path.join(os.getcwd(), project_name))
        pkg_name = _bad_chars_re.sub('', project_name.lower())
        safe_name = pkg_resources.safe_name(project_name)
        egg_name = pkg_resources.to_filename(safe_name)
        vars = {
            'project': project_name,
            'package': pkg_name,
            'egg': egg_name,
            }
        for scaffold_name in options.scaffold_name:
            for scaffold in self.scaffolds:
                if scaffold.name == scaffold_name:
                    scaffold.run(self, output_dir, vars)
        return True

    def show_scaffolds(self):
        scaffolds = sorted(self.scaffolds, key=lambda x: x.name)
        if scaffolds:
            max_name = max([len(t.name) for t in scaffolds])
            self.out('Available scaffolds:')
            for scaffold in scaffolds:
                self.out('  %s:%s  %s' % (
                    scaffold.name,
                    ' '*(max_name-len(scaffold.name)), scaffold.summary))
        else:
            self.out('No scaffolds available')
        return True

    def all_scaffolds(self):
        scaffolds = []
        eps = list(pkg_resources.iter_entry_points('pyramid.scaffold'))
        for entry in eps:
            try:
                scaffold_class = entry.load()
                scaffold = scaffold_class(entry.name)
                scaffolds.append(scaffold)
            except Exception as e: # pragma: no cover
                self.out('Warning: could not load entry point %s (%s: %s)' % (
                    entry.name, e.__class__.__name__, e))
        return scaffolds

    def out(self, msg): # pragma: no cover
        if not self.options.quiet:
            print(msg)


