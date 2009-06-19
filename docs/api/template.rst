.. _template_module:

:mod:`repoze.bfg` Built-in Templating Facilties
===============================================

Two templating facilities are provided by :mod:`repoze.bfg` "out of
the box": :term:`ZPT` -style and text templating.

ZPT-style and text templates are in :mod:`repoze.bfg` are supported by
the :term:`Chameleon` (nee :term:`z3c.pt`) templating engine, which
contains an alternate implementation of the ZPT language
specification.

Below is API documentation for each of those facilities.  Each
facility is similar to the other, but to use a particular facility,
you must import the API function from a specific module.  For
instance, to render a ZPT-style template to a response, you would
import the ``render_template_to_response`` function from
``repoze.bfg.chameleon_zpt`` while you would import
``render_template_to_response`` from ``repoze.bfg.chameleon_text`` in
order to render a text-style template to a response.  While these
functions have the same name, each will only operate on template files
that match the style in which the template file itself is written.  If
you need to import API functions from two templating facilities within
the same module, use the ``as`` feature of the Python import
statement, e.g.:

.. code-block:: python

  from repoze.chameleon_zpt import render_template as zpt_render
  from repoze.chameleon_text import render_template as text_render

:mod:`repoze.bfg.chameleon_zpt`
-------------------------------

.. automodule:: repoze.bfg.chameleon_zpt

  .. autofunction:: get_template

  .. autofunction:: render_template

  .. autofunction:: render_template_to_response

.. note:: For backwards compatibility purposes, these functions may
          also be imported from ``repoze.bfg.template``.

:mod:`repoze.bfg.chameleon_text`
----------------------------------

.. automodule:: repoze.bfg.chameleon_text

  .. autofunction:: get_template

  .. autofunction:: render_template

  .. autofunction:: render_template_to_response

