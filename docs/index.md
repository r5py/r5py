# r5py: rapic realistic routing with Python

**R5py** is a Python library for rapid realistic routing on multimodal
transport networks (walk, bike, public transport and car).  It provides a
simple and friendly interface to R{sup}`5`, the Rapid Realistic Routing on
Real-world and Reimagined networks, the [routing
engine](https://github.com/conveyal/r5) developed by Conveyal. `r5py` is
inspired by [r5r, a wrapper for R](https://ipeagit.github.io/r5r/), and it is
designed to interact with [GeoPandas](https://geopandas.org/) GeoDataFrames.

`R5py` offers a simple way to run R5 locally with Python, allowing the users to
calculate travel time matrices and accessibility by different travel modes.  To
get started, take a look at the [user manual](user-guide/user-manual) that
includes a detailed demonstration of `r5py` in action.  Over time, `r5py` will
be expanded to incorporate other functionalities from R5.

:::{toctree}
:caption: User guide
:maxdepth: 2
:hidden:

user-guide/installation
user-guide/configuration
user-guide/user-manual
user-guide/citation
:::

:::{toctree}
:caption: Contributing
:maxdepth: 1
:hidden:

contributing/CONTRIBUTING
Code of conduct <contributing/CODE_OF_CONDUCT>
:::

:::{toctree}
:caption: API reference
:maxdepth: 1
:hidden:

Module contents <reference/reference>
:::
