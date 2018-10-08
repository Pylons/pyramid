from setuptools import setup

# List of dependencies installed via `pip install -e .`.
# by virtue of the Setuptools `install_requires` value below.
requires = [
    'bcrypt',
    'pyramid',
    'pyramid_chameleon',
    'pyramid_debugtoolbar',
    'waitress',
]

# List of dependencies installed via `pip install -e ".[testing]"`
# by virtue of the Setuptools `extras_require` value in the Python
# dictionary below.
tests_require = [
    'pytest',
    'webtest',
]

setup(
    name='tutorial',
    install_requires=requires,
    extras_require={
        'testing': tests_require,
    },
    entry_points={
        'paste.app_factory': [
            'main = tutorial:main'
        ],
    },
)
