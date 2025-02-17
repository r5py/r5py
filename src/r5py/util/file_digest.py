#!/usr/bin/env python3

"""Create a hash sum of a file."""


import hashlib
import pathlib


__all__ = ["FileDigest"]


class FileDigest(str):
    """Create a hash sum of a file."""
    def __new__(cls, input_file, digest="blake2s"):
        """
        Create a hash sum of a file.

        Arguments
        ---------
        input_file : pathlib.Path | str
            for which file to compute a hash digest
        digest : str | func
            name of hash algorithm (s.
            https://docs.python.org/3/library/hashlib.html) or function that
            returns a hash sum
        """
        input_file = pathlib.Path(input_file)
        with input_file.open("rb") as f:
            hashdigest = hashlib.file_digest(f, digest)
        return hashdigest.hexdigest()
