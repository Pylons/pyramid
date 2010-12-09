.. _static_directive:

``static``
----------

Use of the ``static`` ZCML directive or allows you to serve static
resources (such as JavaScript and CSS files) within a
:app:`Pyramid` application. This mechanism makes static files
available at a name relative to the application root URL.

Attributes
~~~~~~~~~~

``name``
  The (application-root-relative) URL prefix of the static directory.
  For example, to serve static files from ``/static`` in most
  applications, you would provide a ``name`` of ``static``.

``path``
  A path to a directory on disk where the static files live.  This
  path may either be 1) absolute (e.g. ``/foo/bar/baz``) 2)
  Python-package-relative (e.g. (``packagename:foo/bar/baz``) or 3)
  relative to the package directory in which the ZCML file which
  contains the directive (e.g. ``foo/bar/baz``).

``cache_max_age``
  The number of seconds that the static resource can be cached, as
  represented in the returned response's ``Expires`` and/or
  ``Cache-Control`` headers, when any static file is served from this
  directive.  This defaults to 3600 (5 minutes).  Optional.

``permission``
  Used to specify the :term:`permission` required by a user to execute
  this static view.  This value defaults to the string
  ``__no_permission_required__``.  The ``__no_permission_required__``
  string is a special sentinel which indicates that, even if a
  :term:`default permission` exists for the current application, the
  static view should be renderered to completely anonymous users.
  This default value is permissive because, in most web apps, static
  resources seldom need protection from viewing.  You should use this
  option only if you register a static view which points at a
  directory that contains resources which should be shown only if the
  calling user has (according to the :term:`authorization policy`) a
  particular permission.

Examples
~~~~~~~~

.. topic:: Serving Static Files from an Absolute Path

   .. code-block:: xml
      :linenos:

      <static
         name="static"
         path="/var/www/static"
         />

.. topic:: Serving Static Files from a Package-Relative Path

   .. code-block:: xml
      :linenos:

      <static
         name="static"
         path="some_package:a/b/c/static"
         />

.. topic:: Serving Static Files from a Current-Package-Relative Path

   .. code-block:: xml
      :linenos:

      <static
         name="static"
         path="static_files"
         />

Alternatives
~~~~~~~~~~~~

:meth:`pyramid.config.Configurator.add_static_view` can also
be used to add a static view.

See Also
~~~~~~~~

See also :ref:`static_resources_section` and
:ref:`generating_static_resource_urls`.
