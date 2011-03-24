=============================
Distributing Your Application
=============================

Once your application works properly, you can create a "tarball" from
it by using the ``setup.py sdist`` command.  The following commands
assume your current working directory is the ``tutorial`` package
we've created and that the parent directory of the ``tutorial``
package is a virtualenv representing a :app:`Pyramid` environment.

On UNIX:

.. code-block:: text

   $ ../bin/python setup.py sdist

On Windows:

.. code-block:: text

   c:\pyramidtut> ..\Scripts\python setup.py sdist

The output of such a command will be something like:

.. code-block:: text

   running sdist
   # ... more output ...
   creating dist
   tar -cf dist/tutorial-0.1.tar tutorial-0.1
   gzip -f9 dist/tutorial-0.1.tar
   removing 'tutorial-0.1' (and everything under it)

Note that this command creates a tarball in the "dist" subdirectory
named ``tutorial-0.1.tar.gz``.  You can send this file to your friends
to show them your cool new application.  They should be able to
install it by pointing the ``easy_install`` command directly at it.
Or you can upload it to `PyPI <http://pypi.python.org>`_ and share it
with the rest of the world, where it can be downloaded via
``easy_install`` remotely like any other package people download from
PyPI.

