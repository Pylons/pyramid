.. _renderers_module:

:mod:`pyramid.renderers`
---------------------------

.. module:: pyramid.renderers

.. autofunction:: get_renderer

.. autofunction:: render

.. autofunction:: render_to_response

.. autoclass:: JSON

   .. automethod:: add_adapter

.. autoclass:: JSONP

   .. automethod:: add_adapter

.. attribute:: null_renderer

   An object that can be used in advanced integration cases as input to the
   view configuration ``renderer=`` argument.  When the null renderer is used
   as a view renderer argument, Pyramid avoids converting the view callable
   result into a Response object.  This is useful if you want to reuse the
   view configuration and lookup machinery outside the context of its use by
   the Pyramid router.

