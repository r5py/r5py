# r5py: Rapid Realistic Routing with R5 in Python

[![Documentation Status](https://readthedocs.org/projects/r5py/badge/?version=stable)](https://r5py.readthedocs.io/en/stable/?badge=stable)
[![Trunk build status](https://github.com/r5py/r5py/actions/workflows/build-merged-pull-requests.yml/badge.svg)](https://github.com/r5py/r5py/actions/workflows/build-merged-pull-requests.yml)
[![Python version](https://img.shields.io/pypi/pyversions/r5py)](https://pypi.org/project/r5py)
[![PyPi package version](https://img.shields.io/pypi/v/r5py)](https://pypi.org/project/r5py)
[![Coverage](https://codecov.io/gh/r5py/r5py/branch/main/graph/badge.svg?token=WG8RBMZBK6)](https://codecov.io/gh/r5py/r5py)

**R5py** is a Python wrapper for the [R5 routing analysis
engine](https://github.com/conveyal/r5). It’s inspired by [r5r, a wrapper for
R](https://ipeagit.github.io/r5r/), and is designed to interact with
[GeoPandas](https://geopandas.org/) data frames.

Similar to [r5r](https://ipeagit.github.io/r5r/), **r5py** represents a simple
way to run [R5](https://github.com/conveyal/r5) locally. It allows users to
generate detailed routing analyses or calculate travel time matrices using
parallel computing, and integrates seamlessly with Python/Geopandas workflows.


## Installation

**R5py** is available from conda-forge and PyPi. You can use `mamba`, `pip` or `conda` to install it.
To quickstart your use of **r5py**, we also provide an [`environment.yml` file ](ci/r5py_distro.yaml),
using which you can [quickly set up a development environment](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#creating-an-environment-from-an-environment-yml-file) and are ready to go.

For more details and alternative installation options, read the dedicated [installation section](https://r5py.readthedocs.io/en/latest/installation.html) of the r5py documentation.

## Usage

You can find detailed installation instructions, example code, documentation and
API reference at [r5py.readthedocs.io](https://r5py.readthedocs.io).


## Acknowledgements

The [R<sup>5</sup> routing engine](https://github.com/conveyal/r5) is developed
at [Conveyal](https://www.conveyal.com/) with contributions from several people.

R5py draws a lot of inspiration from [r5r](https://github.com/ipeaGIT/r5r/), an
interface to R5 from the R language that is developed at the Institute for Applied
Economic Research (Ipea), Brazil.

<!--//

TODO:
Citation (at least a Zenodo link, first; then also a software paper)

//-->

## License

This work is dual-licensed under GNU General Public License v3.0 or later and MIT License. You can choose between one of them if you use this work.

`SPDX-License-Identifier: GPL-3.0-or-later OR MIT`
