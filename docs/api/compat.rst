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
        
   .. attribute:: configparser

      The ``configparser`` module.

   .. function:: escape(v)

      The ``html.escape`` function.

   .. function:: exec_(code, globs=None, locs=None)

      Exec code.

   .. attribute:: im_func

      The string value ``__func__``.

   .. function:: input_(v)

      The ``input`` function.

   .. function:: is_nonstr_iter(v)

      Return ``True`` if ``v`` is a non-``str``.

   .. function:: iteritems_(d)

      Return ``d.items()``.

   .. function:: itervalues_(d)

      Return ``d.values()``.

   .. function:: iterkeys_(d)

      Return ``d.keys()``.

   .. attribute:: long

      Long type ``int``.

   .. function:: map_(v)

      Return ``list(map(v))``.

   .. attribute:: pickle

       ``cPickle`` module if it exists, ``pickle`` module otherwise.

   .. attribute:: PYPY

      ``True`` if running on PyPy, ``False`` otherwise.

   .. function:: reraise(tp, value, tb=None)

      Reraise an exception ``reraise(*sys.exc_info())``.

   .. attribute:: SimpleCookie

      ``http.cookies.SimpleCookie`` module.

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

