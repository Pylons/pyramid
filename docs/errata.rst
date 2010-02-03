Errata for "The repoze.bfg Web Framework, Version 1.2" Printed Edition
======================================================================

pp. 66
------

The sentence:

  "Technically, traversal is a repoze.bfg subsystem that is separated
  from traversal entirely."

Should read:

  "Technically, view lookup is a repoze.bfg subsystem that is
  separated from traversal entirely."


pp. 103
-------

The sentence:

  "The Context Finding and View Lookup (pp. 57) describes how a
  context and a view name are computed using information from the
  request. "

Should read:

  "The chapter named Context Finding and View Lookup (pp. 57)
  describes how, using information from the request, a context and a
  view name are computed ."

pp. 106
-------

The enumeration:

  2. Classes that have an ``__init__`` method that accepts ``context,
     request``, e.g.:

     .. code-block:: python
        :linenos:

        from webob import Response

        class view(object):
            def __init__(self, context, request):
                return Response('OK')

Should read:

  2. Classes that have an ``__init__`` method that accepts ``context,
     request``, and a ``__call__`` which accepts no arguments, e.g.:

     .. code-block:: python
        :linenos:

        from webob import Response

        class view(object):
            def __init__(self, context, request):
                self.context = context
                self.request = request

            def __call__(self):
                return Response('OK')

pp. 98
------

The section entitled "Global View Configurations May Match When a
Route-Specific View Configuration Doesn't" is incorrect.  The entire
section should be disregarded.

pp. 99
------

The section entitled "context Type Registrations Bind More Tightly
Than request Type Registrations" is incorrect.  The entire section
should be disgregarded.

pp. 83
-------

A "route configuration" argument was omitted:

  ``use_global_views``
    When a request matches this route, and view lookup cannot find a
    view which has a 'route_name' predicate argument that matches the
    route, try to fall back to using a view that otherwise matches the
    context, request, and view name (but does not match the route name
    predicate).

