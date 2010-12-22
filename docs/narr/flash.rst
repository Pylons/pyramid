.. _flash_chapter:

Flash Messages
==============

"Flash messages" are simply a queue of message strings stored in the
:term:`session`.  To use flash messaging, you must enable a :term:`session
factory` as described in :ref:`using_the_default_session_factory` or
:ref:`using_alternate_session_factories`.

Flash messaging has two main uses: to display a status message only once to
the user after performing an internal redirect, and to allow generic code to
log messages for single-time display without having direct access to an HTML
template. The user interface consists of two methods of the :term:`session`
object.

Using the ``session.flash`` Method
----------------------------------

To add a message to a flash queue, use a session object's ``flash`` method:

.. code-block:: python
   :linenos:

   request.session.flash('mymessage')

The ``.flash`` method appends a message to the queue, creating the queue if
necessary. The message is not modified in any way.

The ``category`` argument names a category or level. The library defines
several default category names: ``debug``, ``info``, ``success``, ``warning``
and ``error``.  The default category level is ``info``.

The ``queue_name`` argument allows you to define multiple message
queues. This can be used to display different kinds of messages in different
places on a page.  You cam pass any name for your queue, but it must be a
string. The default value is the empty string, which chooses the default
queue. Each queue is independent, and can be popped by ``unflash``
separately.

Constant names for flash message category names are importable from the
:mod:`pyramid.flash` module as ``DEBUG``, ``INFO``, ``SUCCESS``, ``WARNING``
and ``ERROR``, which respectively name ``debug``, ``info``, ``success``,
``warning`` and ``error`` strings.  For example you can do this:

.. code-block:: python

   from pyramid import flash
   request.session.flash(msg, flash.DEBUG)

Or you can use the literal name ``debug``:

.. code-block:: python

   request.session.flash(msg, 'debug')

Both examples do the same thing.  The meanings of flash category names are
detailed in :mod:`pyramid.flash`.

To pop a particular queue of messages from the flash object, use the session
object's ``unflash`` method.

.. code-block:: python
   :linenos:

   >>> request.session.flash('info message', 'info')
   >>> messages = request.session.unflash()
   >>> messages['info']
   ['info message']

Using the ``session.unflash`` Method
------------------------------------

Once one or more messages has been added to a flash queue by the
``session.flash`` API, the ``session.unflash`` API can be used to pop that
queue and return it for use.

For example some code that runs in a view callable might call the
``session.flash`` API:

.. code-block:: python
   :linenos:

   request.session.flash('mymessage')
   
A corresponding ``session.unflash`` might be called on a subsequent request:

.. code-block:: python
   :linenos:

   messages = request.session.unflash()

Calling ``session.unflash`` again like above without a corresponding call to
``session.flash`` will return an empty ``messages`` object, because the queue
has already been popped.

The ``messages`` object returned from ``unflash`` is a dictionary-like
object.  Its keys are category names, and its values are sequences of
strings.  For ease of use, the dict-like object returned by ``unflash`` isn't
a "plain" dict: it's an object which has several helper methods, each named
after a particular flash category level.  These methods return all messages
related to the category name:

.. code-block:: python
   :linenos:

   >>> request.session.flash('debug message', 'debug')
   >>> request.session.flash('info message', 'info')
   >>> messages = request.session.unflash()
   >>> info_messages = messages.debug()
   ['debug message']
   >>> info_messages = messages.info()
   ['info message']

The full API of the ``messages`` object returned by ``unflash`` is documented
in :class:`pyramid.interfaces.IFlashMessages`.

.. The ``ignore_duplicate`` flag tells whether to suppress duplicate
.. messages.  If true, and another message with identical text exists in the
.. queue, don't add the new message. But if the existing message has a
.. different category than the new message, change its category to match the
.. new message.

