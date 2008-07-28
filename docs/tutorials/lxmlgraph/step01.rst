=======================
Step 1: Getting Started
=======================

To get started, using the ``paster`` command from a :term:`virtualenv`
you've created that has :mod:`repoze.bfg` installed, run ``paster
create -t bfg`` as described in :ref:`project_narr` to create your
``lxmlgraph`` project::

 $ paster create -t bfg Selected and implied templates: repoze.bfg#bfg
  repoze.bfg starter project

  Enter project name: lxmlgraph
  ...
 $
  
You now have a project named ``lxmlgraph`` in your current directory.
We'll add to this project in subsequent steps.

To get your project ready for development and execution, use the
``setup.py develop`` command within the same virtualenv as bfg is
installed as documented in :ref:`project_narr` .  You'll need to do
this in order to run the ``lxmlgraph`` application in subsequent
steps.
