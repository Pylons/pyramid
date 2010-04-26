##############################################################################
#
# Copyright (c) 2008-2010 Agendaless Consulting and Contributors.
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

__version__ = '1.3a1'

import os
import sys

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
try:
    README = open(os.path.join(here, 'README.txt')).read()
    CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()
except IOError:
    README = CHANGES = ''

install_requires=[
    'Chameleon >= 1.2.3',
    'Paste > 1.7', # temp version pin to prevent PyPi install failure :-(
    'PasteDeploy',
    'PasteScript',
    'WebOb >= 0.9.7', # "default_charset" 
    'repoze.lru',
    'setuptools',
    'zope.component >= 3.6.0', # independent of zope.hookable
    'zope.configuration',
    'zope.deprecation',
    'zope.interface >= 3.5.1',  # 3.5.0 comment: "allow to bootstrap on jython"
    'venusian >= 0.2',
    'translationstring',
    ]

if sys.version_info[:2] < (2, 6):
    install_requires.append('simplejson')
    
setup(name='repoze.bfg',
      version=__version__,
      description='The repoze.bfg web application framework',
      long_description=README + '\n\n' +  CHANGES,
      classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Framework :: BFG",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI",
        "License :: Repoze Public License",
        ],
      keywords='web wsgi bfg',
      author="Agendaless Consulting",
      author_email="repoze-dev@lists.repoze.org",
      url="http://bfg.repoze.org",
      license="BSD-derived (http://www.repoze.org/LICENSE.txt)",
      packages=find_packages(),
      include_package_data=True,
      namespace_packages = ['repoze', 'repoze.bfg'],
      zip_safe=False,
      install_requires = install_requires,
      tests_require= install_requires + ['Sphinx', 'docutils', 'coverage',
                                         'twill'],
      test_suite="repoze.bfg.tests",
      entry_points = """\
        [paste.paster_create_template]
        bfg_starter=repoze.bfg.paster:StarterProjectTemplate
        bfg_zodb=repoze.bfg.paster:ZODBProjectTemplate
        bfg_routesalchemy=repoze.bfg.paster:RoutesAlchemyProjectTemplate
        bfg_alchemy=repoze.bfg.paster:AlchemyProjectTemplate
        [paste.paster_command]
        bfgshell=repoze.bfg.paster:BFGShellCommand
      """
      )

