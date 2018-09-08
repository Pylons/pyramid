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
from setuptools import find_packages, setup


def readfile(name):
    with open(name) as f:
        return f.read()


README = readfile('README.rst')
CHANGES = readfile('CHANGES.rst')
# instaling
install_requires = [
    'hupper',
    'plaster',
    'plaster_pastedeploy',
    'setuptools',
    'translationstring >= 0.4',  # py3 compat
    'venusian >= 1.0',  # ``ignore``
    'webob >= 1.8.2',  # cookies.make_cookie allows non-bytes samesite
    'zope.deprecation >= 3.5.0',  # py3 compat
    'zope.interface >= 3.8.0',  # has zope.interface.registry
]
# testing
tests_require = [
    'webtest >= 1.3.1',  # py3 compat
    'zope.component >= 4.0',  # py3 compat
]


docs_extras = [
    'Sphinx >= 1.7.4',
    'docutils',
    'pylons-sphinx-themes',
    'pylons_sphinx_latesturl',
    'repoze.sphinx.autointerface',
    'sphinxcontrib-autoprogram',
]

testing_extras = tests_require + [
    'coverage',
    'nose',
    'virtualenv',  # for scaffolding tests
]

setup(name='pyramid',
      version='1.10.dev0',
      description='The Pyramid Web Framework, a Pylons project',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
          "Development Status :: 6 - Mature",
          "Intended Audience :: Developers",
          "Programming Language :: Python",
          "Programming Language :: Python :: 2.7",
          "Programming Language :: Python :: 3",
          "Programming Language :: Python :: 3.4",
          "Programming Language :: Python :: 3.5",
          "Programming Language :: Python :: 3.6",
          "Programming Language :: Python :: 3.7",
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
      python_requires='>=2.7,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*',
      install_requires=install_requires,
      extras_require={
          ':python_version<"3.2"': ['repoze.lru >= 0.4'],
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
