from setuptools import setup

requires = [
    'bcrypt',
    'pyramid[testing]',
    'pyramid_chameleon',
    'waitress',
]


setup(name='tutorial',
      install_requires=requires,
      entry_points="""\
      [paste.app_factory]
      main = tutorial:main
      """,
)
