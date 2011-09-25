##############################################################################
#
# Copyright (c) 2008-2011 Agendaless Consulting and Contributors.
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

if sys.version_info[:2] < (2, 6):
    raise RuntimeError('Requires Python 2.6 or better')

PY3 = sys.version_info[0] == 3

here = os.path.abspath(os.path.dirname(__file__))
try:
    README = open(os.path.join(here, 'README.rst')).read()
    CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()
except IOError:
    README = CHANGES = ''

install_requires=[
    'setuptools',
    'Chameleon >= 1.2.3',
    'Mako >= 0.3.6', # strict_undefined
    'WebOb >= 1.2dev', # response.text / py3 compat
    'repoze.lru >= 0.4', # py3 compat
    'zope.interface >= 3.8.0',  # has zope.interface.registry
    'zope.deprecation >= 3.5.0', # py3 compat
    'venusian >= 1.0a1', # ``onerror``
    'translationstring >= 0.4', # py3 compat
    ]

if not PY3:
    install_requires.extend([
        'Paste > 1.7', # temp version pin to prevent PyPi install failure :-(
        'PasteDeploy',
        'PasteScript >= 1.7.4', # "here" in logging fileConfig
        ])

tests_require = install_requires + [
    'WebTest >= 1.3.1', # py3 compat
    'virtualenv',
    ]

if not PY3:
    tests_require.extend([
        'Sphinx',
        'docutils',
        'repoze.sphinx.autointerface',
        'zope.component>=3.11.0',
        ])

setup(name='pyramid',
      version='1.2',
      description=('The Pyramid web application development framework, a '
                   'Pylons project'),
      long_description=README + '\n\n' +  CHANGES,
      classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Framework :: Pylons",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI",
        "License :: Repoze Public License",
        ],
      keywords='web wsgi pylons pyramid',
      author="Chris McDonough, Agendaless Consulting",
      author_email="pylons-devel@googlegroups.com",
      url="http://pylonsproject.org",
      license="BSD-derived (http://www.repoze.org/LICENSE.txt)",
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires = install_requires,
      tests_require = tests_require,
      test_suite="pyramid.tests",
      entry_points = """\
        [paste.paster_create_template]
        pyramid_starter=pyramid.scaffolds:StarterProjectTemplate
        pyramid_zodb=pyramid.scaffolds:ZODBProjectTemplate
        pyramid_routesalchemy=pyramid.scaffolds:RoutesAlchemyProjectTemplate
        pyramid_alchemy=pyramid.scaffolds:AlchemyProjectTemplate
        [paste.paster_command]
        pshell=pyramid.paster:PShellCommand
        proutes=pyramid.paster:PRoutesCommand
        pviews=pyramid.paster:PViewsCommand
        ptweens=pyramid.paster:PTweensCommand
        [console_scripts]
        bfg2pyramid = pyramid.fixers.fix_bfg_imports:main
      """
      )

