import optparse
import os
import pkg_resources
import re
import sys

_bad_chars_re = re.compile('[^a-zA-Z0-9_]')

def main(argv=sys.argv):
    command = CreateCommand(argv)
    return command.run()

class CreateCommand(object):
    verbose = True
    interactive = False
    simulate = False
    usage = "usage: %prog [options] project"
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

    def __init__(self, argv):
        self.options, self.args = self.parser.parse_args(argv[1:])
        self.scaffolds = all_scaffolds()
        self.available_scaffoldnames = [x.name for x in self.scaffolds]

    def run(self):
        if self.options.list:
            return self.show_scaffolds()
        if not self.options.scaffold_name:
            print('You must provide at least one scaffold name')
            return
        if not self.args:
            print('You must provide a project name')
            return
        diff = set(self.options.scaffold_name).difference(
            self.available_scaffoldnames)
        if diff:
            print('Unavailable scaffolds: %s' % list(diff))
        self.render_scaffolds()

    def render_scaffolds(self):
        options = self.options
        args = self.args
        dist_name = args[0].lstrip(os.path.sep)
        output_dir = os.path.normpath(os.path.join(os.getcwd(), dist_name))
        pkg_name = _bad_chars_re.sub('', dist_name.lower())
        safe_name = pkg_resources.safe_name(dist_name)
        egg_name = pkg_resources.to_filename(safe_name),
        vars = {
            'project': dist_name,
            'package': pkg_name,
            'egg': egg_name,
            }
        for scaffold_name in options.scaffold_name:
            for scaffold in self.scaffolds:
                if scaffold.name == scaffold_name:
                    scaffold.run(self, output_dir, vars)

    def show_scaffolds(self):
        scaffolds = list(self.scaffolds)
        max_name = max([len(t.name) for t in scaffolds])
        scaffolds.sort(key=lambda x: x.name)
        print('Available scaffolds:')
        for scaffold in scaffolds:
            print('  %s:%s  %s' % (
                scaffold.name,
                ' '*(max_name-len(scaffold.name)), scaffold.summary))


def all_scaffolds():
    scaffolds = []
    eps = list(pkg_resources.iter_entry_points('pyramid.scaffold'))
    for entry in eps:
        try:
            scaffold_class = entry.load()
            scaffold = scaffold_class(entry.name)
            scaffolds.append(scaffold)
        except Exception as e:
            print('Warning: could not load entry point %s (%s: %s)' % (
                entry.name, e.__class__.__name__, e))
    return scaffolds

