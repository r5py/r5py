#!/usr/bin/env python3

"""Handle configuration options and command line options."""

import os
import sys

import configargparse

__all__ = [
    "argparser",
    "arguments"
]


PACKAGE = __package__.split(".")[0]


argparser = configargparse.get_argument_parser(
    prog=PACKAGE,
    description=sys.modules[PACKAGE].__doc__,
    default_config_files=[
        "/etc/{:s}.yml".format(__package__),
        os.path.join(
            (
                os.environ.get("APPDATA")
                or os.environ.get("XDG_CONFIG_HOME")
                or os.path.join(os.environ["HOME"], ".config")
            ),
            "{:s}.yml".format(__package__)
        )
    ]
)


def arguments():
    """Parse arguments passed from command line or config file."""
    arguments = argparser.parse_known_args()[0]
    return arguments
