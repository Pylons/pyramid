=================
Tutorial Approach
=================

This tutorial uses conventions to keep the introduction focused and concise.
Details, references, and deeper discussions are mentioned in "See also" notes.

.. seealso:: This is an example "See also" note.


Directory tree
==============

This "Getting Started" tutorial is broken into independent steps, starting with
the smallest possible "single file WSGI app" example. Each of these steps
introduces a topic and a very small set of concepts via working code. The steps
each correspond to a directory in our workspace, where each step's directory is
a Python package.

As we develop our tutorial, our directory tree will resemble the structure
below:

.. code-block:: text

    quick_tutorial
        │── env
        `── request_response
            `── tutorial
            │   │── __init__.py
            │   │── tests.py
            │   `── views.py
            │── development.ini
            `── setup.py

Each of the directories in our ``quick_tutorial`` workspace (e.g., ``request_response``) is a *Python
project* (except as noted for the ``hello_world`` step). The ``tutorial``
directory is a *Python package*.

For most steps you will copy the previous step's directory to a new directory, and change your working directory to the new directory, then install your project:

.. code-block:: bash

    $ cd ..; cp -r package ini; cd ini
    $ $VENV/bin/pip install -e .

For a few steps, you won't copy the previous step's directory, but you will still need to install your project with ``$VENV/bin/pip install -e .``.
