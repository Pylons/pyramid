import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'pyramid',
    'repoze.zodbconn',
    'repoze.tm2>=1.0b1', # default_commit_veto
    'repoze.retry',
    'ZODB3',
    'WebError',
    'docutils',
    ]

setup(name='tutorial',
      version='0.0',
      description='tutorial',
      long_description=README + '\n\n' +  CHANGES,
      classifiers=[
        "Intended Audience :: Developers",
        "Framework :: Pylons",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='',
      author_email='',
      url='',
      keywords='web pylons pyramid',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      tests_require=requires,
      test_suite="tutorial",
      entry_points = """\
      [paste.app_factory]
      main = tutorial:main
      """,
      paster_plugins=['pyramid'],
      )

