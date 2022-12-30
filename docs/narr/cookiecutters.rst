.. index::
    single: cookiecutter

.. _cookiecutters:

Pyramid cookiecutters
=====================

A :term:`cookiecutter` is a command-line utility that creates projects from `cookiecutters <https://cookiecutter.readthedocs.io/en/latest/>`__ (project templates).

The Pylons Project supports one official Pyramid cookiecutter `pyramid-cookiecutter-starter <https://github.com/Pylons/pyramid-cookiecutter-starter>`_.

Cookiecutters that use Pyramid can be found using a `search of the GitHub topic "cookiecutter-template" for "Pyramid" <https://github.com/topics/cookiecutter-template?q=pyramid&unscoped_q=pyramid>`_.

You can extend Pyramid by creating a :term:`cookiecutter` project template.
This is useful if you would like to distribute a customizable configuration of Pyramid to other users.
Once you have created a cookiecutter, other people can use it to create a custom version of your Pyramid application.

.. versionadded:: 1.8
    Added cookiecutter support.

.. versionchanged:: 1.10
    Merged features from ``pyramid-cookiecutter-alchemy`` and ``pyramid-cookiecutter-zodb`` into the single cookiecutter to rule them all, ``pyramid-cookiecutter-starter``.

.. deprecated:: 1.10
    ``pyramid-cookiecutter-alchemy`` and ``pyramid-cookiecutter-zodb`` are no longer supported.
    Use ``pyramid-cookiecutter-starter`` going forward.


.. _cookiecutter-basics:

Basics
------

See `Cookiecutter Installation <https://cookiecutter.readthedocs.io/en/latest/installation.html>`_ to get started.

Then see the `README <https://github.com/Pylons/pyramid-cookiecutter-starter#pyramid-cookiecutter-starter>`_ of ``pyramid-cookiecutter-starter`` for its usage to generate a starter project.

The ``pyramid-cookiecutter-starter`` on its ``main`` branch is a good starting point to develop your own cookiecutter.
Development of cookiecutters is documented under `Learn the Basics of Cookiecutter by Creating a Cookiecutter <https://cookiecutter.readthedocs.io/en/latest/first_steps.html>`_.
See `Cookiecutter Features <https://cookiecutter.readthedocs.io/en/latest/README.html#features>`_ for details of what is possible.
