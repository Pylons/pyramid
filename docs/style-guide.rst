.. _style-guide:

Style Guide
===========

.. admonition:: description

   This chapter describes how to edit, update, and build the :app:`Pyramid` documentation.


.. _style-guide-introduction:

Introduction
------------

This chapter provides details of how to contribute updates to the documentation following style guidelines and conventions. We provide examples, including reStructuredText code and its rendered output for both visual and technical reference.


.. _style-guide-contribute:

How to update and contribute to documentation
---------------------------------------------

All projects under the Pylons Projects, including this one, follow the guidelines established at `How to Contribute <http://www.pylonsproject.org/community/how-to-contribute>`_ and `Coding Style and Standards <http://docs.pylonsproject.org/en/latest/community/codestyle.html>`_.

By building the documentation locally, you can preview the output before committing and pushing your changes to the repository. Follow the instructions for `Building documentation for a Pylons Project project <https://github.com/Pylons/pyramid/blob/master/contributing.md#building-documentation-for-a-pylons-project-project>`_. These instructions also include how to install packages required to build the documentation, and how to follow our recommended git workflow.

When submitting a pull request for the first time in a project, sign `CONTRIBUTORS.txt <https://github.com/Pylons/pyramid/blob/master/CONTRIBUTORS.txt>`_ and commit it along with your pull request.


.. _style-guide-file-conventions:

Location, referencing, and naming of files
------------------------------------------

- reStructuredText (reST) files must be located in ``docs/`` and its subdirectories.
- Image files must be located in ``docs/_static/``.
- reST directives must refer to files either relative to the source file or absolute from the top source directory. For example, in ``docs/narr/source.rst``, you could refer to a file in a different directory as either ``.. include:: ../diff-dir/diff-source.rst`` or ``.. include:: /diff-dir/diff-source.rst``.
- File names should be lower-cased and have words separated with either a hyphen "-" or an underscore "_".
- reST files must have an extension of ``.rst``.
- Image files may be any format but must have lower-cased file names and have standard file extensions that consist three letters (``.gif``, ``.jpg``, ``.png``, ``.svg``).  ``.gif`` and ``.svg`` are not currently supported by PDF builders in Sphinx, but you can allow the Sphinx builder to automatically select the correct image format for the desired output by replacing the three-letter file extension with ``*``.  For example:

  .. code-block:: rst

     .. image:: ../_static/pyramid_request_processing.-

  will select the image ``pyramid_request_processing.svg`` for the HTML documentation builder, and ``pyramid_request_processing.png`` for the PDF builder. See the related [Stack Overflow post](http://stackoverflow.com/questions/6473660/using-sphinx-docs-how-can-i-specify-png-image-formats-for-html-builds-and-pdf-im/6486713#6486713).


.. _style-guide-page-structure:

Page structure
--------------

Each page should contain in order the following.

- The main heading. This will be visible in the table of contents.

    .. code-block:: rst

        ================
        The main heading
        ================

- The description of the page. This text will be displayed to the reader below the main heading as well as be inserted into the description metadata field of the document. It will be displayed in search engine listings for the page. This is created using the reST ``admonition`` directive. A single paragraph of text consisting of no more than three sentences is recommended, so that the same text fits into search engine results:

    .. code-block:: rst

        .. admonition:: description

           This is a description of the page, which will appear inline and in the description metadata field.

    .. note:: The ``description`` metadata field is not yet implemented in the documentation's Sphinx theme, but it is a `feature request <https://github.com/Pylons/pylons_sphinx_theme/wiki/New-Theme-Requests>`_, so it is helpful to start using the ``description`` admonition now.

- Introduction paragraph.

    .. code-block:: rst

        Introduction
        ------------

        This chapter is an introduction.

- Finally the content of the document page, consisting of reST elements such as headings, paragraphs, tables, and so on.


.. _style-guide-line-lengths:

Line lengths
------------

Narrative documentation is not code, and should therefore not adhere to PEP8 or other line length conventions. When a translator sees only part of a sentence or paragraph, it makes it more difficult to translate the concept. Line lengths make ``diff`` more difficult. Text editors can soft wrap lines for display to avoid horizontal scrolling. We admit, we boofed it by using arbitrary 79-character line lengths in our own documentation, but we have seen the error of our ways and wish to correct this going forward.


.. _style-guide-trailing-white-space:

Trailing white spaces
---------------------

- No trailing white spaces.
- Always use a line feed or carriage return at the end of a file.


.. _style-guide-indentation:

Indentation
-----------

- Indent using four spaces.
- Do not use tabs to indent.


.. _style-guide-headings:

Headings
--------

Capitalize only the first letter in a heading, unless other words are proper nouns or acronyms, e.g., "Pyramid" or "HTML".


.. _style-guide-paragraphs:

Paragraphs
----------

A paragraph should be on one line. Paragraphs must be separated by two line feeds.


.. _style-guide-grammar-spelling-preferences:

Grammar, spelling, and capitalization preferences
-------------------------------------------------

Use any commercial or free professional style guide in general. Use a spell- and grammar-checker. The following table lists the preferred grammar, spelling, and capitalization of words and phrases for frequently used items in the documentation.

==========           ======================
Preferred            Avoid
==========           ======================
add-on	             addon
and so on	         etc.
GitHub	             Github, github
JavaScript	         Javascript, javascript
plug-in	             plugin
select	             check, tick (checkbox)
such as	             like
verify	             be sure
==========           ======================





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

See :term:`venv` for the meaning of ``$VENV``.

Example blocks representing Windows commands are prefixed with a drive letter
with an optional directory name, e.g.:

  .. code-block:: doscon

     c:\examples> %VENV%\Scripts\py.test -q

See :term:`venv` for the meaning of ``%VENV%``.

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

- It allows one to swap out the higher-level package ``foo`` for something else
  that provides the similar API. An example would be swapping out one database
  for another (e.g., graduating from SQLite to PostgreSQL).

- Looks more neat in cases where a large number of objects get imported from
  that package.

- Adding or removing imported objects from the package is quicker and results
  in simpler diffs.
