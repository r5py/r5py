# Configuration

## Configuration options

*R5py* can be configured in three different ways: in a [configuration
file](#configuration-via-config-files), or using [command line
arguments](#configuration-via-config-files) which can also be used [within
script files or notebooks](#configuration-from-the-command-line). 

The arguments and options of all three approaches share the the same names. Please 
note that in the configuration files the leading dash(es) are omitted (see
[below](#configuration-via-config-files)).


### Overview

% option lists are not yet implemented in myst, 
% cf. https://github.com/executablebooks/MyST-Parser/issues/286

```{eval-rst}
--max-memory=value, -m value
              [Set the limit for the *Java Virtual Machine*’s heap
              size](advanced-usage.html#limit-the-maximum-java-heap-size-memory-use)
              (`-Xmx`).  This option accepts either absolute values (integer or
              decimal), optionally with a suffix to indicate Mibibytes,
              Gibibytes, or Tebibytes: `M`, `G`, `T`), or relative, expressed in
              a percentage of total memory, with a `%` suffix. Default: `80%`

--r5-classpath=classpath, -r classpath
              Point to R⁵’s JAR (or build directory) in case you want to use a
              [custom R⁵ installation](advanced-usage.html#use-a-custom-installation-of-r5).
              Default: `""` (download latest compatible version of R5)

--verbose, -v
              Show more detailed output.
```


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
  - `%APPDATA%\r5py.yml`. The precise path of the `%APPDATA%` directory depends
    on your user name and locale (enter `%APPDATA%` in a Windows Explorer’s search
    bar to navigate to it).

Consult the [list above](#configuration-options), omit any leading dashes from
the option names, and specify in [YAML](https://yaml.org/) format (for
instance, `--max-memory=12G` as `max-memory: 12G`).


:::{admonition} Template configuration file
:class: info

When *r5py* is run for the first time, it creates template configuration files
in all valid locations to which it has write-access.
:::


## Configuration from the command line

When running *r5py* from the command line, you can supply command line
arguments.  To show available options, consult the [list
above](#configuration-options), or run:

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

import r5py  # noqa: F401
```

To find available options, consult the [table above](#configuration-options).

