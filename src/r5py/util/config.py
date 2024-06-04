#!/usr/bin/env python3

"""Handle configuration options and command line options."""

import functools
import os
import pathlib
import sys
import tempfile

import configargparse
import importlib_resources


__all__ = ["Config"]


PACKAGE = __package__.split(".")[0]
CONFIG_FILE_TEMPLATE = importlib_resources.files(f"{PACKAGE}.util").joinpath(
    f"{PACKAGE}.yml.template"
)

if "HOME" not in os.environ:  # e.g., testing environment or container
    os.environ["HOME"] = "."


class Config:
    """Load configuration from config files or command line arguments."""

    _instance = None  # stores singleton instance

    def __init__(self):
        """Load configuration from config files or command line arguments."""
        self.argparser.add(
            "-v",
            "--verbose",
            help="Enable verbose output from R5 and r5py",
            action="store_true",
        )

    def __new__(cls):
        """Load configuration from config files or command line arguments."""
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
        return cls._instance

    @property
    def arguments(self):
        """
        Arguments passed from command line or config file.

        Ignores `--help`: can be used while not all modules have added arguments.
        """
        return self.get_arguments(ignore_help_args=True)

    @property
    def argparser(self):
        """Return a singleton instance of a `configargparse.ArgumentParser`."""
        try:
            argparser = configargparse.get_argument_parser(
                prog=PACKAGE,
                description=sys.modules[PACKAGE].__doc__,
                default_config_files=self.CONFIG_FILES,
            )
        except ValueError:  # has been instantiated, already
            argparser = configargparse.get_argument_parser()
        return argparser

    @functools.cached_property
    def CACHE_DIR(self):
        """Save persistent cache files into this directory."""
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

    @functools.cached_property
    def CONFIG_FILES(self):
        """List locations of potential configuration files."""
        config_files = [
            pathlib.Path(f"/etc/{PACKAGE}.yml"),
            pathlib.Path(
                os.environ.get("APPDATA")
                or os.environ.get("XDG_CONFIG_HOME")
                or (pathlib.Path(os.environ["HOME"]) / ".config")
            )
            / f"{PACKAGE}.yml",
        ]

        # write a template configuration file to possible locations
        for config_file in config_files:
            self._copy_config_file_template(config_file)

        # argparse does not understand pathlib.Path
        config_files = [str(config_file) for config_file in config_files]

        return config_files

    @staticmethod
    def _copy_config_file_template(destination_path):
        """
        Try to copy a configuration file template.

        Arguments:
        ----------
        destination_path : pathlib.Path
            Where could/should a configuration file exist?
        """
        if not destination_path.exists():
            try:
                destination_path.parent.mkdir(parents=True, exist_ok=True)

                with importlib_resources.as_file(CONFIG_FILE_TEMPLATE) as template:
                    destination_path.write_text(template.read_text())

            except (
                FileNotFoundError,
                FileExistsError,
                IsADirectoryError,
                PermissionError,
            ):
                pass

    def get_arguments(self, ignore_help_args=False):
        """Parse arguments passed from command line or config file."""
        return self.argparser.parse_known_args(ignore_help_args=ignore_help_args)[0]

    @functools.cached_property
    def TEMP_DIR(self):
        """
        Save temporary files to this directory.

        read-only property,
        use command-line option `--temporary-directory` to change.
        """
        parent_dir = self.arguments.temporary_directory
        temp_dir = pathlib.Path(tempfile.mkdtemp(prefix=self.PACKAGE, dir=parent_dir))
        return temp_dir

    PACKAGE = PACKAGE


Config().argparser.add(
    "-t",
    "--temporary-directory",
    help="Directory for temporary files, overrides system default",
    default=None,
    type=pathlib.Path,
)
