from setuptools import setup

requires = [
    'pyramid',
    'pyramid_chameleon',
    'bcrypt'
]

setup(name='tutorial',
      install_requires=requires,
      entry_points="""\
      [paste.app_factory]
      main = tutorial:main
      """,
)