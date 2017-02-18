.. _typographical-conventions:

Typographical Conventions
=========================

.. meta::
   :description: This chapter describes typographical conventions used in the Pyramid documentation.
   :keywords: Pyramid, Typographical Conventions


.. _typographical-conventions-introduction:

Introduction
------------

This chapter describes typographical conventions used in the Pyramid documentation.


.. _typographical-conventions-glossary:

Glossary
--------

A glossary defines terms used throughout the documentation. References to glossary terms appear as follows.

:term:`request`

Note it is hyperlinked, and when clicked it will take the user to the term in the Glossary and highlight the term.


.. _typographical-conventions-links:

Links
-----

Links are presented as follows, and may be clickable.

`TryPyramid <https://TryPyramid.com>`_

.. seealso:: See also :ref:`typographical-conventions-cross-references` for other links within the documentation.


.. _typographical-conventions-topic:

Topic
-----

A topic is similar to a block quote with a title, or a self-contained section with no subsections. A topic indicates a self-contained idea that is separate from the flow of the document. Topics may occur anywhere a section or transition may occur.

.. topic:: Topic Title

    Subsequent indented lines comprise
    the body of the topic, and are
    interpreted as body elements.


.. _typographical-conventions-displaying-code:

Code
----

Code may be displayed in blocks or inline. Blocks of code may use syntax highlighting, line numbering, and emphasis.


.. _typographical-conventions-syntax-highlighting:

Syntax highlighting
^^^^^^^^^^^^^^^^^^^

XML:

.. code-block:: xml

    <somesnippet>Some XML</somesnippet>

Unix shell commands are prefixed with a ``$`` character. (See :term:`venv` for the meaning of ``$VENV``.)

.. code-block:: bash

    $ $VENV/bin/pip install -e .

Windows commands are prefixed with a drive letter with an optional directory name. (See :term:`venv` for the meaning of ``%VENV%``.)

.. code-block:: doscon

    c:\> %VENV%\Scripts\pserve development.ini

cfg:

.. code-block:: cfg

    [some-part]
    # A random part in the buildout
    recipe = collective.recipe.foo
    option = value

ini:

.. code-block:: ini

    [nosetests]
    match=^test
    where=pyramid
    nocapture=1

Interactive Python:

.. code-block:: pycon

    >>> class Foo:
    ...     bar = 100
    ...
    >>> f = Foo()
    >>> f.bar
    100
    >>> f.bar / 0
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
    ZeroDivisionError: integer division or modulo by zero


.. _typographical-conventions-long-commands:

Displaying long commands
^^^^^^^^^^^^^^^^^^^^^^^^

When a command that should be typed on one line is too long to fit on the displayed width of a page, the backslash character ``\`` is used to indicate that the subsequent printed line should be part of the command:

.. code-block:: bash

    $ $VENV/bin/py.test tutorial/tests.py --cov-report term-missing \
        --cov=tutorial -q


.. _typographical-conventions-code-block-options:

Code block options
^^^^^^^^^^^^^^^^^^

To emphasize lines, we give the appearance that a highlighting pen has been used on the code.

.. code-block:: python
    :emphasize-lines: 1,3

    if "foo" == "bar":
        # This is Python code
        pass

A code block with line numbers.

.. code-block:: python
    :linenos:

    if "foo" == "bar":
        # This is Python code
        pass

Some code blocks may be given a caption.

.. code-block:: python
    :caption: sample.py
    :name: sample-py-typographical-conventions

    if "foo" == "bar":
        # This is Python code
        pass


.. _typographical-conventions-inline-code:

Inline code
^^^^^^^^^^^

Inline code is displayed as follows, where the inline code is 'pip install -e ".[docs]"'.

Install requirements for building documentation: ``pip install -e ".[docs]"``


.. _typographical-conventions-feature-versioning:

Feature versioning
------------------

We designate the version in which something is added, changed, or deprecated in the project.


.. _typographical-conventions-version-added:

Version added
^^^^^^^^^^^^^

The version in which a feature is added to a project is displayed as follows.

.. versionadded:: 1.1
    :func:`pyramid.paster.bootstrap`


.. _typographical-conventions-version-changed:

Version changed
^^^^^^^^^^^^^^^

The version in which a feature is changed in a project is displayed as follows.

.. versionchanged:: 1.8
    Added the ability for ``bootstrap`` to cleanup automatically via the ``with`` statement.


.. _typographical-conventions-deprecated:

Deprecated
^^^^^^^^^^

The version in which a feature is deprecated in a project is displayed as follows.

.. deprecated:: 1.7
    Use the ``require_csrf`` option or read :ref:`auto_csrf_checking` instead to have :class:`pyramid.exceptions.BadCSRFToken` exceptions raised.


.. _typographical-conventions-danger:

Danger
------

Danger represents critical information related to a topic or concept, and should recommend to the user "don't do this dangerous thing".

.. danger::

    This is danger or an error.


.. _typographical-conventions-warnings:

Warnings
--------

Warnings represent limitations and advice related to a topic or concept.

.. warning::

    This is a warning.


.. _typographical-conventions-notes:

Notes
-----

Notes represent additional information related to a topic or concept.

.. note::

    This is a note.


.. _typographical-conventions-see-also:

See also
--------

"See also" messages refer to topics that are related to the current topic, but have a narrative tone to them instead of merely a link without explanation. "See also" is rendered in a block as well, so that it stands out for the reader's attention.

.. seealso::

    See :ref:`Quick Tutorial section on Requirements <qtut_requirements>`.


.. _typographical-conventions-todo:

Todo
----

Todo items designated tasks that require further work.

.. todo::

    This is a todo item.


.. _typographical-conventions-cross-references:

Cross-references
----------------

Cross-references are links that may be to a document, arbitrary location, object, or other items.


.. _typographical-conventions-cross-referencing-documents:

Cross-referencing documents
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Links to pages within this documentation display as follows.

:doc:`quick_tour`


.. _typographical-conventions-cross-referencing-arbitrary-locations:

Cross-referencing arbitrary locations
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Links to sections, and tables and figures with captions, within this documentation display as follows.

:ref:`i18n_chapter`


.. _typographical-conventions-cross-referencing-python:

Python modules, classes, methods, and functions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

All of the following are clickable links to Python modules, classes, methods, and functions.

Python module names display as follows.

:mod:`pyramid.config`

Python class names display as follows.

:class:`pyramid.config.Configurator`

Python method names display as follows.

:meth:`pyramid.config.Configurator.add_view`

Python function names display as follows.

:func:`pyramid.renderers.render_to_response`

Sometimes we show only the last segment of a Python object's name, which displays as follows.

:func:`~pyramid.renderers.render_to_response`

The application "Pyramid" itself displays as follows.

:app:`Pyramid`

