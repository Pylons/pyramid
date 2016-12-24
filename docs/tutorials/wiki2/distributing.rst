.. _wiki2_distributing_your_application:

=============================
Distributing Your Application
=============================

Once your application works properly, you can create a "tarball" from it by
using the ``setup.py sdist`` command.  The following commands assume your
current working directory contains the ``tutorial`` package and the
``setup.py`` file.

On UNIX:

.. code-block:: bash

   $ $VENV/bin/python setup.py sdist

On Windows:

.. code-block:: doscon

   c:\tutorial> %VENV%\Scripts\python setup.py sdist

The output of such a command will be something like:

.. code-block:: text

   running sdist
   # more output
   creating dist
   Creating tar archive
   removing 'tutorial-0.0' (and everything under it)

Note that this command creates a tarball in the ``dist`` subdirectory named
``tutorial-0.0.tar.gz``.  You can send this file to your friends to show them
your cool new application.  They should be able to install it by pointing the
``pip install`` command directly at it. Or you can upload it to `PyPI
<https://pypi.python.org/pypi>`_ and share it with the rest of the world, where
it can be downloaded via ``pip install`` remotely like any other package people
download from PyPI.
