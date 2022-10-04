#!/usr/bin/env python3

"""Handle configuration options and command line options."""

import os
import pathlib
import sys

import configargparse


__all__ = ["argparser", "arguments", "CACHE_DIR", "CONFIG_FILES", "PACKAGE"]


PACKAGE = __package__.split(".")[0]


def find_cache_dir():
    if "HOME" not in os.environ:  # e.g., testing environment or container
        os.environ["HOME"] = "."

    cache_dir = (
        pathlib.Path(
            os.environ.get("LOCALAPPDATA")
            or os.environ.get("XDG_CACHE_HOME")
            or (pathlib.Path(os.environ["HOME"]) / ".cache")
        )
        / PACKAGE
    )
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir


CACHE_DIR = find_cache_dir()


CONFIG_FILES = [
    f"/etc/{PACKAGE}.yml",
    str(
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
