.. _compat_module:

:mod:`pyramid.compat`
----------------------

The ``pyramid.compat`` module provides platform and version compatibility for
Pyramid and its add-ons across Python platform and version differences.  APIs
will be removed from this module over time as Pyramid ceases to support
systems which require compatibility imports.

.. automodule:: pyramid.compat

   .. autofunction:: ascii_native_

   .. attribute:: binary_type

        Binary type for this platform.  For Python 3, it's ``bytes``.  For
        Python 2, it's ``str``.

   .. autofunction:: bytes_
        
   .. attribute:: class_types

        Sequence of class types for this platform.  For Python 3, it's
        ``(type,)``.  For Python 2, it's ``(type, types.ClassType)``.

   .. attribute:: configparser

      On Python 2, the ``ConfigParser`` module, on Python 3, the
      ``configparser`` module.

   .. function:: escape(v)

      On Python 2, the ``cgi.escape`` function, on Python 3, the
      ``html.escape`` function.

   .. function:: exec_(code, globs=None, locs=None)

      Exec code in a compatible way on both Python 2 and 3.

   .. attribute:: im_func

      On Python 2, the string value ``im_func``, on Python 3, the string
      value ``__func__``.

   .. function:: input_(v)

      On Python 2, the ``raw_input`` function, on Python 3, the
      ``input`` function.

   .. attribute:: integer_types

        Sequence of integer types for this platform.  For Python 3, it's
        ``(int,)``.  For Python 2, it's ``(int, long)``.

   .. function:: is_nonstr_iter(v)

      Return ``True`` if ``v`` is a non-``str`` iterable on both Python 2 and
      Python 3.

   .. function:: iteritems_(d)

      Return ``d.items()`` on Python 3, ``d.iteritems()`` on Python 2.

   .. function:: itervalues_(d)

      Return ``d.values()`` on Python 3, ``d.itervalues()`` on Python 2.

   .. function:: iterkeys_(d)

      Return ``d.keys()`` on Python 3, ``d.iterkeys()`` on Python 2.

   .. attribute:: long

        Long type for this platform.  For Python 3, it's ``int``.  For
        Python 2, it's ``long``.

   .. function:: map_(v)

      Return ``list(map(v))`` on Python 3, ``map(v)`` on Python 2.

   .. attribute:: pickle

       ``cPickle`` module if it exists, ``pickle`` module otherwise.

   .. attribute:: PY3

      ``True`` if running on Python 3, ``False`` otherwise.

   .. attribute:: PYPY

      ``True`` if running on PyPy, ``False`` otherwise.

   .. function:: reraise(tp, value, tb=None)

      Reraise an exception in a compatible way on both Python 2 and Python 3,
      e.g. ``reraise(*sys.exc_info())``.

   .. attribute:: string_types

        Sequence of string types for this platform.  For Python 3, it's
        ``(str,)``.  For Python 2, it's ``(basestring,)``.

   .. attribute:: SimpleCookie

      On Python 2, the ``Cookie.SimpleCookie`` class, on Python 3, the
      ``http.cookies.SimpleCookie`` module.

   .. autofunction:: text_

   .. attribute:: text_type

        Text type for this platform.  For Python 3, it's ``str``.  For Python
        2, it's ``unicode``.

   .. autofunction:: native_

   .. attribute:: urlparse

      ``urlparse`` module on Python 2, ``urllib.parse`` module on Python 3.

   .. attribute:: url_quote

      ``urllib.quote`` function on Python 2, ``urllib.parse.quote`` function
      on Python 3.

   .. attribute:: url_quote_plus

      ``urllib.quote_plus`` function on Python 2, ``urllib.parse.quote_plus``
      function on Python 3.

   .. attribute:: url_unquote

      ``urllib.unquote`` function on Python 2, ``urllib.parse.unquote``
      function on Python 3.

   .. attribute:: url_encode

      ``urllib.urlencode`` function on Python 2, ``urllib.parse.urlencode``
      function on Python 3.

   .. attribute:: url_open

      ``urllib2.urlopen`` function on Python 2, ``urllib.request.urlopen``
      function on Python 3.

   .. function:: url_unquote_text(v, encoding='utf-8', errors='replace')

      On Python 2, return ``url_unquote(v).decode(encoding(encoding, errors))``;
      on Python 3, return the result of ``urllib.parse.unquote``.

   .. function:: url_unquote_native(v, encoding='utf-8', errors='replace')

      On Python 2, return ``native_(url_unquote_text_v, encoding, errors))``;
      on Python 3, return the result of ``urllib.parse.unquote``.

