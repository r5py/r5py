# Installation

```{note}
There are many different ways to install **r5py** on your computer. Below, we describe the most
commonly used ones.  If you don’t have any particular preferences, we recommend to try `mamba`,
which will install r5py and all dependencies (*except* a Java Development Kit) from conda-forge.

Please see the [dependencies](#dependencies) section to understand what will be installed on your computer.
```


## Install using `mamba`

[Mambaforge](https://github.com/conda-forge/miniforge#mambaforge) (available for Windows/Linux/Mac)
is a drop-in replacement for the popular package manager [Miniconda](https://docs.conda.io/en/latest/miniconda.html).
It comes with a significantly faster package manager called `mamba`. By default, MambaForge uses only the
`conda-forge` channel to fetch packages. This helps to avoid dependency conflicts and potential
issues with licensing (see [this blog post](https://florianwilhelm.info/2021/09/Handling_Anaconda_without_getting_constricted/)).

If you are new to the (sometimes confusing) world of Python package managers, you can read more about them
[here](https://python-gis-book.readthedocs.io/en/develop/part1/chapter-01/nb/05-installation.html).


### Install `mamba`

First, make sure that you have `mamba` available on your system. You can either download it from
[Mambaforge](https://github.com/conda-forge/miniforge#mambaforge), or use `conda`:

     conda install -n base -c conda-forge mamba


### Install `r5py` in your existing environment

To install r5py, run:

     mamba install -c conda-forge r5py


### Install `r5py` into a dedicated Python environment

You can also install r5py (plus a few other Python packages that are useful
when working with it, such as, e.g., [Geopandas](https://geopandas.org/)) into
a dedicated conda environment.

1. [Download the `r5py_distro.yaml` file](https://github.com/r5py/r5py/blob/main/ci/r5py_distro.yaml)
2. Run the following command to install the packages into a new environment named `r5py-env`:

        mamba env create -f r5py_distro.yaml


4. Activate the `r5py-env` environment:

        conda activate r5py-env

After this, you can start using the `r5py` library in the environment, e.g., using
[JupyterLab](https://jupyterlab.readthedocs.io/en/stable/) (installed as part of the environment).

## Install using `conda`

If you prefer to use conda as your Python package manager, follow the same instructions as above,
but replace `mamba` with `conda`:

To install r5py with `conda`, run:

     conda install -c conda-forge r5py

Alternatively, to create a dedicated Python environment, [download the `r5py_distro.yaml`
file](https://github.com/r5py/r5py/blob/main/ci/r5py_distro.yaml), and use conda to create and activate the environment:

    conda env create -f r5py_distro.yaml
    conda activate r5py-env

## Install using `pip`

The ‘classic’ way to install Python packages is from the PyPi repository, using `pip`:

    pip install r5py

## Dependencies

**R5py** relies on a few external dependencies, most noteably a Java environment. 

### Java Development Kit

To interface with R5, **r5py** requires a *Java Development Kit* (jdk).
Please install a JDK in version 11, for instance, [OpenJDK](https://openjdk.java.net/java-se-ri/11).


### R5

**R5py** searches for a local R5 installation in the default class path (`/usr/share/java/r5/r5-all.jar`).
If it is not found, it automatically downloads its own copy of R5. The class path can be configured to
point to a different location, see *[Configuration](configuration)*).

```{note}
We generally recommend to install OpenJDK 11 (and R5, if available) using your operating system’s
package manager. That way, your system can keep track of installed packages and provide security
updates; as a side effect, your project directories/environments stay smaller.
```
