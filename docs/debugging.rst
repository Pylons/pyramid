Debugging Pyramid
=======================

This tutorial provides a brief introduction to using the python
debugger (``pdb``) for debugging pyramid applications.

It is also assumed the reader has found pyramid starter
documentation elsewhere, such as `Pyramid Documentation`_.

Getting Started
---------------
- As broad strokes, start with a virtual environment, created at
  ``env`` in the users root directory::

    $ cd ; virtualenv-2.7 --no-site-packages env

- Install pyramid into your virtualenv using easy_install or pip::

    $ env/bin/easy_install pyramid

Create A Project
----------------
- Now create a pyramid project using one of the available scaffolds.
  (``env/bin/pcreate --list`` shows the current options.) Using the
  ``alchemy`` scaffold, create a project named ``buggy``::

    $ env/bin/pcreate --scaffold alchemy buggy

Install The Project
-------------------
- Install this project into your virtual environment (this will also
  install any missing dependencies the scaffold requires)::

    $ cd buggy ; ~/env/bin/python setup.py develop

- Confirm http://localhost:6543 is serving content::

    $ env2/bin/paster serve development.ini

Introducing PDB
---------------
- This single line of python is your new friend::

    import pdb;  pdb.set_trace()

- As valid python, that can be inserted practically anywhere in a
  python source file.  When the python interpreter hits it - execution
  will be suspended providing you with interactive control from the
  parent TTY.

PDB Commands
------------
- pdb exposes a number of standard interactive debugging
  commands, including::

    Documented commands (type help <topic>):
    ========================================
    EOF    bt         cont      enable  jump  pp       run      unt   
    a      c          continue  exit    l     q        s        until 
    alias  cl         d         h       list  quit     step     up    
    args   clear      debug     help    n     r        tbreak   w     
    b      commands   disable   ignore  next  restart  u        whatis
    break  condition  down      j       p     return   unalias  where 
    
    Miscellaneous help topics:
    ==========================
    exec  pdb
    
    Undocumented commands:
    ======================
    retval  rv

Debugging Traversal
-------------------
- Back to our demo application, traversal is confusing to many
  newcomers, lets see if we can learn anything debugging it.

- The traversal documentation describes how pyramid first acquires a
  root object, and then descends the resource tree using the
  __getitem__ for each respective resource.

Huh?
----
- Let's drop a pdb statement into our root factory object's
  __getitem__ method and have a look.  Edit ~/buggy/buggy/models.py
  and add the aforementioned ``pdb`` line in MyModel.__getitem__ ::

    def __getitem__(self, key):
        import pdb; pdb.set_trace()
        session = DBSession()
        [...]

- Restart the service, and request a page.  Note the request requires
  a path to hit our break-point::

    http://localhost:6543/   <- misses the break-point, no traversal
    http://localhost:6543/1  <- should find an object
    http://localhost:6543/2  <- does not

- For a very simple case, attempt an insert missing keys be default.
  Set item to a valid new MyModel in MyRoot.__getitem__ if a match
  isn't found in the database::

        item = session.query(MyModel).get(id)
        if item is None:
            item = MyModel(name='test %d'%id, value=str(id))  # naive insertion

- Move the break-point within the if clause to avoid the false positive hits::

        if item is None:
            import pdb; pdb.set_trace()
            item = MyModel(name='test %d'%id, value=str(id))  # naive insertion

- Run again, note multiple request to the same id continue to create
  new MyModel instances.

- Ah, of course, we forgot to add the new item to the session.
  Another line added to our __getitem__ method::

        if item is None:
            import pdb; pdb.set_trace()
            item = MyModel(name='test %d'%id, value=str(id))
            session.add(item)

- Restart and test.  Observe the stack; debug again.  Examine the item
  returning from MyModel::

    (pdb) session.query(MyModel).get(id)

- Finally, we realize the item.id needs to be set as well before adding::

        if item is None:
            item = MyModel(name='test %d'%id, value=str(id))
            item.id = id
            session.add(item)

- Many great resources can be found describing the details of using
  pdb.  Try the interactive ``help`` (hit 'h') or a search engine near
  you.

.. _Pyramid Documentation: http://docs.pylonsproject.org/docs/pyramid.html