#!/usr/bin/env python3


"""A thin layer around com.conveyal.r5.file.FileStorage."""


import jpype

from ..util import start_jvm

import com.conveyal.file
import java.io.File


__all__ = ["FileStorage"]


start_jvm()


@jpype.JImplements(com.conveyal.file.FileStorage)
class FileStorage:
    """A thin layer around com.conveyal.r5.file.FileStorage."""

    @jpype.JOverride
    def moveIntoStorage(self, *args):
        """Not implemented."""
        pass

    @jpype.JOverride
    def getFile(self, file_storage_key):
        """
        Return a java.io.File for the file identified by file_storage_key.

        Arguments
        ---------
        file_storage_key : com.conveyal.r5.file.FileStorageKey
            An R5 object referencing a certain file

        Returns
        -------
        java.io.File
            The file identified by file_storage_key
        """
        return java.io.File(file_storage_key.path)

    @jpype.JOverride
    def getURL(self, file_storage_key):
        """
        Return an URL for the file identified by file_storage_key.

        Arguments
        ---------
        file_storage_key : com.conveyal.r5.file.FileStorageKey
            An R5 object referencing a certain file

        Returns
        -------
        str
            An imaginary URL pointing to the file identified by file_storage_key
        """
        return f"file://{file_storage_key.path}"

    @jpype.JOverride
    def delete(self, *args):
        """Not implemented."""
        pass

    @jpype.JOverride
    def exists(self, file_storage_key):
        """
        Check whether the file identified by file_storage_key exists.

        Arguments
        ---------
        file_storage_key : com.conveyal.r5.file.FileStorageKey
            An R5 object referencing a certain file

        Returns
        -------
        bool
            Whether or not the file identified by file_storage_key exists
        """
        return self.getFile(file_storage_key).exists()
