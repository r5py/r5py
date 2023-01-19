# Configuration

## Configuration via config files

*R5py* can be configured using a configuration file `r5py.yml`, for which the
package searches in the following paths:

- On Unix-like operating systems (such as most Linux and BSD distributions,
  as well as MacOS): 
  - `${XDG_CONFIG_HOME}/r5py.yml` or `~/.config/r5py.yml` for per-user
    configuration (if both files exist, only the former is read)
  - `/etc/r5py.yml` for system-wide configuration (user config overrides system
    config)
- On Windows operating systems:
  - `%APPDATA%\\r5py.yml`. The precise path of the `%APPDATA%` directory depends
    on your user name and locale (enter `%APPDATA%` in a Windows Explorer’s search
    bar to navigate to it).


## Configuration from the command line

When running *r5py* from the command line, you can supply command line
arguments.  To show available options, consult the [table
below](configuration-options), or run:

```bash
python -m r5py --help
```


## Using command line options in a script or notebook

If you use *r5py* in a script, or run it from a notebook and don’t want to
rely on a configuration file, you can set command line arguments ***before***
*importing r5py*:

```python
import sys
sys.argv.append(["--max-memory", "99%"])
import r5py
```

To find available options, consult the *command line argument* column of the
[table below](configuration-options).


## Configuration options

### Overview

% IDEA: would it be good to use executablebook’s ‘option lists’?
% https://raw.githubusercontent.com/executablebooks/sphinx-book-theme/master/docs/reference/kitchen-sink/lists.rst
% https://sphinx-book-theme.readthedocs.io/en/stable/reference/kitchen-sink/lists-and-tables.html#option-lists

:::{list-table}
:header-rows: 1
:name: configuration-options

* - configuration file option
  - command line argument
  - explanation
  - default value

* - `max-memory: [value]`
  - `--max-memory [value]`, <br>
    `-m [value]`
  - Set the limit for the Java Virtual Machine’s heap size (`-Xmx`).
    This option accepts either absolute values (integer or decimal),
    optionally with a suffix to indicate Mibibytes, Gibibytes, or
    Tebibytes: `M`, `G`, `T`), or relative, expressed in a percentage
    of total memory, with a `%` suffix.
  - `80%`

* - `r5-classpath: [classpath]`
  - `--r5-classpath [classpath]`, <br>
    `-r [classpath]`
  - Point to R5’s JAR (or build directory) in case you want to use a
    custom R5 installation.
  - `/usr/share/java/r5/r5-all.jar`

* - `verbose: [boolean]`
  - `--verbose`, `-v`
  - Show more detailed output
  - `False` in configuration file, not specified on commandline
:::


### Setting the maximum Java heap size (memory use)

A *Java Virtual Machine* (JVM) typically restricts the memory usage of programs
it runs.  More specifically, the *heap size* can be limited (see [this
stackoverflow
discussion](https://stackoverflow.com/questions/14763079/what-are-the-xms-and-xmx-parameters-when-starting-jvm)
for details). 

The tasks carried out by *R5* under the hood of *r5py* are fairly
memory-intensive, which is why, by default, r5py allows the JVM to grant up to
80% of total memory to R5 (but always leaving at least 2 GiB to the system and
other processes).

You might want to lower this limit if you are running other tasks in parallel,
or raise it, if you have a dedicated computer with large memory and small
operating system requirements.

As outlined above, you can either create a configuration file, and set
`max-memory` there, specify the `--max-memory` or `-m` command line arguments,
or add the same arguments to `sys.argv`.

For instance, to set the maximum heap size to a fixed 12 GiB, you can create a
configuration file in the [location suitable for your operating
system](#configuration-via-config-files), and add the following line:

```yaml
max-memory: 12G
```


### Using a custom installation of R5

For some use cases, it can be useful to use a local copy of *R5*, rather than
the one downloaded by *r5py*, for instance, in order to apply custom patches
to extend or modify R5’s functionality, or to force the use of a certain
version for longitudinal comparability. 

This can be achieved by either installing R5 into the default class path
`/usr/share/java/r5/r5-all.jar`, or by using a configuration option or command
line argument to change the class path. 

For example, to set a custom classpath inside a Python notebook, you can set
`sys.argv` before importing `r5py`:

```python
import sys
sys.argv.append(["--r5-classpath", "/opt/r5/"])
import r5py
```
