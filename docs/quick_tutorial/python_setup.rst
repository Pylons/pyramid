============
Python Setup
============

.. note::

    This tutorial is aimed at Python 3.3. It also works with
    Python 2.7.

First thing's first: we need our Python environment in ship-shape.
Pyramid encourages standard Python development practices (virtual
environments, packaging tools, logging, etc.) so let's get our working
area in place. For Python 3.3:

.. code-block:: bash

  $ pyvenv-3.3 venv
  $ source env/bin/activate
  (venv)$ wget https://bitbucket.org/pypa/setuptools/raw/bootstrap/ez_setup.py -O - | python

If ``wget`` complains with a certificate error, run it with:

.. code-block:: bash

  $ wget --no-check-certificate

In these steps above we first made a :term:`virtualenv` and then
"activated"  it, which adjusted our path to look first in
``venv/bin`` for commands (such as ``python``). We next downloaded
Python's packaging support and installed it, giving us the
``easy_install`` command-line script for adding new packages. Python
2.7 users will need to use ``virtualenv`` instead of ``pyvenv`` to make
their virtual environment.

.. note::

   Why ``easy_install`` and not ``pip``? Pyramid encourages use of
   namespace packages which, until recently, ``pip`` didn't permit.
   Also, Pyramid has some optional C extensions for performance. With
   ``easy_install``, Windows users can get these extensions without
   needing a C compiler.

.. seealso:: See Also: Python 3's :mod:`venv module <python3:venv>`,
   the ``setuptools`` `installation
   instructions <https://pypi.python.org/pypi/setuptools/0.9.8#installation-instructions>`_,
   `easy_install help <https://pypi.python.org/pypi/setuptools/0.9.8#using-setuptools-and-easyinstall>`_,
   and Pyramid's :ref:`Before You Install <installing_chapter>`.
