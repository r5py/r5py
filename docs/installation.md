# Installation

There are many ways to install `r5py` to your computer. In this page, we document different options for installing the library.
For most users, we recommend to install r5py and all its dependencies (incl. Java Developent Kit) from conda-forge. 
Please see the [dependencies](#dependencies) section to understand what will be installed to your computer.

**Contents:**

 - [Install r5py with mamba](#install-using-mamba)
 - [Install r5py with conda](#install-using-conda)
 - [Install r5py with pip](#install-using-pip)
 - [Dependencies](#dependencies)

## Install using `mamba`

The best way to install `r5py` is by installing [Mambaforge](https://github.com/conda-forge/miniforge#mambaforge) (available for Windows/Linux/Mac), which is a drop-in replacement to a popular package distribution [Miniconda](https://docs.conda.io/en/latest/miniconda.html),
but comes with a significantly faster package manager called `mamba`. Mamba solves dependencies and installs Python packages faster than `conda`, 
and when it is installed from [Mambaforge](https://github.com/conda-forge/miniforge#mambaforge), it by default uses only `conda-forge` channel to fetch 
packages. This is a good thing because it helps avoiding dependency conflicts and potential issues with licensing (see [this blog post](https://florianwilhelm.info/2021/09/Handling_Anaconda_without_getting_constricted/)).
If you are new to (sometimes confusing) Python package managers, you can read more information [from here](https://python-gis-book.readthedocs.io/en/develop/part1/chapter-01/nb/05-installation.html).

If you don't have `mamba` yet available on your system:

1. Download and install [Mambaforge](https://github.com/conda-forge/miniforge#mambaforge) for your operating system.
2. Alternatively, if you are already using `conda`, you can install mamba to your `base` environment by:

       conda install -n base -c conda-forge mamba 

### Install r5py to your environment 

1. Install r5py and Java Development Kit (OpenJDK) with `mamba` by executing following command from terminal:
    
       mamba install -c conda-forge r5py openjdk

After this r5py is ready for use in your Python environment. 

### Install r5py to a dedicated Python environment

As an alternative approach (for the step 2 above), you can also install r5py and a few useful Python packages into a dedicated conda environment called `r5py-env` (uses Python 3.10).

1. [Download the r5py_distro.yaml file](../ci/r5py_distro.yaml) to your computer 
2. Navigate with a terminal to the folder where you downloaded the file
3. Execute following command which will install the packages into environment called `r5py-env`:

       mamba env create -f r5py_distro.yaml

4. Activate the `r5py-env` environment:
       
       conda activate r5py-env

After this, you can start using the `r5py` library in the environment e.g. using [JupyterLab](https://jupyterlab.readthedocs.io/en/stable/) which was 
installed as part of the environment. 

## Install using `conda` 

If you are using `conda` as your package manager, you can install r5py with following steps (although we highly recommend using `mamba`!).

1. Download and install [Miniconda](https://docs.conda.io/en/latest/miniconda.html) for your operating system.
2. Install r5py and Java Development Kit (OpenJDK) with `conda` by executing following command from terminal:
    
       conda install -c conda-forge r5py openjdk

After this r5py is ready for use in your Python environment. Alternatively, you can install the r5py into a dedicated Python
environment by following the [instructions above](#install-r5py-to-dedicated-python-environment) but by replacing the `mamba` 
command to `conda` (as mamba is a direct drop-in replacement for conda).
  
## Install using pip
  
You can also install r5py from PyPi, e.g., using `pip`:  

    pip install r5py    
  
In addition, to be able to use r5py, you need to install a *Java Development Kit*, for instance,  
[OpenJDK](http://jdk.java.net/java-se-ri/11), in version 11. If you are on  
Linux, please use the jdk provided by your operating system’s package manager.

## Dependencies

### Java Development Kit

To interface with R5, **r5py** requires a *Java Development Kit* (jdk) in version 11. [OpenJDK](https://openjdk.java.net/) works fine.


### R5

**R5py** searches for a local R5 installation in the default class path (`/usr/share/java/r5/r5-all.jar`). If it is not found, it automatically downloads its own copy of R5. The class path can be configured to point to a different location, see *[Configuration](configuration)*). 


### Python

**R5py** requires Python in version 3.8 or later.


### Python modules

If installed using `mamba`, `conda` or `pip`, all Python modules that **r5py** depends on are installed as dependencies.
