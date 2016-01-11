.. _install:

============
Installation
============

There are several ways to install picraft under Python, each with their own
advantages and disadvantages. Have a read of the sections below and select an
installation method which conforms to your needs.


.. _raspbian_install:

Raspbian installation
=====================

If you are using the `Raspbian`_ distro, it is best to install picraft using
the system's package manager: apt. This will ensure that picraft is easy to
keep up to date, and easy to remove should you wish to do so. It will also make
picraft available for all users on the system. To install picraft using apt
simply::

    $ sudo apt-get update
    $ sudo apt-get install python-picraft python3-picraft

To upgrade your installation when new releases are made you can simply use
apt's normal upgrade procedure::

    $ sudo apt-get update
    $ sudo apt-get upgrade

If you ever need to remove your installation::

    $ sudo apt-get remove python-picraft python3-picraft

.. _Raspbian: http://www.raspbian.org/


.. _ubuntu_install:

Ubuntu installation
===================

If you are using `Ubuntu`_, it is best to install picraft from the author's
PPA. This will ensure that picraft is easy to keep up to date, and easy to
remove should you wish to do so. It will also make picraft available for all
users on the system. To install picraft from the PPA::

    $ sudo add-apt-repository ppa:waveform/ppa
    $ sudo apt-get update
    $ sudo apt-get install python-picraft python3-picraft

To upgrade your installation when new releases are made you can simply use
apt's normal upgrade procedure::

    $ sudo apt-get update
    $ sudo apt-get upgrade

If you ever need to remove your installation::

    $ sudo apt-get remove python-picraft python3-picraft

.. _Ubuntu: http://ubuntu.com
.. _PPA: https://launchpad.net/~waveform/+archive/ubuntu/ppa


.. _windows_install:

Windows installation
====================

The following assumes you're using a recent version of Python (like 3.5) which
comes with pip, and that you checked the option to "adjust PATH" when
installing Python.

Start a command window by pressing :kbd:`Win-R` and entering "cmd". At the
command prompt enter::

    C:\Users\Dave> pip install picraft

To upgrade your installation when new releases are made::

    C:\Users\Dave> pip install -U picraft

If you ever need to remove your installation::

    C:\Users\Dave> pip uninstall picraft


.. _dev_install:

Development installation
========================

If you wish to develop picraft itself, it is easiest to obtain the source by
cloning the GitHub repository and then use the "develop" target of the Makefile
which will install the package as a link to the cloned repository allowing
in-place development (it also builds a tags file for use with vim/emacs with
Exuberant's ctags utility).  The following example (which assumes a UNIX-like
environment like Ubuntu or Raspbian) demonstrates this method within a virtual
Python environment::

    $ sudo apt-get install build-essential git git-core exuberant-ctags \
        python-virtualenv
    $ virtualenv -p /usr/bin/python3 sandbox
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


.. _test_suite:

Test suite
==========

If you wish to run the picraft test suite, follow the instructions in
:ref:`dev_install` above and then execute the following command::

    (sandbox) $ make test

