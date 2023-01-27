# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html


import pathlib
import sys

# import matplotlib here, otherwise we get the
# ‘building font cache’ warning in the middle of
# a notebook (when it runs for the first time)
import matplotlib.pyplot

# -- Add project paths -------------------------------------------------------
sys.path = [
    str(pathlib.Path().resolve().parent / "src"),
    str(pathlib.Path().resolve()),
] + sys.path

from binder_ref import BINDER_REF


# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "r5py"
copyright = "2022, r5py contributors"
author = "r5py contributors"


# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "myst_nb",
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
    "sphinxcontrib.images",
    "sphinx_design",
]

templates_path = ["_templates"]
exclude_patterns = [
    "_build",
    "jupyter_execute",
    "_static",
]

source_suffix = {
    ".rst": "restructuredtext",
    ".ipynb": "myst-nb",
    ".myst": "myst-nb",
}

myst_enable_extensions = [
    "colon_fence",
    "deflist",
    "substitution",
]
myst_heading_anchors = 3  # add #id to h1-h3


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_logo = "_static/images/r5py_blue.svg"
html_favicon = "_static/images/favicon.png"
html_title = ""
html_short_title = "r5py"

html_static_path = ["_static"]
html_css_files = ["custom.css"]
html_last_updated_fmt = "%d %B %Y"

html_theme = "sphinx_book_theme"
html_theme_options = {
    "collapse_navigation": False,
    "launch_buttons": {
        "binderhub_url": "https://mybinder.org",
        "notebook_interface": "classic",
    },
    "path_to_docs": "docs",
    "repository_branch": BINDER_REF,
    "repository_url": "https://github.com/r5py/r5py/",
    "use_edit_page_button": True,
    "use_repository_button": True,
}

# include __init__() in API doc
autoclass_content = "init"

intersphinx_mapping = {
    "geopandas": ("https://geopandas.org/en/stable/", None),
    "gtfslite": ("https://gtfs-lite.readthedocs.io/en/stable/", None),
    "pandas": ("https://pandas.pydata.org/docs/", None),
    "python": ("https://docs.python.org/3/", None),
    "shapely": ("https://shapely.readthedocs.io/en/stable/", None),
}

nb_execution_mode = "force"
nb_execution_timeout = 120  # needed, e.g., when matplotlib updates its font cache
nb_execution_show_tb = True  # show traceback in case of error
