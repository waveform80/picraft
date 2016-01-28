.. _install:

============
Installation
============


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

