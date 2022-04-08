.. _installataion:


Installation
============

Dependencies
------------

In order to interface with R5, r5p requires a Java Runtime Environment (jre), plus a matching Java Development Kit (jdk). We used Java 11, but other versions might work just as well. `OpenJDK <https://openjdk.java.net/>`_ works fine.

At the time of this writing, r5p does not (yet) come with its own copy of R5. Rather, it has to be available on the system. By default, r5p assumes that R5’s class path is at ``/usr/share/java/r5/r5-all.jar`` (the class path can be configured in the `configuration file <#configuration>`_). If you are on Arch Linux, the AUR package ``java-r5`` installs into the correct file path.



Installation
------------

In the future (TODO!) r5p will be available from PyPi, and can be installed using ``pip``::

    pip install r5p

For the time being, please manually download the latest release tar or wheel from the package registry associated with r5p’s git repository: https://gitlab.com/christoph.fink/r5p/-/packages and install it using ``pip``::

    pip install r5p-0.0.1.tar.gz

Alternatively, it can be installed from source by cloning its repository and running pip in the checked-out directory::

    git clone https://gitlab.com/christoph.fink/r5p/
    cd r5p
    pip install .



Configuration
-------------

R5p can be configured using a configuration file ``r5p.yml``, for which the module searches in ``/etc``, ``%APPDATA%\``, ``${XDG_CONFIG_HOME}/``, and ``~/.config/``. Currently the following configuration options and default values are available::

    r5-classpath: /usr/share/java/r5/r5-all.jar
    verbose: False
