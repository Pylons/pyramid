import argparse
import importlib.metadata
from operator import itemgetter
import platform
import sys


def out(*args):  # pragma: no cover
    for arg in args:
        sys.stdout.write(arg)
        sys.stdout.write(' ')
    sys.stdout.write('\n')


def get_parser():
    parser = argparse.ArgumentParser(
        description="Show Python distribution versions and locations in use"
    )
    return parser


def main(
    argv=sys.argv,
    importlib_metadata=importlib.metadata,
    platform=platform.platform,
    out=out,
):
    # all args except argv are for unit testing purposes only
    parser = get_parser()
    parser.parse_args(argv[1:])
    packages = []
    for distribution in importlib_metadata.distributions():
        name = distribution.metadata['Name']
        packages.append(
            {
                'version': distribution.version,
                'lowername': name.lower(),
                'name': name,
                'summary': distribution.metadata.get('Summary'),
            }
        )
    packages = sorted(packages, key=itemgetter('lowername'))
    pyramid_version = importlib_metadata.distribution('pyramid').version
    plat = platform()
    out('Pyramid version:', pyramid_version)
    out('Platform:', plat)
    out('Packages:')
    for package in packages:
        out(' ', package['name'], package['version'])
        out('   ', package['summary'])


if __name__ == '__main__':  # pragma: no cover
    sys.exit(main() or 0)
