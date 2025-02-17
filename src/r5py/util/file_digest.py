#!/usr/bin/env python3

"""Create a hash sum of a file."""


import hashlib
import pathlib


__all__ = ["FileDigest"]


BUFFER_SIZE = 64 * 1024


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
        try:
            with input_file.open("rb") as f:
                hashdigest = hashlib.file_digest(f, digest)
        except AttributeError:  # Python<=3.10
            hashdigest = hashlib.new(digest)
            with input_file.open("rb") as f:
                while data := f.read(BUFFER_SIZE):
                    hashdigest.update(data)

        return hashdigest.hexdigest()
