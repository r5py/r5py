# *R⁵py* – rapid realistic routing with Python


:::{thumbnail} _static/images/HowWellDoesPublicTransportWorkForSlowWalkers_1200x720px.png
:alt: A map showing the Helsinki metropolitan area, and how walking slowly changes the efficieny of the public transport network.
:title: A travel time matrix made with <em>r5py</em>
:show_caption: 1
:class: align-default
:::


**R5py** is a Python library for rapid realistic routing on multimodal
transport networks (walk, bike, public transport and car).  It provides a
simple and friendly interface to R{sup}`5`, the Rapid Realistic Routing on
Real-world and Reimagined networks, the [routing
engine](https://github.com/conveyal/r5) developed by Conveyal. `r5py` is
inspired by [r5r, a wrapper for R](https://ipeagit.github.io/r5r/), and it is
designed to interact with [GeoPandas](https://geopandas.org/) GeoDataFrames.

`R5py` offers a simple way to run R5 locally with Python, allowing the users to
calculate travel time matrices and accessibility by different travel modes.  To
get started, take a look at the [user
manual](user-guide/user-manual/quickstart) that includes a detailed
demonstration of `r5py` in action.  Over time, `r5py` will be expanded to
incorporate other functionalities from R5.

:::{toctree}
:caption: User guide
:maxdepth: 1
:hidden:

User Manual <user-guide/user-manual/quickstart>
user-guide/installation/installation
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
