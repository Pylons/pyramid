from setuptools import setup

requires = [
    'pyramid',
    'pyramid_chameleon',
    'pyramid_debugtoolbar',
    'pyramid_jinja2',
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
