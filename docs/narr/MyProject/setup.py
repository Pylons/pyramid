"""Setup for the MyProject package.

"""
import os
from setuptools import setup, find_packages


HERE = os.path.abspath(os.path.dirname(__file__))


with open(os.path.join(HERE, 'README.txt')) as fp:
    README = fp.read()


with open(os.path.join(HERE, 'CHANGES.txt')) as fp:
    CHANGES = fp.read()


REQUIRES = [
    'pyramid',
    'pyramid_chameleon',
    'pyramid_debugtoolbar',
    'waitress',
    ]

TESTS_REQUIRE = [
    'webtest'
    ]

setup(name='MyProject',
      version='0.0',
      description='MyProject',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
          'Programming Language :: Python',
          'Framework :: Pyramid',
          'Topic :: Internet :: WWW/HTTP',
          'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
      ],
      author='',
      author_email='',
      url='',
      keywords='web pyramid pylons',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=REQUIRES,
      tests_require=TESTS_REQUIRE,
      test_suite='myproject',
      entry_points="""\
      [paste.app_factory]
      main = myproject:main
      """)
