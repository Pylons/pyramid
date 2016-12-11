import sys
import platform
import pkg_resources
import argparse
from operator import itemgetter

def out(*args): # pragma: no cover
    for arg in args:
        sys.stdout.write(arg)
        sys.stdout.write(' ')
    sys.stdout.write('\n')

def get_parser():
    parser = argparse.ArgumentParser(
        description="Show Python distribution versions and locations in use")
    return parser

def main(argv=sys.argv, pkg_resources=pkg_resources, platform=platform.platform,
         out=out):
    # all args except argv are for unit testing purposes only
    parser = get_parser()
    parser.parse_args(argv[1:])
    packages = []
    for distribution in pkg_resources.working_set:
        name = distribution.project_name
        packages.append(
            {'version': distribution.version,
             'lowername': name.lower(),
             'name': name,
             'location':distribution.location}
            )
    packages = sorted(packages, key=itemgetter('lowername'))
    pyramid_version = pkg_resources.get_distribution('pyramid').version
    plat = platform()
    out('Pyramid version:', pyramid_version)
    out('Platform:', plat)
    out('Packages:')
    for package in packages:
        out(' ', package['name'], package['version'])
        out('   ', package['location'])

if __name__ == '__main__': # pragma: no cover
    sys.exit(main() or 0)
