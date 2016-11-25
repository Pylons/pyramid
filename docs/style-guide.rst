.. _style-guide:

Style Guide
===========

.. admonition:: description

   This chapter describes how to edit, update, and build the :app:`Pyramid` documentation. For coding style guidelines, see `Coding Style <http://docs.pylonsproject.org/en/latest/community/codestyle.html#coding-style>`_.


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


.. _style-guide-section-structure:

Section structure
-----------------

Each section, or a subdirectory of reST files, such as a tutorial, must contain an ``index.rst`` file. ``index.rst`` must contain the following.

- A section heading. This will be visible in the table of contents.
- A single paragraph describing this section.
- A Sphinx ``toctree`` directive, with a ``maxdepth`` of 2. Each ``.rst`` file in the folder should be linked to this ``toctree``.

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

- No trailing white spaces.
- Always use a line feed or carriage return at the end of a file.


.. _style-guide-indentation:

Indentation
^^^^^^^^^^^

- Indent using four spaces.
- Do not use tabs to indent.


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

- =, for sections
- -, for subsections
- ^, for subsubsections
- ", for paragraphs

As individual files do not have so-called "parts" or "chapters", the headings would be underlined with characters as shown.

    .. code-block:: rst

        Heading Level 1
        ===============

        Heading Level 2
        ---------------

        Heading Level 3
        ^^^^^^^^^^^^^^^

        Heading Level 4
        ```````````````

The above code renders as follows.

Heading Level 1
===============

Heading Level 2
---------------

Heading Level 3
^^^^^^^^^^^^^^^

Heading Level 4
```````````````

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

To link to pages within this documentation:

.. code-block:: rst

    :doc:`quick_tour`

The above code renders as follows.

:doc:`quick_tour`

To link to a section within a page in this documentation:

.. code-block:: rst

    :ref:`quick_tour`

The above code renders as follows.

:ref:`quick_tour`

To link to pages configured via intersphinx:

.. code-block:: rst

    :ref:`Deform <deform:overview>`

The above code renders as follows.

:ref:`Deform <deform:overview>`


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

Code may be displayed in blocks or inline. You can include blocks of code from other source files. Blocks of code should use syntax highlighting.

.. seealso:: See also the Sphinx documentation for :ref:`Showing code examples <sphinx:code-examples>`.


.. _style-guide-syntax-highlighting:

Syntax highlighting
```````````````````

Sphinx does syntax highlighting of code blocks using the `Pygments <http://pygments.org/>`_ library.

Do not use two colons "::" at the end of a line, followed by a blank line, then indented code. Always specify the language to be used for syntax highlighting by using the ``code-block`` directive and indenting the code.

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


.. _style-guide-long-commands:

Displaying long commands
````````````````````````

When a command that should be typed on one line is too long to fit on the displayed width of a page, the backslash character ``\`` is used to indicate that the subsequent printed line should be part of the command:

.. code-block:: rst

    .. code-block:: bash

        $ $VENV/bin/py.test tutorial/tests.py --cov-report term-missing \
            --cov=tutorial -q


.. _style-guide-code-block-options:

Code block options
``````````````````

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

Code blocks may be given a caption, which may serve as a filename or other description, using the ``caption`` option. They may also be given a ``name`` option, providing an implicit target name that can be referenced by using ``ref``.

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

The above code renders as follows. As you can see, ``lineno-start`` is not altogether meaningful.

.. code-block:: python
    :lineno-start: 2

    if "foo" == "bar":
        # This is Python code
        pass


.. _style-guide-includes:

Includes
````````

Longer displays of verbatim text may be included by storing the example text in an external file containing only plain text or code. The file may be included using the ``literalinclude`` directive. The file name follows the conventions of :ref:`style-guide-file-conventions`.

.. code-block:: rst

    .. literalinclude:: narr/helloworld.py
        :language: python

The above code renders as follows.

.. literalinclude:: narr/helloworld.py
    :language: python

Like code blocks, ``literalinclude`` supports the following options.

- ``language`` to select a language for syntax highlighting
- ``linenos`` to switch on line numbers
- ``lineno-start`` to specify the starting number to use for line numbering
- ``emphasize-lines`` to emphasize particular lines

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
```````````

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
    3      - Second column of row 3.

           - Second item in bullet
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
3      - Second column of row 3.

       - Second item in bullet
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
    | body row 3             | Cells may  | - Table cells       |
    +------------------------+ span rows. | - contain           |
    | body row 4             |            | - body elements.    |
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
| body row 3             | Cells may  | - Table cells       |
+------------------------+ span rows. | - contain           |
| body row 4             |            | - body elements.    |
+------------------------+------------+---------------------+


.. _style-guide-danger-errors:

Danger and errors
^^^^^^^^^^^^^^^^^

Danger and errors represent critical information related to a topic or concept, and should recommend to the user "don't do this dangerous thing". ``danger`` and ``error`` appear similarly when rendered, but the HTML generated has the appropriate semantic context.

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


.. _style-guide-python:

Python modules, classes, methods, and functions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

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

.. seealso::

    See also the Sphinx documentation for the :ref:`reStructuredText Primer <sphinx:rst-primer>`.



:app:`Pyramid`

:ref:`i18n_chapter`

References to glossary terms are presented using the following style:

  :term:`Pylons`

Glossary terms appear in the Glossary

.. glossary:: :sorted:

References to sections and chapters are presented using the following style:

  :ref:`traversal_chapter`


API documentation
-----------------

.. automodule:: pyramid.i18n

.. .. autoclass:: TranslationString

.. .. autofunction:: TranslationStringFactory

