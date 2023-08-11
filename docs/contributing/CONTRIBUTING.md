# How to contribute to *r5py*

Contributions of any kind to *r5py* are more than welcome. That does not mean
new code only, but also improvements of documentation and user guide, additional
tests (ideally filling the gaps in existing suite) or a bug report. In addition,
we warmly welcome ideas of new features that could be added to the *r5py*, or
ideas on how to improve the existing codebase.

All contributions should go through our GitHub repository. Bug reports, ideas or
even questions should be raised by opening an issue on the GitHub tracker.
Suggestions for changes in code or documentation should be submitted as a pull
request. However, if you are not sure what to do, feel free to open an issue.
All discussion will then take place on GitHub to keep the development of *r5py*
transparent.

If you decide to contribute to the codebase, ensure that you are using an
up-to-date `main` branch. The latest development version will always be there,
including the documentation (powered by [sphinx](https://www.sphinx-doc.org/)).

## Seven Steps for Contributing

There are seven basic steps to contributing to *r5py*:

1. [Fork the *r5py* git repository](#1-fork-the-r5py-git-repository)
2. [Create a development environment with *r5py*
   dependencies](#2-create-a-development-environment)
3. [Make a development build of *r5py*](#3-make-a-development-build)
4. [Make changes to the code and add tests](#4-make-changes-and-write-tests)
5. [Update the documentation](#5-update-the-documentation-and-user-guide)
6. [Format and lint the code](#6-format-the-code)
7. [Submit a Pull Request](#7-submit-a-pull-request)

Each of the steps is detailed below.

### 1. Fork the *r5py* git repository

Git can be complicated for new users, but you no longer need to use command line
to work with git. If you are not familiar with git, we recommend using tools on
Github.com, GitHub Desktop or tools with included git like Atom or PyCharm.
However, if you want to use command line, you can fork the *r5py* repository
using following:

:::{code} sh

git clone git@github.com:your-user-name/r5py.git r5py-yourname
cd r5py-yourname
git remote add upstream git://github.com/r5py/r5py.git

:::

This creates the directory `r5py-yourname` and connects your repository to
the upstream (main project) r5py repository.

Then simply create a new branch of main branch.

### 2. Create a development environment

A development environment is a virtual space where you can keep an independent
installation of *r5py*. This makes it easy to keep both a stable version of
python in one place you use for work, and a development version (which you may
break while playing with code) in another.

An easy way to create a *r5py* development environment is as follows:

- Install [MambaForge](https://github.com/conda-forge/miniforge#mambaforge) (or
  [install mamba using
  conda](https://r5py.readthedocs.io/en/latest/installation.html#install-mamba))
- Make sure that you have **cloned the *r5py* repository**
- `cd` to the *r5py* source directory (the root folder)

Tell `mamba` to create a new environment from a [YAML
file](https://github.com/r5py/r5py/blob/main/ci/python_311_dev.yaml) inside `ci`
directory, by running:

:::{code} sh

mamba env create -f ci/python_311_dev.yaml

:::

This will create a new environment called `r5py`, and not touch any of your
existing environments, nor existing python installations. The environment
includes all necessary dependencies for *r5py*, as well as optional packages for
running tests and building docs.  With this environment, you can directly start
working with *r5py*.

To work in this environment, you should `activate` it as follows:

:::{code} sh

conda activate r5py

:::

You will then see a confirmation message to indicate you are in the new
development environment.

To view your environments:

:::{code} sh

  conda info -e

:::

To return to you home root environment::

:::{code} sh

  deactivate

:::

See the full conda docs [here](http://conda.pydata.org/docs).

### 3. Make a development build

Once dependencies are in place, make an in-place build by navigating to the git
clone of the *r5py* repository and run:

:::{code} sh

pip install .

:::

This will install *r5py* from the source into your environment.

### 4. Make changes and write tests

*r5py* is serious about testing and strongly encourages contributors to embrace
[test-driven development
(TDD)](http://en.wikipedia.org/wiki/Test-driven_development).  This development
process "relies on the repetition of a very short development cycle: first the
developer writes an (initially failing) automated test case that defines a
desired improvement or new function, then produces the minimum amount of code to
pass that test." So, before actually writing any code, you should write your
tests. Often the test can be taken from the original GitHub issue. However, it
is always worth considering additional use cases and writing corresponding
tests.

*r5py* uses the [pytest testing system](http://doc.pytest.org/en/latest).

#### Write tests

All tests should go into the `tests` directory. This folder contains many
current examples of tests, and we suggest looking to these for inspiration.

#### Run the test suite

The tests can then be run directly inside your Git clone without having to
install *r5py*. Run the tests by typing (`v` means *verbose*):

:::{code} sh

pytest -v

:::


### 5. Update the documentation and user guide

*r5py* documentation resides in the `docs` folder. Changes to the docs are make
by modifying the appropriate file within `docs`.  *r5py* docs uses [Myst
notebooks](https://myst-nb.readthedocs.io/), a format for executable notebooks
using a syntax based on Markdown. Docstrings follow the [Numpy Docstring
standard](https://github.com/numpy/numpy/blob/master/doc/HOWTO_DOCUMENT.rst.txt).

Once you have made your changes, you may try if they render correctly by
building the docs using Sphinx (comes with `r5py` environment if [installed from
the YAML file](#2-create-a-development-environment)).  To do so, you can
navigate to the `docs` folder and type:

:::{code} python

python -m sphinx . _build

:::

The resulting html pages will be located in `docs/_build/html/`.


### 6. Format the code

#### Python (PEP8 / black)

*r5py* follows the [PEP8](http://www.python.org/dev/peps/pep-0008) standard
and uses [Black](https://black.readthedocs.io/en/stable/) to ensure a consistent code format throughout the project.

CI will run `black --check` and fails if there are files which would be
auto-formatted by `black`. Therefore, it is helpful before submitting code to
auto-format your code::

:::{code} python

black src

:::

Additionally, many editors have plugins that will apply `black` as you edit files.
If you don't have black, you can install it using pip:

:::{code} python

pip install black

:::


#### Import order, import of submodules

**R5py** uses [jpype](https://jpype.readthedocs.io), with the help of which Java
classes can be imported using normal `import` statements. As a consequence, the
order of import statements at the beginning of source files plays a crucial
role.

By convention, in *r5py* source files, the import statements should be grouped
in the following order:

1. Imports of modules of the Python Standard Library
2. Imports of third-party Python modules
3. Relative imports of other *r5py* modules
4. Imports of Java classes

The modules of each group should be sorted alphabetically, the groups be
separated by an empty line.

The import of submodules (`from ... import ...`), as well as the use of aliases
for imported modules (`import ... as ...`) are discouraged. An exception to this
rule, assets from other modules from within *r5py* should always be imported as
submodules (`from . import TravelTimeMatrixComputer`).


### 7. Submit a *Pull Request*

Once you've made changes and pushed them to your forked repository, you then
submit a pull request to have them integrated into the *r5py* code base.

You can find a pull request (or PR) tutorial in the [GitHub's Help
Docs](https://help.github.com/articles/using-pull-requests).

### References

These contribution guidelines are largely based on
[pyrosm](https://pyrosm.readthedocs.io/en/latest/) and
[momepy](http://docs.momepy.org/en/stable/) -libraries.
