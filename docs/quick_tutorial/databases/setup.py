from setuptools import setup

requires = [
    'deform',
    'pyramid',
    'pyramid_chameleon',
    'pyramid_tm',
    'sqlalchemy',
    'waitress',
    'zope.sqlalchemy',
]

setup(name='tutorial',
      install_requires=requires,
      entry_points="""\
      [paste.app_factory]
      main = tutorial:main
      [console_scripts]
      initialize_tutorial_db = tutorial.initialize_db:main
      """,
)
