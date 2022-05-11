#!/usr/bin/env python3

"""Handle configuration options and command line options."""

import os
import os.path
import sys

import configargparse


__all__ = ["argparser", "arguments", "CACHE_DIR", "CONFIG_FILES", "PACKAGE"]


PACKAGE = __package__.split(".")[0]

if "HOME" not in os.environ:  # e.g., testing env
    os.environ["HOME"] = "."

CACHE_DIR = os.path.join(
    (
        os.environ.get("LOCALAPPDATA")
        or os.environ.get("XDG_CACHE_HOME")
        or os.path.join(os.environ["HOME"], ".cache")
    ),
    PACKAGE,
)
CONFIG_FILES = [
    "/etc/{:s}.yml".format(PACKAGE),
    os.path.join(
        (
            os.environ.get("APPDATA")
            or os.environ.get("XDG_CONFIG_HOME")
            or os.path.join(os.environ["HOME"], ".config")
        ),
        "{:s}.yml".format(PACKAGE),
    ),
]


argparser = configargparse.get_argument_parser(
    prog=PACKAGE,
    description=sys.modules[PACKAGE].__doc__,
    default_config_files=CONFIG_FILES,
)


def arguments():
    """Parse arguments passed from command line or config file."""
    arguments = argparser.parse_known_args()[0]
    return arguments
