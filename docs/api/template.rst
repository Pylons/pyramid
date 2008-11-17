.. _template_module:

:mod:`repoze.bfg` Built-in Templating Facilties
===============================================

Four templating facilities are provided by :mod:`repoze.bfg` "out of
the box": :term:`ZPT` -style, :term:`Genshi` -style, text templating,
and :term:`XSLT` templating.

ZPT-style, Genshi-style, and text templates are in :mod:`repoze.bfg`
are supported by the :term:`Chameleon` (nee :term:`z3c.pt`) templating
engine, which contains alternate implementations of both the ZPT and
Genshi language specifications.

XSLT templating is supported by the use of :term:`lxml`.

Below is API documentation for each of those facilities.  Each
facility is similar to the other, but to use a particular facility,
you must import the API function from a specific module.  For
instance, to render a ZPT-style template to a response, you would
import the ``render_template_to_response`` function from
``repoze.bfg.chameleon_zpt`` while you would import
``render_template_to_response`` from ``repoze.bfg.chameleon_genshi``
in order to render a Genshi-style template to a response.  While these
functions have the same name, each will only operate on template files
that match the style in which the template file itself is written.  If
you need to import API functions from two templating facilities within
the same module, use the ``as`` feature of the Python import
statement, e.g.:

.. code-block:: python

  from repoze.chameleon_zpt import render_template as zpt_render
  from repoze.chameleon_genshi import render_template as genshi_render
  from repoze.chameleon_text import render_template as text_render

:mod:`repoze.bfg.chameleon_zpt`
-------------------------------

.. automodule:: repoze.bfg.chameleon_zpt

  .. autofunction:: get_template

  .. autofunction:: render_template

  .. autofunction:: render_template_to_response

.. note:: For backwards compatibility purposes, these functions may
          also be imported from ``repoze.bfg.template``.

:mod:`repoze.bfg.chameleon_genshi`
----------------------------------

.. automodule:: repoze.bfg.chameleon_genshi

  .. autofunction:: get_template

  .. autofunction:: render_template

  .. autofunction:: render_template_to_response

:mod:`repoze.bfg.chameleon_text`
----------------------------------

.. automodule:: repoze.bfg.chameleon_text

  .. autofunction:: get_template

  .. autofunction:: render_template

  .. autofunction:: render_template_to_response

:mod:`repoze.bfg.xslt`
----------------------

.. automodule:: repoze.bfg.xslt

  .. autofunction:: get_transform

  .. autofunction:: render_transform

  .. autofunction:: render_transform_to_response

.. note:: For backwards compatibility purposes, these functions may
          also be imported from ``repoze.bfg.template``.

