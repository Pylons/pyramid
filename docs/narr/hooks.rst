.. _hooks_chapter:

Using Hooks
===========

"Hooks" can be used to influence the behavior of the
:mod:`repoze.bfg` framework in various ways.

.. index::
   single: not found view

.. _changing_the_notfound_view:

Changing the Not Found View
---------------------------

When :mod:`repoze.bfg` can't map a URL to view code, it invokes a
:term:`not found view`, which is a :term:`view callable`. The view it
invokes can be customized through application configuration.  This
view can be configured via :term:`imperative configuration` or
:term:`ZCML`.

.. topic:: Using Imperative Configuration

   If your application uses :term:`imperative configuration`, you can
   replace the Not Found view by using the
   :meth:`repoze.bfg.configuration.Configurator.set_notfound_view`
   method:

   .. code-block:: python
      :linenos:

      import helloworld.views
      config.set_notfound_view(helloworld.views.notfound_view)

   Replace ``helloworld.views.notfound_view`` with a reference to the
   Python :term:`view callable` you want to use to represent the Not
   Found view.

.. topic:: Using ZCML

   If your application uses :term:`ZCML`, you can replace the Not Found
   view by placing something like the following ZCML in your
   ``configure.zcml`` file.

   .. code-block:: xml
      :linenos:

      <notfound 
          view="helloworld.views.notfound_view"/>

   Replace ``helloworld.views.notfound_view`` with the Python dotted name
   to the notfound view you want to use.

   Other attributes of the ``notfound`` directive are documented at
   :ref:`notfound_directive`.

Here's some sample code that implements a minimal NotFound view:

.. code-block:: python
   :linenos:

   from webob.exc import HTTPNotFound

   def notfound_view(request):
       return HTTPNotFound()

.. note:: When a NotFound view is invoked, it is passed a
   :term:`request`.  The ``environ`` attribute of the request is the
   WSGI environment.  Within the WSGI environ will be a key named
   ``repoze.bfg.message`` that has a value explaining why the not
   found error was raised.  This error will be different when the
   ``debug_notfound`` environment setting is true than it is when it
   is false.

.. index::
   single: forbidden view

.. _changing_the_forbidden_view:

Changing the Forbidden View
---------------------------

When :mod:`repoze.bfg` can't authorize execution of a view based on
the :term:`authorization policy` in use, it invokes a :term:`forbidden
view`.  The default forbidden response has a 401 status code and is
very plain, but it can be overridden as necessary using either
:term:`imperative configuration` or :term:`ZCML`:

.. topic:: Using Imperative Configuration

   If your application uses :term:`imperative configuration`, you can
   replace the Forbidden view by using the
   :meth:`repoze.bfg.configuration.Configurator.set_forbidden_view`
   method:

   .. code-block:: python
      :linenos:

      import helloworld.views
      config.set_forbiddden_view(helloworld.views.forbidden_view)

   Replace ``helloworld.views.forbidden_view`` with a reference to the
   Python :term:`view callable` you want to use to represent the
   Forbidden view.

.. topic:: Using ZCML

   If your application uses :term:`ZCML`, you can replace the
   Forbidden view by placing something like the following ZCML in your
   ``configure.zcml`` file.

   .. code-block:: xml
      :linenos:

      <forbidden
          view="helloworld.views.forbidden_view"/>


   Replace ``helloworld.views.forbidden_view`` with the Python
   dotted name to the forbidden view you want to use.

   Other attributes of the ``forbidden`` directive are documented at
   :ref:`forbidden_directive`.

Like any other view, the forbidden view must accept at least a
``request`` parameter, or both ``context`` and ``request``.  The
``context`` (available as ``request.context`` if you're using the
request-only view argument pattern) is the context found by the router
when the view invocation was denied.  The ``request`` is the current
:term:`request` representing the denied action.

Here's some sample code that implements a minimal forbidden view:

.. code-block:: python
   :linenos:

   from repoze.bfg.chameleon_zpt import render_template_to_response

   def forbidden_view(request):
       return render_template_to_response('templates/login_form.pt')

.. note:: When a forbidden view is invoked, it is passed the
   :term:`request` as the second argument.  An attribute of the
   request is ``environ``, which is the WSGI environment.  Within the
   WSGI environ will be a key named ``repoze.bfg.message`` that has a
   value explaining why the current view invocation was forbidden.
   This error will be different when the ``debug_authorization``
   environment setting is true than it is when it is false.

.. warning:: the default forbidden view sends a response with a ``401
   Unauthorized`` status code for backwards compatibility reasons.
   You can influence the status code of Forbidden responses by using
   an alternate forbidden view.  For example, it would make sense to
   return a response with a ``403 Forbidden`` status code.

.. index::
   single: traverser

.. _changing_the_traverser:

Changing the Traverser
----------------------

The default :term:`traversal` algorithm that BFG uses is explained in
:ref:`traversal_algorithm`.  Though it is rarely necessary, this
default algorithm can be swapped out selectively for a different
traversal pattern via configuration.

Use an ``adapter`` stanza in your application's ``configure.zcml`` to
change the default traverser:

.. code-block:: xml
   :linenos:

    <adapter
      factory="myapp.traversal.Traverser"
      provides="repoze.bfg.interfaces.ITraverser"
      for="*"
      />

In the example above, ``myapp.traversal.Traverser`` is assumed to be
a class that implements the following interface:

.. code-block:: python
   :linenos:

   class Traverser(object):
       def __init__(self, root):
           """ Accept the root object returned from the root factory """

       def __call__(self, request):
           """ Return a dictionary with (at least) the keys ``root``,
           ``context``, ``view_name``, ``subpath``, ``traversed``,
           ``virtual_root``, and ``virtual_root_path``.  These values are
           typically the result of an object graph traversal.  ``root``
           is the physical root object, ``context`` will be a model
           object, ``view_name`` will be the view name used (a Unicode
           name), ``subpath`` will be a sequence of Unicode names that
           followed the view name but were not traversed, ``traversed``
           will be a sequence of Unicode names that were traversed
           (including the virtual root path, if any) ``virtual_root``
           will be a model object representing the virtual root (or the
           physical root if traversal was not performed), and
           ``virtual_root_path`` will be a sequence representing the
           virtual root path (a sequence of Unicode names) or None if
           traversal was not performed.

           Extra keys for special purpose functionality can be added as
           necessary.

           All values returned in the dictionary will be made available
           as attributes of the ``request`` object.
           """

.. warning:: In :mod:`repoze.bfg.` 1.0 and previous versions, the
     traverser ``__call__`` method accepted a WSGI *environment*
     dictionary rather than a :term:`request` object.  The request
     object passed to the traverser implements a dictionary-like API
     which mutates and queries the environment, as a backwards
     compatibility shim, in order to allow older code to work.
     However, for maximum forward compatibility, traverser code
     targeting :mod:`repoze.bfg` 1.1 and higher should expect a
     request object directly.

More than one traversal algorithm can be active at the same time.  For
instance, if your :term:`root factory` returns more than one type of
object conditionally, you could claim that an alternate traverser
adapter is ``for`` only one particular class or interface.  When the
root factory returned an object that implemented that class or
interface, a custom traverser would be used.  Otherwise, the default
traverser would be used.  For example:

.. code-block:: xml
   :linenos:

    <adapter
      factory="myapp.traversal.Traverser"
      provides="repoze.bfg.interfaces.ITraverser"
      for="myapp.models.MyRoot"
      />

If the above stanza was added to a ``configure.zcml`` file,
:mod:`repoze.bfg` would use the ``myapp.traversal.Traverser`` only
when the application :term:`root factory` returned an instance of the
``myapp.models.MyRoot`` object.  Otherwise it would use the default
:mod:`repoze.bfg` traverser to do traversal.

Example implementations of alternate traversers can be found "in the
wild" within `repoze.bfg.traversalwrapper
<http://pypi.python.org/pypi/repoze.bfg.traversalwrapper>`_ and
`repoze.bfg.metatg <http://svn.repoze.org/repoze.bfg.metatg/trunk/>`_.

.. index::
   single: url generator

Changing How :mod:`repoze.bfg.url.model_url` Generates a URL
------------------------------------------------------------

When you add a traverser as described in
:ref:`changing_the_traverser`, it's often convenient to continue to
use the :func:`repoze.bfg.url.model_url` API.  However, since the way
traversal is done will have been modified, the URLs it generates by
default may be incorrect.

If you've added a traverser, you can change how
:func:`repoze.bfg.url.model_url` generates a URL for a specific type
of :term:`context` by adding an adapter stanza for
:class:`repoze.bfg.interfaces.IContextURL` to your application's
``configure.zcml``:

.. code-block:: xml
   :linenos:

    <adapter
      factory="myapp.traversal.URLGenerator"
      provides="repoze.bfg.interfaces.IContextURL"
      for="myapp.models.MyRoot *"
      />

In the above example, the ``myapp.traversal.URLGenerator`` class will
be used to provide services to :func:`repoze.bfg.url.model_url` any
time the :term:`context` passed to ``model_url`` is of class
``myapp.models.MyRoot``.  The asterisk following represents the type
of interface that must be possessed by the :term:`request` (in this
case, any interface, represented by asterisk).

The API that must be implemented by a class that provides
:class:`repoze.bfg.interfaces.IContextURL` is as follows:

.. code-block:: python
  :linenos:

  from zope.interface import Interface

  class IContextURL(Interface):
      """ An adapter which deals with URLs related to a context.
      """
      def __init__(self, context, request):
          """ Accept the context and request """

      def virtual_root(self):
          """ Return the virtual root object related to a request and the
          current context"""

      def __call__(self):
          """ Return a URL that points to the context """

The default context URL generator is available for perusal as the
class :class:`repoze.bfg.traversal.TraversalContextURL` in the
`traversal module
<http://svn.repoze.org/repoze.bfg/trunk/repoze/bfg/traversal.py>`_ of
the :term:`Repoze` Subversion repository.
