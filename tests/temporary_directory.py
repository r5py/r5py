#!/usr/bin/env python3


"""TemporaryDirectory that cleans up gracefully (https://bugs.python.org/issue26660)."""


# see also https://www.scivision.dev/python-tempfile-permission-error-windows/
# (Python 3.10 has a fix, so as soon as we deprecate 3.9, this can be changed to
# `with tempfile.TemporaryDirectory(ignore_cleanup_errors=True)`


import pathlib
import tempfile


class TemporaryDirectory:
    """A `TemporaryDirectory` that cleans up gracefully (https://bugs.python.org/issue26660)."""

    def __init__(self):
        """Create a `TemporaryDirectory` that cleans up gracefully (https://bugs.python.org/issue26660)."""
        self.temp_directory = tempfile.TemporaryDirectory()

    def __enter__(self):
        """Provide a context."""
        return pathlib.Path(self.temp_directory.name)

    def __exit__(self, exception_type, exception_value, traceback):
        """Exit context."""
        try:
            self.temp_directory.cleanup()
        except (PermissionError, NotADirectoryError):
            pass  # let the operating system take care of it
