.. _style-guide:

Style Guide
===========

.. meta::
   :description: This chapter describes how to edit, update, and build the Pyramid documentation.
   :keywords: Pyramid, Style Guide


.. _style-guide-introduction:

Introduction
------------

This chapter provides details of how to contribute updates to the documentation following style guidelines and conventions. We provide examples, including reStructuredText code and its rendered output for both visual and technical reference.

For coding style guidelines, see `Coding Style <http://docs.pylonsproject.org/en/latest/community/codestyle.html#coding-style>`_.


.. _style-guide-contribute:

How to update and contribute to documentation
---------------------------------------------

All projects under the Pylons Projects, including this one, follow the guidelines established at `How to Contribute <http://www.pylonsproject.org/community/how-to-contribute>`_ and `Coding Style and Standards <http://docs.pylonsproject.org/en/latest/community/codestyle.html>`_.

By building the documentation locally, you can preview the output before committing and pushing your changes to the repository. Follow the instructions for `Building documentation for a Pylons Project project <https://github.com/Pylons/pyramid/blob/master/contributing.md#building-documentation-for-a-pylons-project-project>`_. These instructions also include how to install packages required to build the documentation, and how to follow our recommended git workflow.

When submitting a pull request for the first time in a project, sign `CONTRIBUTORS.txt <https://github.com/Pylons/pyramid/blob/master/CONTRIBUTORS.txt>`_ and commit it along with your pull request.


.. _style-guide-file-conventions:

Location, referencing, and naming of files
------------------------------------------

* reStructuredText (reST) files must be located in ``docs/`` and its subdirectories.
* Image files must be located in ``docs/_static/``.
* reST directives must refer to files either relative to the source file or absolute from the top source directory. For example, in ``docs/narr/source.rst``, you could refer to a file in a different directory as either ``.. include:: ../diff-dir/diff-source.rst`` or ``.. include:: /diff-dir/diff-source.rst``.
* File names should be lower-cased and have words separated with either a hyphen "-" or an underscore "_".
* reST files must have an extension of ``.rst``.
* Image files may be any format but must have lower-cased file names and have standard file extensions that consist three letters (``.gif``, ``.jpg``, ``.png``, ``.svg``).  ``.gif`` and ``.svg`` are not currently supported by PDF builders in Sphinx, but you can allow the Sphinx builder to automatically select the correct image format for the desired output by replacing the three-letter file extension with ``*``.  For example:

  .. code-block:: rst

      .. image:: ../_static/pyramid_request_processing.

  will select the image ``pyramid_request_processing.svg`` for the HTML documentation builder, and ``pyramid_request_processing.png`` for the PDF builder. See the related `Stack Overflow post <http://stackoverflow.com/questions/6473660/using-sphinx-docs-how-can-i-specify-png-image-formats-for-html-builds-and-pdf-im/6486713#6486713>`_.


.. _style-guide-table-of-contents-tree:

Table of contents tree
----------------------

To insert a table of contents (TOC), use the ``toctree`` directive. Entries listed under the ``toctree`` directive follow :ref:`location conventions <style-guide-file-conventions>`. A numeric ``maxdepth`` option may be given to indicate the depth of the tree; by default, all levels are included.

.. code-block:: rst

    .. toctree::
        :maxdepth: 2

        narr/introduction
        narr/install

The above code renders as follows.

.. toctree::
    :maxdepth: 2

    narr/introduction
    narr/install

Globbing can be used.

.. code-block:: rst

    .. toctree::
        :maxdepth: 1
        :glob:

        pscripts/index
        pscripts/*

The above code renders as follows.

.. toctree::
    :maxdepth: 1
    :glob:

    pscripts/index
    pscripts/*

To notify Sphinx of the document hierarchy, but not insert links into the document at the location of the directive, use the option ``hidden``. This makes sense when you want to insert these links yourself, in a different style, or in the HTML sidebar.

.. code-block:: rst

    .. toctree::
        :hidden:

        quick_tour

    * :doc:`quick_tour` gives an overview of the major features in Pyramid, covering a little about a lot.

The above code renders as follows.

.. toctree::
    :hidden:

    quick_tour

* :doc:`quick_tour` gives an overview of the major features in Pyramid, covering a little about a lot.

.. seealso:: Sphinx documentation of :ref:`toctree-directive`.


.. _style-guide-glossary:

Glossary
--------

A glossary defines terms used throughout the documentation.

The glossary file must be named ``glossary.rst``. Its content must begin with the directive ``glossary``. An optional ``sorted`` argument should be used to sort the terms alphabetically when rendered, making it easier for the user to find a given term. Without the argument ``sorted``, terms will appear in the order of the ``glossary`` source file.

.. code-block:: rst

    .. glossary::
        :sorted:

        voom
            Theoretically, the sound a parrot makes when four-thousand volts of electricity pass through it.

        pining
            What the Norwegien Blue does when it misses its homeland, e.g., pining for the fjords.

The above code renders as follows.

.. glossary::
    :sorted:

    voom
        Theoretically, the sound a parrot makes when four-thousand volts of electricity pass through it.

    pining
        What the Norwegien Blue does when it misses its homeland, e.g., pining for the fjords.

References to glossary terms use the ``term`` directive.

.. code-block:: rst

    :term:`voom`

The above code renders as follows. Note it is hyperlinked, and when clicked it will take the user to the term in the Glossary and highlight the term.

:term:`voom`


.. _style-guide-section-structure:

Section structure
-----------------

Each section, or a subdirectory of reST files, such as a tutorial, must contain an ``index.rst`` file. ``index.rst`` must contain the following.

* A section heading. This will be visible in the table of contents.
* A single paragraph describing this section.
* A Sphinx ``toctree`` directive, with a ``maxdepth`` of 2. Each ``.rst`` file in the folder should be linked to this ``toctree``.

    .. code-block:: rst

        .. toctree::
           :maxdepth: 2

           chapter1
           chapter2
           chapter3


.. _style-guide-page-structure:

Page structure
--------------

Each page should contain in order the following.

#. The main heading. This will be visible in the table of contents.

    .. code-block:: rst

        ================
        The main heading
        ================

#. Meta tag information. The "meta" directive is used to specify HTML metadata stored in HTML META tags. "Metadata" is data about data, in this case data about web pages. Metadata is used to describe and classify web pages in the World Wide Web, in a form that is easy for search engines to extract and collate.

    .. code-block:: rst

        .. meta::
           :description: This chapter describes how to edit, update, and build the Pyramid documentation.
           :keywords: Pyramid, Style Guide

    The above code renders as follows.

    .. code-block:: xml

        <meta content="This chapter describes how to edit, update, and build the Pyramid documentation." name="description" />
        <meta content="Pyramid, Style Guide" name="keywords" />

#. Introduction paragraph.

    .. code-block:: rst

        Introduction
        ------------

        This chapter is an introduction.

#. Finally the content of the document page, consisting of reST elements such as headings, paragraphs, tables, and so on.


.. _style-guide-page-content:

Page content
------------

Within a page, content should adhere to specific guidelines.


.. _style-guide-line-lengths:

Line lengths
^^^^^^^^^^^^

Narrative documentation is not code, and should therefore not adhere to PEP8 or other line length conventions. When a translator sees only part of a sentence or paragraph, it makes it more difficult to translate the concept. Line lengths make ``diff`` more difficult. Text editors can soft wrap lines for display to avoid horizontal scrolling. We admit, we boofed it by using arbitrary 79-character line lengths in our own documentation, but we have seen the error of our ways and wish to correct this going forward.


.. _style-guide-trailing-white-space:

Trailing white spaces
^^^^^^^^^^^^^^^^^^^^^

* No trailing white spaces.
* Always use a line feed or carriage return at the end of a file.


.. _style-guide-indentation:

Indentation
^^^^^^^^^^^

* Indent using four spaces, except for :ref:`nested lists <style-guide-lists>`.
* Do not use tabs to indent.


.. _style-guide-grammar-spelling-preferences:

Grammar, spelling, and capitalization preferences
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Use any commercial or free professional style guide in general. Use a spell- and grammar-checker. The following table lists the preferred grammar, spelling, and capitalization of words and phrases for frequently used items in the documentation.

========== =====
Preferred  Avoid
========== =====
add-on     addon
and so on  etc.
GitHub     Github, github
JavaScript Javascript, javascript
plug-in    plugin
select     check, tick (checkbox)
such as    like
verify     be sure
========== =====


.. _style-guide-headings:

Headings
^^^^^^^^

Capitalize only the first letter in a heading (sentence-case), unless other words are proper nouns or acronyms, e.g., "Pyramid" or "HTML".

For consistent heading characters throughout the documentation, follow the guidelines stated in the `Python Developer's Guide <https://docs.python.org/devguide/documenting.html#sections>`_. Specifically:

* =, for sections
* -, for subsections
* ^, for subsubsections
* ", for paragraphs

As individual files do not have so-called "parts" or "chapters", the headings would be underlined with characters as shown.

    .. code-block:: rst

        ==================================
        The main heading or web page title
        ==================================

        Heading Level 1
        ---------------

        Heading Level 2
        ^^^^^^^^^^^^^^^

        Heading Level 3
        """""""""""""""

Note, we do not render heading levels here because doing so causes a loss in page structure.


.. _style-guide-paragraphs:

Paragraphs
^^^^^^^^^^

A paragraph should be on one line. Paragraphs must be separated by two line feeds.


.. _style-guide-links:

Links
^^^^^

Use inline links to keep the context or link label together with the URL. Do not use targets and links at the end of the page, because the separation makes it difficult to update and translate. Here is an example of inline links, our required method.

.. code-block:: rst

    `TryPyramid <https://trypyramid.com>`_

The above code renders as follows.

`TryPyramid <https://TryPyramid.com>`_

.. seealso:: See also :ref:`style-guide-cross-references` for generating links throughout the entire documentation.


.. _style-guide-topic:

Topic
^^^^^

A topic is similar to a block quote with a title, or a self-contained section with no subsections. Use the ``topic`` directive to indicate a self-contained idea that is separate from the flow of the document. Topics may occur anywhere a section or transition may occur. Body elements and topics may not contain nested topics.

The directive's sole argument is interpreted as the topic title, and next line must be blank. All subsequent lines make up the topic body, interpreted as body elements.

    .. code-block:: rst

        .. topic:: Topic Title

            Subsequent indented lines comprise
            the body of the topic, and are
            interpreted as body elements.

The above code renders as follows.

.. topic:: Topic Title

    Subsequent indented lines comprise
    the body of the topic, and are
    interpreted as body elements.

.. _style-guide-displaying-code:

Displaying code
^^^^^^^^^^^^^^^

Code may be displayed in blocks or inline. You can include blocks of code from other source files. Blocks of code should use syntax highlighting, and may use line numbering or emphasis.

.. seealso:: See also the Sphinx documentation for :ref:`code-examples`.


.. _style-guide-syntax-highlighting:

Syntax highlighting
"""""""""""""""""""

Sphinx does syntax highlighting of code blocks using the `Pygments <http://pygments.org/>`_ library.

Do not use two colons "::" at the end of a line, followed by a blank line, then code. Always specify the language to be used for syntax highlighting by using a language argument in the ``code-block`` directive. Always indent the subsequent code.

.. code-block:: rst

    .. code-block:: python

        if "foo" == "bar":
            # This is Python code
            pass

XML:

.. code-block:: rst

    .. code-block:: xml

        <somesnippet>Some XML</somesnippet>

Unix shell commands are prefixed with a ``$`` character. (See :term:`venv` for the meaning of ``$VENV``.)

.. code-block:: rst

    .. code-block:: bash

        $ $VENV/bin/pip install -e .

Windows commands are prefixed with a drive letter with an optional directory name. (See :term:`venv` for the meaning of ``%VENV%``.)

.. code-block:: rst

    .. code-block:: doscon

        c:\> %VENV%\Scripts\pcreate -s starter MyProject

cfg:

.. code-block:: rst

    .. code-block:: cfg

        [some-part]
        # A random part in the buildout
        recipe = collective.recipe.foo
        option = value

ini:

.. code-block:: rst

    .. code-block:: ini

        [nosetests]
        match=^test
        where=pyramid
        nocapture=1

Interactive Python:

.. code-block:: rst

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

If syntax highlighting is not enabled for your code block, you probably have a syntax error and Pygments will fail silently.

View the `full list of lexers and associated short names <http://pygments.org/docs/lexers/>`_.


.. _style-guide-parsed-literals:

Parsed literals
"""""""""""""""

Parsed literals are used to render, for example, a specific version number of the application in code blocks. Use the directive ``parsed-literal``. Note that syntax highlighting is not supported and code is rendered as plain text.

.. code-block:: rst

    .. parsed-literal::

        $ $VENV/bin/pip install "pyramid==\ |release|\ "

The above code renders as follows.

.. parsed-literal::

    $ $VENV/bin/pip install "pyramid==\ |release|\ "


.. _style-guide-long-commands:

Displaying long commands
""""""""""""""""""""""""

When a command that should be typed on one line is too long to fit on the displayed width of a page, the backslash character ``\`` is used to indicate that the subsequent printed line should be part of the command:

.. code-block:: rst

    .. code-block:: bash

        $ $VENV/bin/py.test tutorial/tests.py --cov-report term-missing \
            --cov=tutorial -q


.. _style-guide-code-block-options:

Code block options
""""""""""""""""""

To emphasize lines (give the appearance that a highlighting pen has been used on the code), use the ``emphasize-lines`` option. The argument passed to ``emphasize-lines`` must be a comma-separated list of either single or ranges of line numbers.

.. code-block:: rst

    .. code-block:: python
        :emphasize-lines: 1,3

        if "foo" == "bar":
            # This is Python code
            pass

The above code renders as follows.

.. code-block:: python
    :emphasize-lines: 1,3

    if "foo" == "bar":
        # This is Python code
        pass

To display a code block with line numbers, use the ``linenos`` option.

.. code-block:: rst

    .. code-block:: python
        :linenos:

        if "foo" == "bar":
            # This is Python code
            pass

The above code renders as follows.

.. code-block:: python
    :linenos:

    if "foo" == "bar":
        # This is Python code
        pass

Code blocks may be given a caption, which may serve as a filename or other description, using the ``caption`` option. They may also be given a ``name`` option, providing an implicit target name that can be referenced by using ``ref`` (see :ref:`style-guide-cross-referencing-arbitrary-locations`).

.. code-block:: rst

    .. code-block:: python
        :caption: sample.py
        :name: sample-py

        if "foo" == "bar":
            # This is Python code
            pass

The above code renders as follows.

.. code-block:: python
    :caption: sample.py
    :name: sample-py

    if "foo" == "bar":
        # This is Python code
        pass

To specify the starting number to use for line numbering, use the ``lineno-start`` directive.

.. code-block:: rst

    .. code-block:: python
        :lineno-start: 2

        if "foo" == "bar":
            # This is Python code
            pass

The above code renders as follows. As you can see, ``lineno-start`` is not altogether accurate.

.. code-block:: python
    :lineno-start: 2

    if "foo" == "bar":
        # This is Python code
        pass


.. _style-guide-includes:

Includes
""""""""

Longer displays of verbatim text may be included by storing the example text in an external file containing only plain text or code. The file may be included using the ``literalinclude`` directive. The file name follows the conventions of :ref:`style-guide-file-conventions`.

.. code-block:: rst

    .. literalinclude:: narr/helloworld.py
        :language: python

The above code renders as follows.

.. literalinclude:: narr/helloworld.py
    :language: python

Like code blocks, ``literalinclude`` supports the following options.

* ``language`` to select a language for syntax highlighting
* ``linenos`` to switch on line numbers
* ``lineno-start`` to specify the starting number to use for line numbering
* ``emphasize-lines`` to emphasize particular lines

.. code-block:: rst

    .. literalinclude:: narr/helloworld.py
        :language: python
        :linenos:
        :lineno-start: 11
        :emphasize-lines: 1,6-7,9-

The above code renders as follows. Note that ``lineno-start`` and ``emphasize-lines`` do not align.  The former displays numbering starting from the *arbitrarily provided value*, whereas the latter emphasizes the line numbers of the *source file*.

.. literalinclude:: narr/helloworld.py
    :language: python
    :linenos:
    :lineno-start: 11
    :emphasize-lines: 1,6-7,9-

``literalinclude`` also supports including only parts of a file.

If the source code is a Python module, you can select a class, function, or method to include using the ``pyobject`` option.

.. code-block:: rst

    .. literalinclude:: narr/helloworld.py
        :language: python
        :pyobject: hello_world

The above code renders as follows. It returns the function ``hello_world`` in the source file.

.. literalinclude:: narr/helloworld.py
    :language: python
    :pyobject: hello_world

Another way to control which part of the file is included is to use the ``start-after`` and ``end-before`` options (or only one of them). If ``start-after`` is given as a string option, only lines that follow the first line containing that string are included. If ``end-before`` is given as a string option, only lines that precede the first lines containing that string are included.

.. code-block:: rst

    .. literalinclude:: narr/helloworld.py
        :language: python
        :start-after: from pyramid.response import Response
        :end-before: if __name__ == '__main__':

The above code renders as follows.

.. literalinclude:: narr/helloworld.py
    :language: python
    :start-after: from pyramid.response import Response
    :end-before: if __name__ == '__main__':

You can specify exactly which lines to include by giving a ``lines`` option.

.. code-block:: rst

    .. literalinclude:: narr/helloworld.py
        :language: python
        :lines: 6-7

The above code renders as follows.

.. literalinclude:: narr/helloworld.py
    :language: python
    :lines: 6-7

When specifying particular parts of a file to display, it can be useful to display exactly which lines are being presented. This can be done using the ``lineno-match`` option.

.. code-block:: rst

    .. literalinclude:: narr/helloworld.py
        :language: python
        :lines: 6-7
        :lineno-match:

The above code renders as follows.

.. literalinclude:: narr/helloworld.py
    :language: python
    :lines: 6-7
    :lineno-match:

Out of all the ways to include parts of a file, ``pyobject`` is the most preferred option because if you change your code and add or remove lines, you don't need to adjust line numbering, whereas with ``lines`` you would have to adjust. ``start-after`` and ``end-before`` are less desirable because they depend on source code not changing. Alternatively you can insert comments into your source code to act as the delimiters, but that just adds comments that have nothing to do with the functionality of your code.

Above all with includes, if you use line numbering, it's much preferred to use ``lineno-match`` over ``linenos`` with ``lineno-start`` because it "just works" without thinking and with less markup.


.. _style-guide-inline-code:

Inline code
"""""""""""

Inline code is surrounded by double backtick marks. Literals, filenames, and function arguments are presented using this style.

.. code-block:: rst

    Install requirements for building documentation: ``pip install -e ".[docs]"``

The above code renders as follows.

Install requirements for building documentation: ``pip install -e ".[docs]"``


.. _style-guide-rest-block-markup:

reST block markup
-----------------

This section contains miscellaneous reST block markup for items not already covered.


.. _style-guide-lists:

Lists
^^^^^

Bulleted lists use an asterisk "``*``".

.. code-block:: rst

    * This is an item in a bulleted list.
    * This is another item in a bulleted list.

The above code renders as follows.

* This is an item in a bulleted list.
* This is another item in a bulleted list.

Numbered lists should use a number sign followed by a period "``#.``" and will be numbered automatically.

.. code-block:: rst

    #. This is an item in a numbered list.
    #. This is another item in a numbered list.

The above code renders as follows.

#. This is an item in a numbered list.
#. This is another item in a numbered list.

The appearance of nested lists can be created by separating the child lists from their parent list by blank lines, and indenting by two spaces. Note that Sphinx renders the reST markup not as nested HTML lists, but instead merely indents the children using ``<blockquote>``.

.. code-block:: rst

    #. This is a list item in the parent list.
    #. This is another list item in the parent list.

      #. This is a list item in the child list.
      #. This is another list item in the child list.

    #. This is one more list item in the parent list.

The above code renders as follows.

#. This is a list item in the parent list.
#. This is another list item in the parent list.

  #. This is a list item in the child list.
  #. This is another list item in the child list.

#. This is one more list item in the parent list.


.. _style-guide-tables:

Tables
^^^^^^

Two forms of tables are supported, `simple <http://docutils.sourceforge.net/docs/ref/rst/restructuredtext.html#simple-tables>`_ and `grid <http://docutils.sourceforge.net/docs/ref/rst/restructuredtext.html#grid-tables>`_.

Simple tables require less markup but have fewer features and some constraints compared to grid tables. The right-most column in simple tables is unbound to the length of the underline in the column header.

.. code-block:: rst

    =====  =====
    col 1  col 2
    =====  =====
    1      Second column of row 1.
    2      Second column of row 2.
           Second line of paragraph.
    3      * Second column of row 3.

           * Second item in bullet
             list (row 3, column 2).
    \      Row 4; column 1 will be empty.
    =====  =====

The above code renders as follows.

=====  =====
col 1  col 2
=====  =====
1      Second column of row 1.
2      Second column of row 2.
       Second line of paragraph.
3      * Second column of row 3.

       * Second item in bullet
         list (row 3, column 2).
\      Row 4; column 1 will be empty.
=====  =====

Grid tables have much more cumbersome markup, although Emacs' table mode may lessen the tedium.

.. code-block:: rst

    +------------------------+------------+----------+----------+
    | Header row, column 1   | Header 2   | Header 3 | Header 4 |
    | (header rows optional) |            |          |          |
    +========================+============+==========+==========+
    | body row 1, column 1   | column 2   | column 3 | column 4 |
    +------------------------+------------+----------+----------+
    | body row 2             | Cells may span columns.          |
    +------------------------+------------+---------------------+
    | body row 3             | Cells may  | * Table cells       |
    +------------------------+ span rows. | * contain           |
    | body row 4             |            | * body elements.    |
    +------------------------+------------+---------------------+

The above code renders as follows.

+------------------------+------------+----------+----------+
| Header row, column 1   | Header 2   | Header 3 | Header 4 |
| (header rows optional) |            |          |          |
+========================+============+==========+==========+
| body row 1, column 1   | column 2   | column 3 | column 4 |
+------------------------+------------+----------+----------+
| body row 2             | Cells may span columns.          |
+------------------------+------------+---------------------+
| body row 3             | Cells may  | * Table cells       |
+------------------------+ span rows. | * contain           |
| body row 4             |            | * body elements.    |
+------------------------+------------+---------------------+


.. _style-guide-feature-versioning:

Feature versioning
^^^^^^^^^^^^^^^^^^

Three directives designate the version in which something is added, changed, or deprecated in the project.


.. _style-guide-version-added:

Version added
"""""""""""""

To indicate the version in which a feature is added to a project, use the ``versionadded`` directive. If the feature is an entire module, then the directive should be placed at the top of the module section before any prose.

The first argument is the version. An optional second argument must appear upon a subsequent line, without blank lines in between, and indented.

.. code-block:: rst

    .. versionadded:: 1.1
        :func:`pyramid.paster.bootstrap`

The above code renders as follows.

.. versionadded:: 1.1
    :func:`pyramid.paster.bootstrap`


.. _style-guide-version-changed:

Version changed
"""""""""""""""

To indicate the version in which a feature is changed in a project, use the ``versionchanged`` directive. Its arguments are the same as ``versionadded``.

.. code-block:: rst

    .. versionchanged:: 1.8
        Added the ability for ``bootstrap`` to cleanup automatically via the ``with`` statement.

The above code renders as follows.

.. versionchanged:: 1.8
    Added the ability for ``bootstrap`` to cleanup automatically via the ``with`` statement.


.. _style-guide-deprecated:

Deprecated
""""""""""

Similar to ``versionchanged``, ``deprecated`` describes when the feature was deprecated. An explanation can also be given, for example, to inform the reader what should be used instead.

.. code-block:: rst

    .. deprecated:: 1.7
        Use the ``require_csrf`` option or read :ref:`auto_csrf_checking` instead to have :class:`pyramid.exceptions.BadCSRFToken` exceptions raised.

The above code renders as follows.

.. deprecated:: 1.7
    Use the ``require_csrf`` option or read :ref:`auto_csrf_checking` instead to have :class:`pyramid.exceptions.BadCSRFToken` exceptions raised.


.. _style-guide-danger:

Danger
^^^^^^

Danger represents critical information related to a topic or concept, and should recommend to the user "don't do this dangerous thing".

.. code-block:: rst

    .. danger::

        This is danger or an error.

The above code renders as follows.

.. danger::

    This is danger or an error.

.. todo::

    The style for ``danger`` and ``error`` has not yet been created.


.. _style-guide-warnings:

Warnings
^^^^^^^^

Warnings represent limitations and advice related to a topic or concept.

.. code-block:: rst

    .. warning::

        This is a warning.

The above code renders as follows.

.. warning::

    This is a warning.


.. _style-guide-notes:

Notes
^^^^^

Notes represent additional information related to a topic or concept.

.. code-block:: rst

    .. note::

        This is a note.

The above code renders as follows.

.. note::

    This is a note.


.. _style-guide-see-also:

See also
^^^^^^^^

"See also" messages refer to topics that are related to the current topic, but have a narrative tone to them instead of merely a link without explanation. "See also" is rendered in a block as well, so that it stands out for the reader's attention.

.. code-block:: rst

    .. seealso::

        See :ref:`Quick Tutorial section on Requirements <qtut_requirements>`.

The above code renders as follows.

.. seealso::

    See :ref:`Quick Tutorial section on Requirements <qtut_requirements>`.


.. _style-guide-todo:

Todo
^^^^

Todo items designated tasks that require further work.

.. code-block:: rst

    .. todo::

        This is a todo item.

The above code renders as follows.

.. todo::

    This is a todo item.

.. todo::

    The todo style is not yet implemented and needs further work.


.. _style-guide-comments:

Comments
^^^^^^^^

Comments of the documentation within the documentation may be generated with two periods ``..``. Comments are not rendered, but provide information to documentation authors.

.. code-block:: rst

    .. This is an example comment.


.. _style-guide-rest-inline-markup:

reST inline markup
------------------

This section contains miscellaneous reST inline markup for items not already covered. Within a block of content, inline markup is useful to apply styles and links to other files.


.. _style-guide-italics:

Italics
^^^^^^^

.. code-block:: rst

    This *word* is italicized.

The above code renders as follows.

This *word* is italicized.


.. _style-guide-strong:

Strong
^^^^^^

.. code-block:: rst

    This **word** is in bold text.

The above code renders as follows.

This **word** is in bold text.

.. seealso::

    See also the Sphinx documentation for the :ref:`rst-primer`.


.. _style-guide-cross-references:

Cross-references
^^^^^^^^^^^^^^^^

To create cross-references to a document, arbitrary location, object, or other items, use variations of the following syntax.

* ``:role:`target``` creates a link to the item named ``target`` of the type indicated by ``role``, with the link's text as the title of the target. ``target`` may need to be disambiguated between documentation sets linked through intersphinx, in which case the syntax would be ``deform:overview``.
* ``:role:`~target``` displays the link as only the last component of the target.
* ``:role:`title <target>``` creates a custom title, instead of the default title of the target.


.. _style-guide-cross-referencing-documents:

Cross-referencing documents
"""""""""""""""""""""""""""

To link to pages within this documentation:

.. code-block:: rst

    :doc:`quick_tour`

The above code renders as follows.

:doc:`quick_tour`


.. _style-guide-cross-referencing-arbitrary-locations:

Cross-referencing arbitrary locations
"""""""""""""""""""""""""""""""""""""

To support cross-referencing to arbitrary locations in any document and between documentation sets via intersphinx, the standard reST labels are used. For this to work, label names must be unique throughout the entire documentation including externally linked intersphinx references. There are two ways in which you can refer to labels, if they are placed directly before a section title, a figure, or table with a caption, or at any other location. The following section has a label with the syntax ``.. _label_name:`` followed by the section title.

.. code-block:: rst

    .. _i18n_chapter:

    Internationalization and Localization
    =====================================

To generate a link to that section with its title, use the following syntax.

.. code-block:: rst

    :ref:`i18n_chapter`

The above code renders as follows.

:ref:`i18n_chapter`

The same syntax works figures and tables with captions.

For labels that are not placed as mentioned, the link must be given an explicit title, such as ``:ref:`Link title <label-name>```.

.. seealso:: See also the Sphinx documentation, :ref:`inline-markup`.


.. _style-guide-cross-referencing-python:

Python modules, classes, methods, and functions
"""""""""""""""""""""""""""""""""""""""""""""""

Python module names use the ``mod`` directive, with the module name as the argument.

.. code-block:: rst

    :mod:`pyramid.config`

The above code renders as follows.

:mod:`pyramid.config`

Python class names use the ``class`` directive, with the class name as the argument.

.. code-block:: rst

    :class:`pyramid.config.Configurator`

The above code renders as follows.

:class:`pyramid.config.Configurator`

Python method names use the ``meth`` directive, with the method name as the argument.

.. code-block:: rst

    :meth:`pyramid.config.Configurator.add_view`

The above code renders as follows.

:meth:`pyramid.config.Configurator.add_view`

Python function names use the ``func`` directive, with the function name as the argument.

.. code-block:: rst

    :func:`pyramid.renderers.render_to_response`

The above code renders as follows.

:func:`pyramid.renderers.render_to_response`

Note that you can use the ``~`` prefix to show only the last segment of a Python object's name. We prefer not to use the ``.`` prefix, even though it may seem to be a convenience to documentation authors, because Sphinx might generate an error if it cannot disambiguate the reference.

.. code-block:: rst

    :func:`~pyramid.renderers.render_to_response`

The above code renders as follows.

:func:`~pyramid.renderers.render_to_response`


.. _style-guide-role-app-pyramid:

The role ``:app:`Pyramid```
^^^^^^^^^^^^^^^^^^^^^^^^^^^

We use the special role ``app`` to refer to the application "Pyramid".

.. code-block:: rst

    :app:`Pyramid`

The above code renders as follows.

:app:`Pyramid`


.. _style-guide-sphinx-extensions:

Sphinx extensions
-----------------

We use several Sphinx extensions to add features to our documentation. Extensions need to be enabled and configured in ``docs/conf.py`` before they can be used.


.. _style-guide-sphinx-extension-autodoc:

:mod:`sphinx.ext.autodoc`
-------------------------

API documentation uses the Sphinx extension :mod:`sphinx.ext.autodoc` to include documentation from docstrings.

See the source of any documentation within the ``docs/api/`` directory for conventions and usage, as well as the Sphinx extension's :mod:`documentation <sphinx.ext.autodoc>`.


.. _style-guide-sphinx-extension-doctest:

:mod:`sphinx.ext.doctest`
-------------------------

:mod:`sphinx.ext.doctest` allows you to test code snippets in the documentation in a natural way. It works by collecting specially-marked up code blocks and running them as doctest tests. We have only a few tests in our Pyramid documentation which can be found in ``narr/sessions.rst`` and ``narr/hooks.rst``.


.. _style-guide-sphinx-extension-intersphinx:

:mod:`sphinx.ext.intersphinx`
-----------------------------

:mod:`sphinx.ext.intersphinx` generates links to the documentation of objects in other projects.


.. _style-guide-sphinx-extension-todo:

:mod:`sphinx.ext.todo`
----------------------

:mod:`sphinx.ext.todo` adds support for todo items.


.. _style-guide-sphinx-extension-viewcode:

:mod:`sphinx.ext.viewcode`
--------------------------

:mod:`sphinx.ext.viewcode` looks at your Python object descriptions and tries to find the source files where the objects are contained. When found, a separate HTML page will be output for each module with a highlighted version of the source code, and a link will be added to all object descriptions that leads to the source code of the described object. A link back from the source to the description will also be inserted.


.. _style-guide-sphinx-extension-repoze-sphinx-autointerface:

`repoze.sphinx.autointerface <https://pypi.python.org/pypi/repoze.sphinx.autointerface>`_
-----------------------------------------------------------------------------------------

`repoze.sphinx.autointerface <https://pypi.python.org/pypi/repoze.sphinx.autointerface>`_ auto-generates API docs from Zope interfaces.


.. _style-guide-script-documentation:

Script documentation
--------------------

We currently use `sphinxcontrib-programoutput <https://pypi.python.org/pypi/sphinxcontrib-programoutput>`_ to generate program output of the p* scripts. It is no longer maintained and may cause future builds of the documentation to fail.

.. todo::

    See `issue #2804 <https://github.com/Pylons/pyramid/issues/2804>`_ for further discussion.
