.. _chameleon_text_module:

:mod:`repoze.bfg.chameleon_text`
----------------------------------

.. automodule:: repoze.bfg.chameleon_text

  .. autofunction:: get_template

  .. autofunction:: render_template

  .. autofunction:: render_template_to_response

These APIs will will work against template files which contain simple
``${Genshi}`` - style replacement markers.

The API of :mod:`repoze.bfg.chameleon_text` is identical to that of
:mod:`repoze.bfg.chameleon_zpt`; only its import location is
different.  If you need to import an API functions from this module as
well as the :mod:`repoze.bfg.chameleon_zpt` module within the same
view file, use the ``as`` feature of the Python import statement,
e.g.:

.. code-block:: python
   :linenos:

   from repoze.bfg.chameleon_zpt import render_template as zpt_render
   from repoze.bfg.chameleon_text import render_template as text_render



