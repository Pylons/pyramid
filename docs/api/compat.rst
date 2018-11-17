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
