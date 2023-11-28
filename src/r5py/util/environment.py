#!/usr/bin/env python3


"""Normalise some environment variables that might not always get set."""


import os
import pathlib


# if a readthedocs runner uses a conda environment, it fails to
# properly initialise the JAVA_HOME and PROJ_LIB environment variables
#
# this might happen on other installation, so let’s keep this as general
# as possible.
#
# As readthedocs also does not export CONDA_PREFIX, we first reconstruct
# it from CONDA_ENVS_PATH and CONDA_DEFAULT_ENV
if (
    "CONDA_PREFIX" not in os.environ
    and "CONDA_DEFAULT_ENV" in os.environ
    and "CONDA_ENVS_PATH" in os.environ
):
    os.environ["CONDA_PREFIX"] = str(
        pathlib.Path(os.environ["CONDA_ENVS_PATH"]) / os.environ["CONDA_DEFAULT_ENV"]
    )
if "JAVA_HOME" not in os.environ and "CONDA_PREFIX" in os.environ:
    os.environ["JAVA_HOME"] = str(
        pathlib.Path(os.environ["CONDA_PREFIX"]) / "lib" / "jvm"
    )
if "PROJ_LIB" not in os.environ and "CONDA_PREFIX" in os.environ:
    os.environ["PROJ_LIB"] = str(
        pathlib.Path(os.environ["CONDA_PREFIX"]) / "share" / "proj"
    )
