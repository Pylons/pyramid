from setuptools import setup

requires = [
    'deform',
    'pyramid',
    'pyramid_chameleon',
    'pyramid_debugtoolbar',
    'pyramid_tm',
    'sqlalchemy',
    'waitress',
    'zope.sqlalchemy',
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
      [console_scripts]
      initialize_tutorial_db = tutorial.initialize_db:main
      """,
      )
