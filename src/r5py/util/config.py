#!/usr/bin/env python3

"""Handle configuration options and command line options."""

import os
import pathlib
import sys

import configargparse


__all__ = ["argparser", "arguments", "CACHE_DIR", "CONFIG_FILES", "PACKAGE"]


PACKAGE = __package__.split(".")[0]

if "HOME" not in os.environ:  # e.g., testing environment or container
    os.environ["HOME"] = "."

CACHE_DIR = (
    pathlib.Path(
        os.environ.get("LOCALAPPDATA")
        or os.environ.get("XDG_CACHE_HOME")
        or (pathlib.Path(os.environ["HOME"]) / ".cache")
    )
    / PACKAGE
)
CACHE_DIR.mkdir(parents=True, exist_ok=True)

CONFIG_FILES = [
    f"/etc/{PACKAGE}.yml",
    (
        pathlib.Path(
            os.environ.get("APPDATA")
            or os.environ.get("XDG_CONFIG_HOME")
            or (pathlib.Path(os.environ["HOME"]) / ".config")
        )
        / f"{PACKAGE}.yml",
    ),
]

argparser = configargparse.get_argument_parser(
    prog=PACKAGE,
    description=sys.modules[PACKAGE].__doc__,
    default_config_files=CONFIG_FILES,
)

argparser.add(
    "-v", "--verbose", help="Enable verbose output from R5." "", action="store_true"
)


def arguments():
    """Parse arguments passed from command line or config file."""
    arguments = argparser.parse_known_args()[0]
    return arguments
