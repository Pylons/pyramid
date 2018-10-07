from setuptools import setup

requires = [
    'bcrypt',
    'pyramid',
    'pyramid_chameleon',
    'pyramid_debugtoolbar',
    'waitress',
]

tests_require = [
    'pyramid[testing]'
]

setup(name='tutorial',
      install_requires=requires,
      extras_require={
          'test': [
              'pytest',
              'webtest',
          ],
      },
      entry_points="""\
      [paste.app_factory]
      main = tutorial:main
      """,
      )
