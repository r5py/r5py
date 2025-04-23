#!/usr/bin/env python3


import pathlib

import r5py

import com.conveyal.file
import java.io


class TestFileStorage:
    def test_void_methods(self):
        file_storage = r5py.r5.file_storage.FileStorage()
        assert file_storage.moveIntoStorage() is None
        assert file_storage.delete() is None

    def test_get_file(self):
        file_storage = r5py.r5.file_storage.FileStorage()
        fake_file_path = pathlib.Path("/home/foo/bar.txt")
        gotten_file = file_storage.getFile(
            com.conveyal.file.FileStorageKey(
                com.conveyal.file.FileCategory.DATASOURCES,
                f"{fake_file_path.with_suffix('')}",
            )
        )
        assert isinstance(gotten_file, java.io.File)
        assert str(gotten_file) == f"{fake_file_path.with_suffix('')}"

    def test_get_url(self):
        file_storage = r5py.r5.file_storage.FileStorage()
        fake_file_path = pathlib.Path("/home/foo/bar.txt")
        gotten_url = file_storage.getURL(
            com.conveyal.file.FileStorageKey(
                com.conveyal.file.FileCategory.DATASOURCES,
                f"{fake_file_path.with_suffix('')}",
            )
        )
        assert isinstance(gotten_url, str)
        assert gotten_url == f"file://{fake_file_path.with_suffix('')}"

    def test_exists(self):
        file_storage = r5py.r5.file_storage.FileStorage()
        fake_file_path = pathlib.Path("/home/foo/bar.txt")
        exists = file_storage.exists(
            com.conveyal.file.FileStorageKey(
                com.conveyal.file.FileCategory.DATASOURCES,
                f"{fake_file_path.with_suffix('')}",
            )
        )
        assert not exists
