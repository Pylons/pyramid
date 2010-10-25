.. _chameleon_zpt_module:

:mod:`pyramid.chameleon_zpt`
-------------------------------

.. automodule:: pyramid.chameleon_zpt

  .. autofunction:: get_template

  .. autofunction:: render_template

  .. autofunction:: render_template_to_response

These APIs will work against files which supply template text which
matches the :term:`ZPT` specification.

The API of :mod:`pyramid.chameleon_zpt` is identical to that of
:mod:`pyramid.chameleon_text`; only its import location is
different.  If you need to import an API functions from this module as
well as the :mod:`pyramid.chameleon_text` module within the same
view file, use the ``as`` feature of the Python import statement,
e.g.:

.. code-block:: python
   :linenos:

   from pyramid.chameleon_zpt import render_template as zpt_render
   from pyramid.chameleon_text import render_template as text_render
