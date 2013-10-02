from setuptools import setup

requires = [
    'pyramid',
    'pyramid_chameleon',
    'deform',
    'sqlalchemy',
    'pyramid_tm',
    'zope.sqlalchemy'
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