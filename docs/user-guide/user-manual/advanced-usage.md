# Advanced Usage

## Setting the maximum Java heap size (memory use)

A *Java Virtual Machine* (JVM) typically restricts the memory usage of programs
it runs.  More specifically, the *heap size* can be limited (see [this
stackoverflow
discussion](https://stackoverflow.com/questions/14763079/what-are-the-xms-and-xmx-parameters-when-starting-jvm)
for a detailed explanation). 

The tasks carried out by *R⁵* under the hood of *r5py* are fairly
memory-intensive, which is why, by default, *r5py* allows the JVM to grant up to
80% of total memory to R⁵ (but ensures to always leave at least 2 GiB to the
system and other processes).

You want to lower this limit if you are running other tasks in parallel, or
raise it, if you have a dedicated computer with large memory and small
operating system requirements.

As outlined above, you can either create a configuration file, and set
`max-memory` there, specify the `--max-memory` or `-m` command line arguments,
or add the same arguments to `sys.argv`.

For instance, to set the maximum heap size to a fixed 12 GiB, you can create a
configuration file in the [location suitable for your operating
system](configuration.md#configuration-via-config-files), and add the following line:

```{code-block} yaml
:name: conf-yml-memory
:caption: r5py.yml

max-memory: 12G
```


## Using a custom installation of R⁵

For some use cases, it can be useful to use a local copy of R⁵, rather than
the one downloaded by *r5py*, for instance, in order to apply custom patches
to extend or modify R⁵’s functionality, or to force the use of a certain
version for longitudinal comparability. 

This can be achieved by either installing R⁵ into the default class path
`/usr/share/java/r5/r5-all.jar`, or by using a configuration option or command
line argument to change the class path. 

For example, to set a custom classpath inside a Python notebook, you can set
`sys.argv` before importing `r5py`:

```python
import sys
sys.argv.append(["--r5-classpath", "/opt/r5/"])
import r5py
```
