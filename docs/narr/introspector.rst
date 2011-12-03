.. index::
   single: introspection
   single: introspector

.. _using_introspection:

Pyramid Configuration Introspection
===================================

When Pyramid starts up, each call to a :term:`configuration directive` causes
one or more :term:`introspectable` objects to be registered with an
:term:`introspector`.  This introspector can be queried by application code
to obtain information about the configuration of the running application.
This feature is useful for debug toolbars, command-line scripts which show
some aspect of configuration, and for runtime reporting of startup-time
configuration settings.

Using the Introspector
----------------------

Here's an example of using Pyramid's introspector:

.. code-block:: python
   :linenos:

    from pyramid.view import view_config
    from pyramid.response import Response

    @view_config(route_name='foo')
    @view_config(route_name='bar')
    def route_accepts(request):
        introspector = request.registry.introspector
        route_name = request.matched_route.name
        route_intr = introspector.get('routes', route_name)
        return Response(str(route_intr['accept']))

This view will return a response that contains the "accept" argument provided
to the ``add_route`` method of the route which matched when the view was
called.  It used the :meth:`pyramid.interfaces.IIntrospector.get` method to
return an introspectable in the category ``routes`` with a
:term:`discriminator` equal to the matched route name.  It then used the
returned introspectable to obtain an "accept" value.

The introspector has a number of other query-related methods: see
:class:`pyramid.interfaces.IIntrospector` for more information.  The
introspectable returned by the query methods of the introspector has methods
and attributes described by :class:`pyramid.interfaces.IIntrospectable`.

Concrete Introspection Categories
---------------------------------

This is a list of concrete introspection categories provided by Pyramid.

``subscribers``

``response adapters``

``asset overrides``

``root factories``

``session factory``

``request factory``

``locale negotiator``

``translation directories``

``renderer factories``

``routes``

``authentication policy``

``authorization policy``

``default permission``

``tweens (implicit)``

``views``

``templates``

``permissions``

``view mapper``

