Typographical Conventions
=========================

Literals, filenames and function arguments are presented using the
following style:

  ``argument1``

Warnings, which represent limitations and need-to-know information
related to a topic or concept are presented in the following style:

  .. warning::

     This is a warning.

Notes, which represent additional information related to a topic or
concept are presented in the following style:

  .. note::

     This is a note.

We present Python method names using the following style:

  :meth:`Python.method_name`

We present Python class names, module names, attributes and global
variables using the following style:

  :class:`Python.class_module_or_attribute.name`

References to glossary terms are presented using the following style:

  :term:`Repoze`

URLs are presented using the following style:

  `Repoze <http://repoze.org>`_

References to sections and chapters are presented using the following
style:

  :ref:`traversal_chapter`

Python code blocks are presented in the following style:

  .. code-block:: python
     :linenos:

     def foo(abc):
         pass

Blocks of XML markup are presented in the following style:

  .. code-block:: xml
     :linenos:

     <root>
       <!-- ... more XML .. -->
     </root>

When a command that should be typed on one line is too long to fit on
a page, the backslash ``\`` is used to indicate that the following
printed line should actually be part of the command:

  .. code-block:: text

     c:\bigfntut\tutorial> ..\Scripts\nosetests --cover-package=tutorial \
           --cover-erase --with-coverage

A sidebar, which presents a concept tangentially related to content
discussed on a page, is rendered like so:

.. sidebar:: This is a sidebar

   Sidebar information.

In printed versions of this book, Python modules classes, methods,
functions, and attributes that are part of the :mod:`repoze.bfg`
module are referenced in paragraph text.  These are contracted to omit
the ``repoze.bfg`` prefix to reduce redundancy and increase
readability.  Therefore, where you might expect:

  .. code-block:: text

     repoze.bfg.configuration.Configurator.add_view (pp. XXX)

Instead a contracted version will be rendered:

  .. code-block:: text

     configuration.Configurator.add_view (pp. XXX)

