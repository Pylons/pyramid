.. index::
   single: request processing
   single: request
   single: router
   single: request lifecycle

.. _router_chapter:

Request Processing
==================

.. image:: ../_static/pyramid_request_processing.*
   :alt: Request Processing

Once a :app:`Pyramid` application is up and running, it is ready to accept
requests and return responses.  What happens from the time a :term:`WSGI`
request enters a :app:`Pyramid` application through to the point that
:app:`Pyramid` hands off a response back to WSGI for upstream processing?

#. A user initiates a request from their browser to the hostname and port
   number of the WSGI server used by the :app:`Pyramid` application.

#. The WSGI server used by the :app:`Pyramid` application passes the WSGI
   environment to the ``__call__`` method of the :app:`Pyramid` :term:`router`
   object.

#. A :term:`request` object is created based on the WSGI environment.

#. The :term:`application registry` and the :term:`request` object created in
   the last step are pushed on to the :term:`thread local` stack that
   :app:`Pyramid` uses to allow the functions named
   :func:`~pyramid.threadlocal.get_current_request` and
   :func:`~pyramid.threadlocal.get_current_registry` to work.

#. A :class:`~pyramid.events.NewRequest` :term:`event` is sent to any
   subscribers.

#. If any :term:`route` has been defined within application configuration, the
   :app:`Pyramid` :term:`router` calls a :term:`URL dispatch` "route mapper."
   The job of the mapper is to examine the request to determine whether any
   user-defined :term:`route` matches the current WSGI environment.  The
   :term:`router` passes the request as an argument to the mapper.

#. If any route matches, the route mapper adds the attributes ``matchdict``
   and ``matched_route`` to the request object. The former contains a
   dictionary representing the matched dynamic elements of the request's
   ``PATH_INFO`` value, and the latter contains the
   :class:`~pyramid.interfaces.IRoute` object representing the route which
   matched.

#. A :class:`~pyramid.events.BeforeTraversal` :term:`event` is sent to any
   subscribers.

#. Continuing, if any route matches, the root object associated with the found
   route is generated. If the :term:`route configuration` which matched has an
   associated ``factory`` argument, then this factory is used to generate the
   root object; otherwise a default :term:`root factory` is used.

   However, if no route matches, and if a ``root_factory`` argument was passed
   to the :term:`Configurator` constructor, that callable is used to generate
   the root object. If the ``root_factory`` argument passed to the
   Configurator constructor was ``None``, a default root factory is used to
   generate a root object.

#. The :app:`Pyramid` router calls a "traverser" function with the root object
   and the request.  The traverser function attempts to traverse the root
   object (using any existing ``__getitem__`` on the root object and
   subobjects) to find a :term:`context`.  If the root object has no
   ``__getitem__`` method, the root itself is assumed to be the context. The
   exact traversal algorithm is described in :ref:`traversal_chapter`. The
   traverser function returns a dictionary, which contains a :term:`context`
   and a :term:`view name` as well as other ancillary information.

#. The request is decorated with various names returned from the traverser
   (such as ``context``, ``view_name``, and so forth), so they can be accessed
   via, for example, ``request.context`` within :term:`view` code.

#. A :class:`~pyramid.events.ContextFound` :term:`event` is sent to any
   subscribers.

#. :app:`Pyramid` looks up a :term:`view` callable using the context, the
   request, and the view name.  If a view callable doesn't exist for this
   combination of objects (based on the type of the context, the type of the
   request, and the value of the view name, and any :term:`predicate`
   attributes applied to the view configuration), :app:`Pyramid` raises a
   :class:`~pyramid.httpexceptions.HTTPNotFound` exception, which is meant to
   be caught by a surrounding :term:`exception view`.

#. If a view callable was found, :app:`Pyramid` attempts to call it.  If an
   :term:`authorization policy` is in use, and the view configuration is
   protected by a :term:`permission`, :app:`Pyramid` determines whether the
   view callable being asked for can be executed by the requesting user based
   on credential information in the request and security information attached
   to the context.  If the view execution is allowed, :app:`Pyramid` calls the
   view callable to obtain a response.  If view execution is forbidden,
   :app:`Pyramid` raises a :class:`~pyramid.httpexceptions.HTTPForbidden`
   exception.

#. If any exception is raised within a :term:`root factory`, by
   :term:`traversal`, by a :term:`view callable`, or by :app:`Pyramid` itself
   (such as when it raises :class:`~pyramid.httpexceptions.HTTPNotFound` or
   :class:`~pyramid.httpexceptions.HTTPForbidden`), the router catches the
   exception, and attaches it to the request as the ``exception`` attribute.
   It then attempts to find a :term:`exception view` for the exception that was
   caught.  If it finds an exception view callable, that callable is called,
   and is presumed to generate a response.  If an :term:`exception view` that
   matches the exception cannot be found, the exception is reraised.

#. The following steps occur only when a :term:`response` could be successfully
   generated by a normal :term:`view callable` or an :term:`exception view`
   callable.  :app:`Pyramid` will attempt to execute any :term:`response
   callback` functions attached via
   :meth:`~pyramid.request.Request.add_response_callback`. A
   :class:`~pyramid.events.NewResponse` :term:`event` is then sent to any
   subscribers.  The response object's ``__call__`` method is then used to
   generate a WSGI response.  The response is sent back to the upstream WSGI
   server.

#. :app:`Pyramid` will attempt to execute any :term:`finished callback`
   functions attached via
   :meth:`~pyramid.request.Request.add_finished_callback`.

#. The :term:`thread local` stack is popped.

.. image:: ../_static/pyramid_router.*
   :alt: Pyramid Router

This is a very high-level overview that leaves out various details.  For more
detail about subsystems invoked by the :app:`Pyramid` router, such as
traversal, URL dispatch, views, and event processing, see
:ref:`urldispatch_chapter`, :ref:`views_chapter`, and :ref:`events_chapter`.
