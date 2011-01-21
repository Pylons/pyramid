.. _request_module:

:mod:`pyramid.request`
---------------------------

.. module:: pyramid.request

.. autoclass:: Request
   :members:
   :inherited-members:

   .. attribute:: context

     The :term:`context` will be available as the ``context``
     attribute of the :term:`request` object.  It will be the context
     object implied by the current request.  See
     :ref:`traversal_chapter` for information about context objects.

   .. attribute:: registry

     The :term:`application registry` will be available as the
     ``registry`` attribute of the :term:`request` object.  See
     :ref:`zca_chapter` for more information about the application
     registry.

   .. attribute:: root

      The :term:`root` object will be available as the ``root``
      attribute of the :term:`request` object.  It will be the resource
      object at which traversal started (the root).  See
      :ref:`traversal_chapter` for information about root objects.

   .. attribute:: subpath

      The traversal :term:`subpath` will be available as the
      ``subpath`` attribute of the :term:`request` object.  It will
      be a sequence containing zero or more elements (which will be
      Unicode objects).  See :ref:`traversal_chapter` for information
      about the subpath.

   .. attribute:: traversed

      The "traversal path" will be available as the ``traversed``
      attribute of the :term:`request` object.  It will be a sequence
      representing the ordered set of names that were used to
      traverse to the :term:`context`, not including the view name or
      subpath.  If there is a virtual root associated with the
      request, the virtual root path is included within the traversal
      path.  See :ref:`traversal_chapter` for more information.

   .. attribute:: view_name

      The :term:`view name` will be available as the ``view_name``
      attribute of the :term:`request` object.  It will be a single
      string (possibly the empty string if we're rendering a default
      view).  See :ref:`traversal_chapter` for information about view
      names.

   .. attribute:: virtual_root

      The :term:`virtual root` will be available as the
      ``virtual_root`` attribute of the :term:`request` object.  It
      will be the virtual root object implied by the current request.
      See :ref:`vhosting_chapter` for more information about virtual
      roots.

   .. attribute:: virtual_root_path

      The  :term:`virtual  root`  *path*  will be  available  as  the
      ``virtual_root_path`` attribute  of the :term:`request` object.
      It will  be a  sequence representing the  ordered set  of names
      that were  used to  traverse to the  virtual root  object.  See
      :ref:`vhosting_chapter`  for  more  information  about  virtual
      roots.

   .. attribute:: exception

     If an exception was raised by a :term:`root factory` or a
     :term:`view callable`, or at various other points where
     :app:`Pyramid` executes user-defined code during the
     processing of a request, the exception object which was caught
     will be available as the ``exception`` attribute of the request
     within a :term:`exception view`, a :term:`response callback` or a
     :term:`finished callback`.  If no exception occurred, the value
     of ``request.exception`` will be ``None`` within response and
     finished callbacks.

   .. attribute:: session

     If a :term:`session factory` has been configured, this attribute
     will represent the current user's :term:`session` object.  If a
     session factory *has not* been configured, requesting the
     ``request.session`` attribute will cause a
     :class:`pyramid.exceptions.ConfigurationError` to be raised.

   .. attribute:: tmpl_context

     The template context for Pylons-style applications.

   .. attribute:: matchdict

      If a :term:`route` has matched during this request, this attribute will
      be a dictionary containing the values matched by the URL pattern
      associated with the route.  If a route has not matched during this
      request, the value of this attribute will be ``None``. See
      :ref:`matchdict`.

   .. attribute:: matched_route

      If a :term:`route` has matched during this request, this attribute will
      be an obect representing the route matched by the URL pattern
      associated with the route.  If a route has not matched during this
      request, the value of this attribute will be ``None``. See
      :ref:`matched_route`.

   .. automethod:: add_response_callback

   .. automethod:: add_finished_callback

   .. automethod:: route_url

   .. automethod:: route_path

   .. automethod:: resource_url

   .. automethod:: static_url

