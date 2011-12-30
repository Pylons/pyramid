.. _request_module:

:mod:`pyramid.request`
---------------------------

.. module:: pyramid.request

.. autoclass:: Request
   :members:
   :inherited-members:
   :exclude-members: add_response_callback, add_finished_callback,
                     route_url, route_path, current_route_url,
                     current_route_path, static_url, static_path,
                     model_url, resource_url, set_property

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

   .. attribute:: exc_info

     If an exception was raised by a :term:`root factory` or a :term:`view
     callable`, or at various other points where :app:`Pyramid` executes
     user-defined code during the processing of a request, result of
     ``sys.exc_info()`` will be available as the ``exc_info`` attribute of
     the request within a :term:`exception view`, a :term:`response callback`
     or a :term:`finished callback`.  If no exception occurred, the value of
     ``request.exc_info`` will be ``None`` within response and finished
     callbacks.

   .. attribute:: response

     This attribute is actually a "reified" property which returns an
     instance of the :class:`pyramid.response.Response` class.  The response
     object returned does not exist until this attribute is accessed.  Once
     it is accessed, subsequent accesses to this request object will return
     the same :class:`~pyramid.response.Response` object.

     The ``request.response`` API can is used by renderers.  A render obtains
     the response object it will return from a view that uses that renderer
     by accessing ``request.response``.  Therefore, it's possible to use the
     ``request.response`` API to set up a response object with "the right"
     attributes (e.g. by calling ``request.response.set_cookie(...)`` or
     ``request.response.content_type = 'text/plain'``, etc) within a view
     that uses a renderer.  For example, within a view that uses a
     :term:`renderer`::

         response = request.response
         response.set_cookie('mycookie', 'mine, all mine!')
         return {'text':'Value that will be used by the renderer'}

     Mutations to this response object will be preserved in the response sent
     to the client after rendering.  For more information about using
     ``request.response`` in conjunction with a renderer, see
     :ref:`request_response_attr`.

     Non-renderer code can also make use of request.response instead of
     creating a response "by hand".  For example, in view code::

        response = request.response
        response.body = 'Hello!'
        response.content_type = 'text/plain'
        return response

     Note that the response in this circumstance is not "global"; it still
     must be returned from the view code if a renderer is not used.

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

   .. automethod:: current_route_url

   .. automethod:: current_route_path

   .. automethod:: static_url

   .. automethod:: static_path

   .. automethod:: resource_url

   .. attribute::  response_*

      In Pyramid 1.0, you could set attributes on a
      :class:`pyramid.request.Request` which influenced the behavor of
      *rendered* responses (views which use a :term:`renderer` and which
      don't directly return a response).  These attributes began with
      ``response_``, such as ``response_headerlist``. If you needed to
      influence response values from a view that uses a renderer (such as the
      status code, a header, the content type, etc) you would set these
      attributes.  See :ref:`response_prefixed_attrs` for further discussion.
      As of Pyramid 1.1, assignment to ``response_*`` attrs are deprecated.
      Assigning to one is still supported but will cause a deprecation
      warning to be emitted, and eventually the feature will be removed.  For
      new code, instead of assigning ``response_*`` attributes to the
      request, use API of the the :attr:`pyramid.request.Request.response`
      object (exposed to view code as ``request.response``) to influence
      rendered response behavior.

   .. attribute:: json_body

       This property will return the JSON-decoded variant of the request
       body.  If the request body is not well-formed JSON, or there is no
       body associated with this request, this property will raise an
       exception.  See also :ref:`request_json_body`.

   .. method:: set_property(func, name=None, reify=False)

       .. versionadded:: 1.3

       Add a callable or a property descriptor to the request instance.

       Properties, unlike attributes, are lazily evaluated by executing
       an underlying callable when accessed. They can be useful for
       adding features to an object without any cost if those features
       go unused.

       A property may also be reified via the
       :class:`pyramid.decorator.reify` decorator by setting
       ``reify=True``, allowing the result of the evaluation to be
       cached. Thus the value of the property is only computed once for
       the lifetime of the object.

       ``func`` can either be a callable that accepts the request as
       its single positional parameter, or it can be a property
       descriptor.

       If the ``func`` is a property descriptor a ``ValueError`` will
       be raised if ``name`` is ``None`` or ``reify`` is ``True``.

       If ``name`` is None, the name of the property will be computed
       from the name of the ``func``.

       .. code-block:: python
          :linenos:

          def _connect(request):
              conn = request.registry.dbsession()
              def cleanup(_):
                  conn.close()
              request.add_finished_callback(cleanup)
              return conn

          @subscriber(NewRequest)
          def new_request(event):
              request = event.request
              request.set_property(_connect, 'db', reify=True)

       The subscriber doesn't actually connect to the database, it just
       provides the API which, when accessed via ``request.db``, will
       create the connection. Thanks to reify, only one connection is
       made per-request even if ``request.db`` is accessed many times.

       This pattern provides a way to augment the ``request`` object
       without having to subclass it, which can be useful for extension
       authors.

.. note::

   For information about the API of a :term:`multidict` structure (such as
   that used as ``request.GET``, ``request.POST``, and ``request.params``),
   see :class:`pyramid.interfaces.IMultiDict`.

