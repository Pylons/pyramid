.. _chameleon_zpt_module:

:mod:`repoze.bfg.chameleon_zpt`
-------------------------------

.. automodule:: repoze.bfg.chameleon_zpt

  .. autofunction:: get_template

  .. autofunction:: render_template

  .. autofunction:: render_template_to_response

These APIs will work against files which supply template text which
matches the :term:`ZPT` specification.

The API of :mod:`repoze.bfg.chameleon_zpt` is identical to that of
:mod:`repoze.bfg.chameleon_text`; only its import location is
different.  If you need to import an API functions from this module as
well as the :mod:`repoze.bfg.chameleon_text` module within the same
view file, use the ``as`` feature of the Python import statement,
e.g.:

.. code-block:: python
   :linenos:

   from repoze.bfg.chameleon_zpt import render_template as zpt_render
   from repoze.bfg.chameleon_text import render_template as text_render
