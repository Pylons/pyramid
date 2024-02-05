.. _wiki2_distributing_your_application:

=============================
Distributing Your Application
=============================

.. note::

    This is an optional step.
    It is not required nor expected that every application is built to be distributed to a package index.
    However, even when building personal projects, defining it as a distributable artifact can provide many advantages when it comes to optimizing your build for a Docker image or other "production" hardened environments that should not mirror your local development environment exactly.

Once your application works properly, you can create a "sdist" or "wheel" from
it by using a PEP517-compliant client tool. The following commands assume your
current working directory contains the ``tutorial`` package and the
``pyproject.toml`` file.

On Unix:

.. code-block:: bash

    $VENV/bin/pip install build
    $VENV/bin/python -m build

On Windows:

.. code-block:: doscon

    %VENV%\Scripts\pip install build
    %VENV%\Scripts\python -m build

Upon successfull completion, a "sdist" and a "wheel" will be output to the ``dist`` subdirectory.
These artifacts are uploadable to `PyPI <https://pypi.org/>`_ using a tool like ``twine``.
You should be able to create a brand new virtualenv and ``pip install`` the sdist or wheel.
Note that the ``production.ini`` is not part of the distribution.
This file is considered to be defined by the "user" of your application, not part of the application itself.
If you'd like to help a user out, consider defining a new CLI script that can render a config file for them!

Please learn more about distributing an application from the `Python Packaging User Guide <https://packaging.python.org/en/latest/tutorials/packaging-projects/>`_.
