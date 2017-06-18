Contributing
============

All projects under the Pylons Projects, including this one, follow the
guidelines established at [How to
Contribute](https://pylonsproject.org/community-how-to-contribute.html) and
[Coding Style and
Standards](http://docs.pylonsproject.org/en/latest/community/codestyle.html).

You can contribute to this project in several ways.

* [File an Issue on GitHub](https://github.com/Pylons/pyramid/issues)
* Fork this project and create a branch with your suggested change. When ready,
  submit a pull request for consideration. [GitHub
  Flow](https://guides.github.com/introduction/flow/index.html) describes the
  workflow process and why it's a good practice. When submitting a pull
  request, sign
  [CONTRIBUTORS.txt](https://github.com/Pylons/pyramid/blob/master/CONTRIBUTORS.txt)
  if you have not yet done so.
* Join the IRC channel #pyramid on irc.freenode.net.

Git Branches
------------
Git branches and their purpose and status at the time of this writing are
listed below.

* [master](https://github.com/Pylons/pyramid/) - The branch on which further
  development takes place. The default branch on GitHub.
* [1.9-branch](https://github.com/Pylons/pyramid/tree/1.9-branch) - The branch
  classified as "alpha".
* [1.8-branch](https://github.com/Pylons/pyramid/tree/1.8-branch) - The branch
  classified as "stable" or "latest".
* [1.7-branch](https://github.com/Pylons/pyramid/tree/1.7-branch) - The oldest
  actively maintained and stable branch.

Older branches are not actively maintained. In general, two stable branches and
one or two development branches are actively maintained.

Prerequisites
-------------

Follow the instructions in HACKING.txt for your version or branch located in
the [root of the Pyramid repository](https://github.com/Pylons/pyramid/) to
install Pyramid and the tools needed to run its tests and build its
documentation.

Building documentation for a Pylons Project project
---------------------------------------------------

*Note:* These instructions might not work for Windows users. Suggestions to
improve the process for Windows users are welcome by submitting an issue or a
pull request. Windows users may find it helpful to follow the guide [Installing
Pyramid on a Windows
System](http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/install.html#installing-pyramid-on-a-windows-system).

1.  Fork the repo on GitHub by clicking the [Fork] button.
2.  Clone your fork into a workspace on your local machine.

         git clone git@github.com:<username>/pyramid.git

3.  Change directories into the cloned repository

         cd pyramid

4.  Add a git remote "upstream" for the cloned fork.

         git remote add upstream git@github.com:Pylons/pyramid.git

5.  Create a virtual environment and set an environment variable as instructed in the
    [prerequisites](https://github.com/Pylons/pyramid/blob/master/HACKING.txt#L55-L58).

         # Mac and Linux
         $ export VENV=~/hack-on-pyramid/env

         # Windows
         set VENV=c:\hack-on-pyramid\env

6.  Install `tox` into your virtual environment.

         $ $VENV/bin/pip install tox

7.  Try to build the docs in your workspace.

         $ $VENV/bin/tox -e docs

     When the build finishes, you'll find HTML documentation rendered in
     `.tox/docs/html`. An `epub` version will be in `.tox/docs/epub`. And the
     result of the tests that are run on the documentation will be in
     `.tox/docs/doctest`.

8.  From this point forward, follow the typical [git
    workflow](https://help.github.com/articles/what-is-a-good-git-workflow/).
    *Always* start by pulling from the upstream to get the most current changes.

         git pull upstream master

9.  Make a branch, make changes to the docs, and rebuild them as indicated above.

10.  Once you are satisfied with your changes and the documentation builds
     successfully without errors or warnings, then git commit and push them to
     your "origin" repository on GitHub.

         git commit -m "commit message"
         git push -u origin --all # first time only, subsequent can be just 'git push'.

11.  Create a [pull request](https://help.github.com/articles/using-pull-requests/).

12.  Repeat the process starting from Step 8.
