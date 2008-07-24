Installation
=====================

You can get the final form of the demo application, along with all the
steps along the way, via the miracles of virtualenv, easy_install and Paster
templates::

  $ virtualenv --no-site-packages myapp
  $ cd myapp
  $ source bin/activate
  $ easy_install repoze.lxmlgraph
  $ paster create -t lxmlgraph_project

Answer the questions, then run the demo:

  cd <<projectname>>
  python run.py

At that point a URL such as ``http://localhost:5432/folder2/query1``
should work.

  