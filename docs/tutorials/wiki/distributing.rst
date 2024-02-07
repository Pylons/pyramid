.. _wiki_distributing_your_application:

=============================
Distributing Your Application
=============================

Once your application works properly, you can create a :term:`distribution` from it by using the PyPA ``build`` command.
The following commands assume your current working directory contains the ``tutorial`` package and its ``pyproject.toml`` file.

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
Or you can upload them to `PyPI <https://pypi.org/>`_ and share them with the rest of the world, where it can be downloaded via ``pip install`` remotely like any other package people download from PyPI.
