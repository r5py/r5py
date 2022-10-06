#!/usr/bin/env python3

"""Handle configuration options and command line options."""

import os
import pathlib
import sys

import configargparse


__all__ = ["Config"]


class Config:
    """Load configuration from config files or command line arguments."""

    _instance = None  # stores singleton instance

    def __init__(self):
        """Load configuration from config files or command line arguments."""
        if "HOME" not in os.environ:  # e.g., testing environment or container
            os.environ["HOME"] = "."

        self.argparser.add(
            "-v",
            "--verbose",
            help="Enable verbose output from R5.",
            action="store_true",
        )

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
        return cls._instance

    @property
    def arguments(self):
        """Parse arguments passed from command line or config file."""
        arguments = self.argparser.parse_known_args()[0]
        return arguments

    _argparser = None  # class property: Singleton!

    @property
    def argparser(self):
        if self._argparser is None:
            try:
                self._argparser = configargparse.get_argument_parser(
                    prog=self.PACKAGE,
                    description=sys.modules[self.PACKAGE].__doc__,
                    default_config_files=self.CONFIG_FILES,
                )
            except ValueError:  # has been instantiated, already
                self._argparser = configargparse.get_argument_parser()
        return self._argparser

    @property
    def CACHE_DIR(self):
        try:
            self._cache_dir
        except AttributeError:
            self._cache_dir = (
                pathlib.Path(
                    os.environ.get("LOCALAPPDATA")
                    or os.environ.get("XDG_CACHE_HOME")
                    or (pathlib.Path(os.environ["HOME"]) / ".cache")
                )
                / self.PACKAGE
            )
            self._cache_dir.mkdir(parents=True, exist_ok=True)
        return self._cache_dir

    @property
    def CONFIG_FILES(self):
        try:
            self._config_files
        except AttributeError:
            self._config_files = [
                f"/etc/{self.PACKAGE}.yml",
                str(
                    pathlib.Path(
                        os.environ.get("APPDATA")
                        or os.environ.get("XDG_CONFIG_HOME")
                        or (pathlib.Path(os.environ["HOME"]) / ".config")
                    )
                    / f"{self.PACKAGE}.yml",
                ),
            ]
        return self._config_files

    PACKAGE = __package__.split(".")[0]
