Typographical Conventions
=========================

Literals, filenames, and function arguments are presented using the
following style:

  ``argument1``

Warnings which represent limitations and need-to-know information
related to a topic or concept are presented in the following style:

  .. warning::

     This is a warning.

Notes which represent additional information related to a topic or
concept are presented in the following style:

  .. note::

     This is a note.

We present Python method names using the following style:

  :meth:`pyramid.config.Configurator.add_view`

We present Python class names, module names, attributes, and global
variables using the following style:

  :class:`pyramid.config.Configurator.registry`

References to glossary terms are presented using the following style:

  :term:`Pylons`

URLs are presented using the following style:

  `Pylons <http://www.pylonsproject.org>`_

References to sections and chapters are presented using the following
style:

  :ref:`traversal_chapter`

Code and configuration file blocks are presented in the following style:

  .. code-block:: python
     :linenos:

     def foo(abc):
         pass

Example blocks representing UNIX shell commands are prefixed with a ``$``
character, e.g.:

  .. code-block:: bash

     $ $VENV/bin/py.test -q

(See :term:`venv` for the meaning of ``$VENV``)

Example blocks representing Windows ``cmd.exe`` commands are prefixed with a
drive letter and/or a directory name, e.g.:

  .. code-block:: doscon

     c:\examples> %VENV%\Scripts\py.test -q

(See :term:`venv` for the meaning of ``%VENV%``)

Sometimes, when it's unknown which directory is current, Windows ``cmd.exe``
example block commands are prefixed only with a ``>`` character, e.g.:

  .. code-block:: doscon

     > %VENV%\Scripts\py.test -q

When a command that should be typed on one line is too long to fit on a page,
the backslash ``\`` is used to indicate that the following printed line should
be part of the command:

  .. code-block:: bash

     $VENV/bin/py.test tutorial/tests.py --cov-report term-missing \
                       --cov=tutorial -q

A sidebar, which presents a concept tangentially related to content discussed
on a page, is rendered like so:

.. sidebar:: This is a sidebar

   Sidebar information.

When multiple objects are imported from the same package, the following
convention is used:

    .. code-block:: python

       from foo import (
           bar,
           baz,
           )

It may look unusual, but it has advantages:

* It allows one to swap out the higher-level package ``foo`` for something else
  that provides the similar API. An example would be swapping out one database
  for another (e.g., graduating from SQLite to PostgreSQL).

* Looks more neat in cases where a large number of objects get imported from
  that package.

* Adding or removing imported objects from the package is quicker and results
  in simpler diffs.
