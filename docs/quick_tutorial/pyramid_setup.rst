=============
Pyramid Setup
=============

Installing Pyramid is easy and normal from a Python packaging
perspective. Again, *make sure* you have your virtual environment first
in your path using ``source bin/activate``.

.. code-block:: bash

  (env27)$ easy_install pyramid
  ....chuggalugga...
  (env27ß)$ which pserve

You now have Pyramid installed. The second command confirms this by
looking for the Pyramid ``pserve`` command that should be on your
``$PATH`` in the ``bin`` of your virtual environment.

Installing Everything
=====================

Later parts of the tutorial install more packages. Most likely,
you'd like to go ahead and get much of it now:

.. code-block:: bash

  (env27)$ easy_install pyramid nose webtest deform sqlalchemy