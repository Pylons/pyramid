.. _hello_traversal_chapter:

Hello Traversal World
======================


.. index::
   single: traversal quick example

Traversal is an alternative to URL dispatch which allows Pyramid
applications to map URLs to code.

If code speaks louder than words, maybe this will help. Here is a
single-file Pyramid application that uses traversal:

.. literalinclude:: hellotraversal.py
   :linenos:

You may notice that this application is intentionally very similar to
the "hello world" app from :doc:`firstapp`.

On lines 5-6, we create a trivial :term:`resource` class that's just a
dictionary subclass.

On lines 8-9, we hard-code a :term:`resource tree` in our :term:`root
factory` function.

On lines 11-13 we define a single :term:`view callable` that can
display a single instance of our Resource class, passed as the
``context`` argument.

The rest of the file sets up and serves our pyramid WSGI app.  Line 18
is where our view gets configured for use whenever the traversal ends
with an instance of our Resource class.

Interestingly, there are no URLs explicitly configured in this
application. Instead, the URL space is defined entirely by the keys in
the resource tree.

Example requests
----------------

If this example is running on http://localhost:8080, and the user
browses to http://localhost:8080/a/b, Pyramid will call
``get_root(request)`` to get the root resource, then traverse the tree
from there by key; starting from the root, it will find the child with
key ``"a"``, then its child with key ``"b"``; then use that as the
``context`` argument for calling ``hello_world_of_resources``.

Or, if the user browses to http://localhost:8080/ , Pyramid will
stop at the root - the outermost Resource instance, in this case - and
use that as the ``context`` argument to the same view.

Or, if the user browses to a key that doesn't exist in this resource
tree, like http://localhost:8080/xyz or
http://localhost:8080/a/b/c/d, the traversal will end by raising a
KeyError, and Pyramid will turn that into a 404 HTTP response.

A more complicated application could have many types of resources,
with different view callables defined for each type, and even multiple
views for each type.

See Also
---------

Full technical details may be found in :doc:`traversal`.

For more about *why* you might use traversal, see :doc:`muchadoabouttraversal`.

