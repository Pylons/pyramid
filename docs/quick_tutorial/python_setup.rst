============
Python Setup
============

First things first: we need our Python environment in ship-shape.
Pyramid encourages standard Python development practices (virtual
environments, packaging tools, logging, etc.) so let's get our working
area in place.

.. note::

    This tutorial is aimed at Python 2.7. It also works with
    Python 3.3.

*This step has most likely been performed already on the CCDC computers.*

Prequisites
===========

Modern Python development means two tools to add to the standard
Python installation: packaging and virtual environments.

Python's tools for installing packages is undergoing rapid change. For
this tutorial, we will install the latest version of
`setuptools <https://pypi.python.org/pypi/setuptools/>`_. This gives us
the ``easy_install`` command-line tool for installing Python packages.
Presuming you have Python on your ``PATH``:

.. code-block:: bash

  $ wget https://bitbucket.org/pypa/setuptools/raw/bootstrap/ez_setup.py -O - | python

We now have an ``easy_install`` command that we can use to install
``virtualenv``:

.. code-block:: bash

  $ easy_install virtualenv

Making a Virtual Environment
============================

Developing in isolation helps us ensure what we are learning doesn't
conflict with any packages installed from other work on the machine.
*Virtual environments* let us do just this.

Presuming you have made a tutorial area at some location (referenced as
``your/tutorial/directory`` below):

.. code-block:: bash

  $ cd your/tutorial/directory
  $ virtualenv env27
  $ source env27/bin/activate
  (env27)$ which python2.7

Once you do this, your path will be setup to point at the ``bin`` of
your virtual environment. Your prompt will also change, as noted above.

.. note::

    This tutorial presumes you are working in a command-line shell
    which has performed the ``source env27/bin/activate``. If you
    close that shell, or open a new one, you will need to re-perform
    that command.

Discussion
==========

The modern world of Python packaging eschews ``easy_install`` in favor
of ``pip``, a more-recent and maintained packaging tool. Why doesn't
this tutorial use it?

- ``pip`` is only gradually getting the ability to install Windows
  binaries. ``easy_install`` has been able to do this for years.

- Until recently, ``pip`` has not been able to use "namespace
  packages." As the ``pip`` support for this stabilizes,
  we can switch to using ``pip``.

- You have to use ``easy_install`` to get ``pip`` installed, so why not
  just stick with ``easy_install``.

Python 3.3 has a `built-in story for virtual
environments <http://docs.python.org/dev/library/venv.html>`_. This
eliminates the requirement for installing ``virtualenv``. Instead,
Python 3.3 provides the ``pyvenv`` command for creating virtual
environments.