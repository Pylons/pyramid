from setuptools import setup

requires = [
    'pyramid',
    'pyramid_debugtoolbar',
    'waitress',
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
