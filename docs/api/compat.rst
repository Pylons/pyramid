.. _compat_module:

:mod:`pyramid.compat`
----------------------

The ``pyramid.compat`` module provides platform and version compatibility for
Pyramid and its add-ons across Python platform and version differences.  APIs
will be removed from this module over time as Pyramid ceases to support
systems which require compatibility imports.

.. automodule:: pyramid.compat

   .. autofunction:: ascii_native_

   .. autofunction:: bytes_
        
   .. attribute:: im_func

      The string value ``__func__``.

   .. attribute:: long

      Long type ``int``.

   .. attribute:: PYPY

      ``True`` if running on PyPy, ``False`` otherwise.

   .. autofunction:: text_

   .. autofunction:: native_

   .. attribute:: urlparse

      ``urllib.parse``

   .. attribute:: url_quote

      ``urllib.parse.quote``

   .. attribute:: url_quote_plus

      ``urllib.parse.quote_plus``

   .. attribute:: url_unquote

      ``urllib.parse.unquote``

   .. attribute:: url_encode

      ``urllib.parse.urlencode``

   .. attribute:: url_open

      ``urllib.request.urlopen``

   .. function:: url_unquote_text(v, encoding='utf-8', errors='replace')

      Return the result of ``urllib.parse.unquote``.

   .. function:: url_unquote_native(v, encoding='utf-8', errors='replace')

      Return the result of ``urllib.parse.unquote``.

