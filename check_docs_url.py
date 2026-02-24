#!/usr/bin/env python
"""
Check that the docs url in the pyproject.toml
matches the version number.
"""
import sys
import tomllib

pyproj = tomllib.load(open("pyproject.toml", 'rb'))

VERSION = pyproj['project']['version']

# code from old setup.py

branch_version = ".".join(VERSION.split(".")[:2])

# black is refusing to make anything under 80 chars so just splitting it up
docs_fmt = 'https://docs.pylonsproject.org/projects/pyramid/en/{}-branch/'
correct_docs_url = docs_fmt.format(branch_version)

docs_url = pyproj['project']['urls']['Documentation']

if docs_url == correct_docs_url:
    print("Documentation url looks good")
    sys.exit(0)
else:
    print("Something wrng with the Documentation url.")
    print(f"It is:        {docs_url}")
    print(f"It should be: {correct_docs_url}")
    sys.exit(1)

