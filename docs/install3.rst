.. _install3:

========================
Python 3.2+ Installation
========================

There are several ways to install picraft under Python 3.2 (or above), each
with their own advantages and disadvantages. Have a read of the sections below
and select an installation method which conforms to your needs.


.. _raspbian_install3:

Raspbian installation
=====================

If you are using the `Raspbian`_ distro, it is best to install picraft using
the system's package manager: apt. This will ensure that picraft is easy to
keep up to date, and easy to remove should you wish to do so. It will also make
picraft available for all users on the system. To install picraft using apt
simply::

    $ sudo apt-get update
    $ sudo apt-get install python3-picraft

To upgrade your installation when new releases are made you can simply use
apt's normal upgrade procedure::

    $ sudo apt-get update
    $ sudo apt-get upgrade

If you ever need to remove your installation::

    $ sudo apt-get remove python3-picraft

.. _Raspbian: http://www.raspbian.org/
.. _NOOBS: http://www.raspberrypi.org/downloads/


.. _user_install3:

User installation
=================

This is the simplest (non-apt) form of installation, but bear in mind that it
will only work for the user you install under. For example, if you install as
the ``pi`` user, you will only be able to use picraft as the ``pi`` user. If
you run python as root (e.g. with ``sudo python``) it will not find the module.
See :ref:`system_install2` below if you require a root installation.

To install as your current user::

    $ sudo apt-get install python3-pip
    $ pip-3.2 install --user picraft

Note that ``pip-3.2`` is **not** run with ``sudo``; this is deliberate. To
upgrade your installation when new releases are made::

    $ pip-3.2 install --user -U picraft

If you ever need to remove your installation::

    $ pip-3.2 uninstall picraft


.. _system_install3:

System installation
===================

A system installation will make picraft accessible to all users (in contrast
to the user installation). It is as simple to perform as the user installation
and equally easy to keep updated. To perform the installation::

    $ sudo apt-get install python3-pip
    $ sudo pip-3.2 install picraft

To upgrade your installation when new releases are made::

    $ sudo pip-3.2 install -U picraft

If you ever need to remove your installation::

    $ sudo pip-3.2 uninstall picraft


.. _virtualenv_install3:

Virtualenv installation
=======================

If you wish to install picraft within a virtualenv (useful if you're working
on several Python projects with potentially conflicting dependencies, or you
just like keeping things separate and easily removable)::

    $ sudo apt-get install python3-pip python-virtualenv
    $ virtualenv -p python3 sandbox
    $ source sandbox/bin/activate
    (sandbox) $ pip-3.2 install picraft

Bear in mind that each time you want to use picraft you will need to activate
the virtualenv before running Python::

    $ source sandbox/bin/activate
    (sandbox) $ python
    >>> import picraft

To upgrade your installation, make sure the virtualenv is activated and just
use pip::

    $ source sandbox/bin/activate
    (sandbox) $ pip-3.2 install -U picraft

To remove your installation simply blow away the virtualenv::

    $ rm -fr ~/sandbox/


.. _dev_install3:

Development installation
========================

If you wish to develop picraft itself, it is easiest to obtain the source by
cloning the GitHub repository and then use the "develop" target of the Makefile
which will install the package as a link to the cloned repository allowing
in-place development (it also builds a tags file for use with vim/emacs with
Exuberant's ctags utility).  The following example demonstrates this method
within a virtual Python environment::

    $ sudo apt-get install build-essential git git-core exuberant-ctags \
        python-virtualenv
    $ virtualenv -p python3 sandbox
    $ source sandbox/bin/activate
    (sandbox) $ git clone https://github.com/waveform80/picraft.git
    (sandbox) $ cd picraft
    (sandbox) $ make develop

To pull the latest changes from git into your clone and update your
installation::

    $ source sandbox/bin/activate
    (sandbox) $ cd picraft
    (sandbox) $ git pull
    (sandbox) $ make develop

To remove your installation blow away the sandbox and the clone::

    $ rm -fr ~/sandbox/ ~/picraft/

Even if you don't feel up to hacking on the code, I'd love to hear suggestions
from people of what you'd like the API to look like (even if the code itself
isn't particularly pythonic, the interface should be)!


.. _test_suite3:

Test suite
==========

If you wish to run the picraft test suite, follow the instructions in
:ref:`dev_install3` above and then execute the following command::

    (sandbox) $ make test

