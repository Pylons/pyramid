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
import platform
import sys

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
try:
    README = open(os.path.join(here, 'README.rst')).read()
    CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()
except IOError:
    README = CHANGES = ''

install_requires=[
    'Chameleon >= 1.2.3',
    'Mako >= 0.3.6', # strict_undefined
    'Paste > 1.7', # temp version pin to prevent PyPi install failure :-(
    'PasteDeploy',
    'PasteScript >= 1.7.4', # "here" in logging fileConfig
    'WebOb >= 1.0.2', # no "default_charset"; request.script_name doesnt error
    'repoze.lru',
    'setuptools',
    'zope.component >= 3.6.0', # independent of zope.hookable
    'zope.interface >= 3.5.1',   # 3.5.0 comment: "allow to bootstrap on jython"
    'zope.deprecation',
    'venusian >= 1.0a1', # ``onerror``
    'translationstring',
    ]

if platform.system() == 'Java':
    tests_require = install_requires + [
        'WebTest',
        'virtualenv',
        ]
else:
    tests_require= install_requires + [
        'Sphinx',
        'docutils',
        'repoze.sphinx.autointerface',
        'WebTest', 
        'virtualenv',
        ]

if sys.version_info[:2] < (2, 6):
    install_requires.append('simplejson')
    
setup(name='pyramid',
      version='1.2.7',
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
        [paste.server_runner]
        wsgiref = pyramid.paster:wsgiref_server_runner
        cherrypy = pyramid.paster:cherrypy_server_runner
      """
      )

