.. _installataion:


Installation
============

Dependencies
------------

In order to interface with R5, r5py requires a Java Runtime Environment (jre), plus a matching Java Development Kit (jdk). We used Java 11, but other versions might work just as well. `OpenJDK <https://openjdk.java.net/>`_ works fine.

If not available in the default class path (``/usr/share/java/r5/r5-all.jar``), r5py attempts to download its own copy of R5 (the class path can be configured in the `configuration file <#configuration>`_). If you are on Arch Linux, the AUR package `java-r5 <https://aur.archlinux.org/packages/java-r5>`_ installs into the correct file path.



Installation
------------

In the future (TODO!), r5py will be available from PyPi, and can be installed using ``pip``::

    pip install r5py

For the time being, please manually download the latest release tar or wheel from the package registry associated with r5py’s git repository: https://github.com/r5py/r5py/releases and install it using ``pip``::

    pip install r5py-0.0.1.tar.gz

Alternatively, r5py can be installed from source by cloning its repository and running pip in the checked-out directory::

    git clone https://github.com/r5py/r5py/
    cd r5py
    pip install .



Configuration
-------------

R5py can be configured using a configuration file ``r5py.yml``, for which the package searches in ``/etc``, ``%APPDATA%\``, ``${XDG_CONFIG_HOME}/``, and ``~/.config/``. Currently the following configuration options and default values are available::

    r5-classpath: /usr/share/java/r5/r5-all.jar
    max-memory: 80%
    verbose: False
