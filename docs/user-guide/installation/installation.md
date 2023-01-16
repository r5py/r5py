# Installation

:::{toctree}
:maxdepth: 1
:caption: Installation
:hidden:

troubleshooting
:::

*R5py* is available from [PyPi](https://pypi.org/project/r5py/) and
[conda-forge](https://anaconda.org/conda-forge/r5py), and can be installed
using [`pip`](https://pip.pypa.io/en/stable/getting-started/),
[`mamba`](https://github.com/conda-forge/miniforge#mambaforge), or
[`conda`](https://docs.conda.io/projects/conda/). See below for detailed
instructions for each installation method.

For **Windows** users, we generally recommend to use [`mamba` or `conda` to
create a new dedicated *environment*](#install-using-mambaconda) and install
*r5py* and its dependencies into it.

On **Linux** and **MacOS**, depending on your use case, either approach might be
appropriate:
- If *r5py* is [installed via `pip`](#install-using-pip),
  system-wide resources can be re-used (and managed by the system package
  manager), lowering both disk and memory footprint - but you need manually ensure
  that a [Java environment](#dependencies) is installed.
- If [installed via `conda`/`mamba`](#install-using-mambaconda), *r5py* is as
  much a turnkey solution on Linux and MacOS as it is on Windows, at the expense
  of a slight performance decrease. However, as additional package managers,
  `conda` and `mamba` are not available from the default package sources on all
  distributions; Debian and Debian-based systems, such as Ubuntu or Mint, for
  instance, do not provide `conda` packages.

:::{admonition} Python package/environment managers
:class: hint

If you are new to the (sometimes confusing) world of Python package managers,
read more about them in [chapter 1 of *Python for Geographic Data
Analysis*](https://pythongis.org/part1/chapter-01/nb/05-installation.html).
:::


## Install using `mamba`/`conda`

:::{admonition} Mamba
:class: note

[Mambaforge](https://github.com/conda-forge/miniforge#mambaforge) (available
for Windows/Linux/Mac) is a drop-in replacement for the popular package manager
[Miniconda](https://docs.conda.io/en/latest/miniconda.html), sporting
tremendously improved installation times.

To use *Mambaforge*, simply replace `conda` with `mamba` in the code examples
below.
:::

To install *r5py* and all its dependencies into a newly created [*conda
environment*](https://docs.conda.io/projects/conda/en/latest/user-guide/concepts/environments.html),
use `conda create` (or `mamba create`):

```{code} sh
conda create \
    --name r5py \
    --channel conda-forge \
    r5py
```

This will create a new environment `r5py`, and installs *r5py* and its
dependencies, using the *conda-forge* repository. To start work inside the newly
created environment, run

```{code} sh
conda activate r5py
```

If you want to use *r5py* in a notebook environment, install
[JupyterLab](https://jupyterlab.readthedocs.io/):

```{code} sh
conda install --channel conda-forge jupyterlab
```


### Install *r5py* into an existing environment

If you already have an existing conda environment, and want to install *r5py*
in addition to the packages installed there, *activate* the environment, and
run:

```{code} sh
conda install --channel conda-forge r5py
conda activate r5py-env
```

After this, you can start using the `r5py` library in the environment, e.g., using
[JupyterLab](https://jupyterlab.readthedocs.io/en/stable/) (installed as part of the environment).


## Install using `pip`

To install *r5py* from *PyPi*, the official *Python package index*, use `pip`:

```{code} sh
pip install r5py
```

Note that this does not automatically install a [Java
environment](#java-development-kit). You will have to ensure that a *Java
Development Kit* is available, see instructions below.


## Dependencies

*R5py* relies on one notable external dependency, a Java environment.

### Java Development Kit

To interface with R5, *r5py* requires a *Java Development Kit* (jdk).

If you installed *r5py* using `conda` or `mamba`, an appropriate version of
OpenJDK has been installed as a dependency, and you are ready to go. If you used
`pip`, or installed *r5py* manually, please install a JDK, for instance, [OpenJDK](https://openjdk.org/).

Consider installing it from your system’s package manager, or the official
[Microsoft build](https://learn.microsoft.com/en-gb/java/openjdk/download) in
case you work on Windows.
