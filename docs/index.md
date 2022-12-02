# R5py

**R5py** is a Python library for rapid realistic routing on multimodal transport networks (walk, bike, public transport and car).
It provides a simple and friendly interface to R{sup}`5`, the Rapid Realistic Routing on Real-world and Reimagined networks,
the [routing engine](https://github.com/conveyal/r5) developed by Conveyal. `r5py` is inspired by [r5r, a wrapper for R](https://ipeagit.github.io/r5r/),
and it is designed to interact with [GeoPandas](https://geopandas.org/) GeoDataFrames.

`R5py` offers a simple way to run R5 locally with Python, allowing the users to calculate travel time matrices and accessibility by different travel modes.
To get started, see a detailed demonstration of the `r5py` in action from the {doc}`usage/basic-usage` section.
Over time, `r5py` will be expanded to incorporate other functionalities from R5.

:::{toctree}
:maxdepth: 1

installation/installation
:::

:::{toctree}
:maxdepth: 1

configuration/configuration
:::

:::{toctree}
:maxdepth: 2

usage/basic-usage
:::

:::{toctree}
:maxdepth: 1

community/CONTRIBUTING
Code of conduct <community/CODE_OF_CONDUCT>
community/citation
:::

:::{toctree}
:maxdepth: 1

API Reference <reference/reference>
:::
