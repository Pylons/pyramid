.. _wiki_distributing_your_application:

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

The output of such a command will be something like:

.. code-block:: text

    * Creating venv isolated environment...
    * Installing packages in isolated environment... (setuptools)
    * Getting build dependencies for sdist...
    ...
    removing build/bdist.linux-x86_64/wheel
    Successfully built tutorial-0.0.tar.gz and tutorial-0.0-py3-none-any.whl

This command creates a subdirectory named ``dist``.
Inside that is a tarball named ``tutorial-0.0.tar.gz`` (the source :term:`distribution` of your application), as well ass ``tutorial-0.0-py3-none-any.whl`` (the binary :term:`distribution`).
You can send these files to your friends to show them your cool new application.
They should be able to install the app by pointing the ``pip install`` command directly at one of them.
These artifacts are also uploadable to `PyPI <https://pypi.org/>`_, or another package index, using a tool like ``twine``.

Note that the config files, such as ``production.ini`` are not part of the distribution.
These files are considered to be defined by the "user" of your application and not part of the application itself.
If you'd like to help a user out, consider defining a new CLI script similar to ``initialize_tutorial_db`` that can render a config file for them!

Please learn more about distributing an application from the `Python Packaging User Guide <https://packaging.python.org/en/latest/tutorials/packaging-projects/>`_.
