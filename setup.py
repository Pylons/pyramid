##############################################################################
#
# Copyright (c) 2008-2013 Agendaless Consulting and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the BSD-like license at
# http://www.repoze.org/LICENSE.txt.  A copy of the license should accompany
# this distribution.  THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL
# EXPRESS OR IMPLIED WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND
# FITNESS FOR A PARTICULAR PURPOSE
#
##############################################################################

import os
import sys

from setuptools import setup, find_packages

py_version = sys.version_info[:2]
is_pypy = '__pypy__' in sys.builtin_module_names

PY3 = py_version[0] == 3

if PY3:
    if py_version < (3, 3) and not is_pypy: # PyPy3 masquerades as Python 3.2...
        raise RuntimeError('On Python 3, Pyramid requires Python 3.3 or better')
else:
    if py_version < (2, 6):
        raise RuntimeError('On Python 2, Pyramid requires Python 2.6 or better')

here = os.path.abspath(os.path.dirname(__file__))
try:
    with open(os.path.join(here, 'README.rst')) as f:
        README = f.read()
    with open(os.path.join(here, 'CHANGES.txt')) as f:
        CHANGES = f.read()
except IOError:
    README = CHANGES = ''

install_requires = [
    'setuptools',
    'WebOb >= 1.3.1', # request.domain and CookieProfile
    'repoze.lru >= 0.4', # py3 compat
    'zope.interface >= 3.8.0',  # has zope.interface.registry
    'zope.deprecation >= 3.5.0', # py3 compat
    'venusian >= 1.0a3', # ``ignore``
    'translationstring >= 0.4', # py3 compat
    'PasteDeploy >= 1.5.0', # py3 compat
    ]

tests_require = [
    'WebTest >= 1.3.1', # py3 compat
    ]

if not PY3:
    tests_require.append('zope.component>=3.11.0')

docs_extras = [
    'Sphinx >= 1.3.5',
    'docutils',
    'repoze.sphinx.autointerface',
    'pylons_sphinx_latesturl',
    'pylons-sphinx-themes',
    'sphinxcontrib-programoutput',
    ]

testing_extras = tests_require + [
    'nose',
    'coverage',
    'virtualenv', # for scaffolding tests
    ]

setup(name='pyramid',
      version='1.7',
      description='The Pyramid Web Framework, a Pylons project',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
          "Development Status :: 6 - Mature",
          "Intended Audience :: Developers",
          "Programming Language :: Python",
          "Programming Language :: Python :: 2.7",
          "Programming Language :: Python :: 3",
          "Programming Language :: Python :: 3.3",
          "Programming Language :: Python :: 3.4",
          "Programming Language :: Python :: 3.5",
          "Programming Language :: Python :: Implementation :: CPython",
          "Programming Language :: Python :: Implementation :: PyPy",
          "Framework :: Pyramid",
          "Topic :: Internet :: WWW/HTTP",
          "Topic :: Internet :: WWW/HTTP :: WSGI",
          "License :: Repoze Public License",
      ],
      keywords='web wsgi pylons pyramid',
      author="Chris McDonough, Agendaless Consulting",
      author_email="pylons-discuss@googlegroups.com",
      url="https://trypyramid.com",
      license="BSD-derived (http://www.repoze.org/LICENSE.txt)",
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=install_requires,
      extras_require={
          'testing': testing_extras,
          'docs': docs_extras,
          },
      tests_require=tests_require,
      test_suite="pyramid.tests",
      entry_points="""\
        [pyramid.scaffold]
        starter=pyramid.scaffolds:StarterProjectTemplate
        zodb=pyramid.scaffolds:ZODBProjectTemplate
        alchemy=pyramid.scaffolds:AlchemyProjectTemplate
        [pyramid.pshell_runner]
        python=pyramid.scripts.pshell:python_shell_runner
        [console_scripts]
        pcreate = pyramid.scripts.pcreate:main
        pserve = pyramid.scripts.pserve:main
        pshell = pyramid.scripts.pshell:main
        proutes = pyramid.scripts.proutes:main
        pviews = pyramid.scripts.pviews:main
        ptweens = pyramid.scripts.ptweens:main
        prequest = pyramid.scripts.prequest:main
        pdistreport = pyramid.scripts.pdistreport:main
        [paste.server_runner]
        wsgiref = pyramid.scripts.pserve:wsgiref_server_runner
        cherrypy = pyramid.scripts.pserve:cherrypy_server_runner
      """
      )
