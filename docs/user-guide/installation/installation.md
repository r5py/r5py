# Installation

%% The TOC below is hidden as we have not come up with a good list of points
%% that require special care/troubleshooting when installing on windows

%:::{toctree}
%:maxdepth: 1
%:caption: Installation
%:hidden:
%
%troubleshooting
%:::

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
Analysis*](https://pythongis.org/part1/chapter-01/nb/06-installation.html).
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

This will create a new environment `r5py`, and install *r5py* and its
dependencies using the *conda-forge* repository. To start working inside the newly
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
in addition to the packages already installed there, *activate* the environment, and
run:

```{code} sh
conda install --channel conda-forge r5py
```


## Install using `pip`

To install *r5py* from *PyPi*, the official *Python package index*, use `pip`:

```{code} sh
pip install r5py
```

Note that this does not automatically install a [Java
environment](#java-development-kit). You will have to ensure that a *Java
Development Kit* is available, see instructions below.


## Dependencies

### Java Development Kit

*R5py* relies on one notable external dependency: a Java environment.
To interface with R⁵, *r5py* requires a *Java Development Kit* (jdk), version 21
or later.

If you installed *r5py* using `conda` or `mamba`, an appropriate version of
OpenJDK has been installed as a dependency, and you are ready to go. If you used
`pip`, or installed *r5py* manually, please install a JDK, for instance
[OpenJDK](https://openjdk.org/).

Consider installing it from your system’s package manager, or the official
[Microsoft build](https://learn.microsoft.com/en-gb/java/openjdk/download) in
case you work on Windows.


## Sample data sets

For the examples in the user manual, we prepared sample data sets, covering the
city centres of Helsinki, Finland, and São Paulo, Brazil, both cities that
researchers who contributed to *r5py* are familiar with. 

These sample data sets are packaged separately. If you work through the examples
independently, be sure to install `r5py.sampledata.helsinki` and
`r5py.sampledata.sao_paulo`, using either `pip` or `conda`/`mamba`:

```
pip install r5py.sampledata.helsinki r5py.sampledata.sao_paulo
```

```
conda install --channel conda-forge r5py.sampledata.helsinki r5py.sampledata.sao_paulo
```

The two packages then provide {class}`pathlib.Path` objects that point to sample
data sets, and can be used directly in {meth}`geopandas.read_file()`,
{meth}`pandas.read_csv()`, {class}`r5py.TransportNetwork()`, and any other
method or function that expects a file path.


:::{admonition} Data is downloaded on demand 
:class: caution

Note that the `r5py.sampledata.*` packages do not contain the actual data sets.
Instead, the data sets are downloaded to a cache directory upon first use. This
means that **you need an internet connection when you first access a data set**.
On subsequent runs, the files are served from your computer’s cache.
:::
