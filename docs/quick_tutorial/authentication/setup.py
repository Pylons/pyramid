from setuptools import setup

requires = [
    'bcrypt',
    'pyramid_chameleon',
    'waitress',
]

tests_require = [
    'pyramid[testing]'
]

setup(name='tutorial',
      install_requires=requires,
      extras_require={
          'testing': tests_require,
      },
      entry_points="""\
      [paste.app_factory]
      main = tutorial:main
      """,
)
