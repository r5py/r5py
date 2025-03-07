#!/usr/bin/env python3

"""Create a copy or link of an input file in a cache directory."""


import filelock
import pathlib
import shutil

from .config import Config


__all__ = ["WorkingCopy"]


class WorkingCopy(pathlib.Path):
    """Create a copy or link of an input file in a cache directory."""

    def __new__(cls, path):
        """
        Create a copy or link of an input file in a cache directory.

        This exists because R5 creates temporary files in the directory of input
        files. This can not only be annoying clutter, but also create problems
        of concurrency, performance, etc., for instance, when the data comes
        from a shared network drive or a read-only file system.

        Arguments
        ---------
        path : str or pathlib.Path
            The file to create a copy or link of in a cache directory
        """
        # try to first create a symbolic link, if that fails (e.g., on Windows),
        # copy the file to a cache directory
        path = pathlib.Path(path).absolute()
        destination = pathlib.Path(Config().CACHE_DIR / path.name).absolute()

        with filelock.FileLock(destination.parent / f"{destination.name}.lock"):
            if not destination.exists():
                try:
                    destination.symlink_to(path)
                except OSError:
                    shutil.copyfile(f"{path}", f"{destination}")
        return destination
