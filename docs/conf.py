# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
# import os
# import sys
# sys.path.insert(0, os.path.abspath('.'))


# -- Project information -----------------------------------------------------

project = 'r5py'
copyright = '2022, r5py contributors'
author = 'r5py contributors'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "IPython.sphinxext.ipython_console_highlighting",
    "myst_nb"
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_book_theme'

# if we are building a stable version, point the binder link to branch `stable`,
# otherwise, point to branch `main`
import os
try:
    READTHEDOCS_VERSION = os.environ["READTHEDOCS_VERSION"]
except KeyError:  # not running on RTD
    READTHEDOCS_VERSION = ""

if READTHEDOCS_VERSION == "stable":
    BINDER_REF = "stable"  # stable is synced with last version tag/release
elif READTHEDOCS_VERSION == "latest":
    BINDER_REF = "main"
else:
    import git
    repository = git.Repo(search_parent_directories=True)
    BINDER_REF = repository.git.rev_parse(repository.head.commit.hexsha, short=True)

html_theme_options = {
    # "external_links": [],
    "repository_url": "https://github.com/r5py/r5py/",
    "repository_branch": BINDER_REF,
    "path_to_docs": "docs",
    "use_edit_page_button": True,
    "launch_buttons": {
        "binderhub_url": "https://notebooks.gesis.org/binder",
        "thebelab": False,
        "notebook_interface": "jupyterlab",
    },
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# include __init__() in API doc
autoclass_content = 'init'

# add r5py’s package directory to path
import pathlib
import sys
sys.path.insert(0, str(pathlib.Path().absolute().parent / "src"))

# Do not execute cells
# (comment out following if you want to exclude executing notebooks during docs building)
# jupyter_execute_notebooks = "off"

# Hide title in left navbar
html_title = ""

# Logo
html_logo = "_static/r5py_blue.svg"
