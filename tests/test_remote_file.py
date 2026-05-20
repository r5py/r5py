#!/usr/bin/env python3


import datetime
import os
import pathlib
import sys

import pytest

from r5py.util.config import Config
from r5py.util.remote_file import RemoteFile


class TestRemoteFile:
    def test_data_set_with_verbose(self, sample_data_set_url, sample_data_set_sha256):
        sys.argv.extend(
            [
                "--verbose",
            ]
        )

        # make sure the cached file does not exist
        try:
            (
                pathlib.Path(Config().CACHE_DIR)
                / "remote"
                / pathlib.Path(sample_data_set_url).name
            ).unlink()
        except FileNotFoundError:
            pass

        with pytest.warns(
            RuntimeWarning,
            match="First access to .*, downloading remote file to local cache",
        ):
            data_set = RemoteFile(sample_data_set_url, sample_data_set_sha256)
            assert data_set.exists()

        data_set.unlink()
        sys.argv = sys.argv[:-1]

    def test_data_set_with_verbose_without_checksum(self, sample_data_set_url):
        sys.argv.extend(
            [
                "--verbose",
            ]
        )

        # make sure the cached file does not exist
        try:
            (
                pathlib.Path(Config().CACHE_DIR)
                / "remote"
                / pathlib.Path(sample_data_set_url).name
            ).unlink()
        except FileNotFoundError:
            pass

        with pytest.warns(
            RuntimeWarning,
            match="First access to .*, downloading remote file to local cache",
        ):
            data_set = RemoteFile(sample_data_set_url)
            assert data_set.exists()

        data_set.unlink()
        sys.argv = sys.argv[:-1]

    def test_data_set_with_verbose_with_corruption(
        self, sample_data_set_url, sample_data_set_sha256
    ):
        sys.argv.extend(
            [
                "--verbose",
            ]
        )

        # make sure the cached file does not exist
        (pathlib.Path(Config().CACHE_DIR) / "remote").mkdir(parents=True, exist_ok=True)
        (
            pathlib.Path(Config().CACHE_DIR)
            / "remote"
            / pathlib.Path(sample_data_set_url).name
        ).write_text("CORRUPTED CONTENT OF SAMPLE DATA SET")

        with pytest.warns(
            RuntimeWarning,
            match=".* changed, re-downloading remote file to local cache",
        ):
            data_set = RemoteFile(sample_data_set_url, sample_data_set_sha256)
            assert data_set.exists()

        data_set.unlink()
        sys.argv = sys.argv[:-1]

    def test_data_set(self, sample_data_set_url, sample_data_set_sha256):
        data_set = RemoteFile(sample_data_set_url, sample_data_set_sha256)
        assert data_set.exists()
        data_set.unlink()

    def test_data_set_invalid_hash(self, sample_data_set_url, sample_data_set_sha256):
        data_set = RemoteFile(sample_data_set_url, sample_data_set_sha256)
        data_set.write_text("foobar")  # change file, invalidate checksum
        del data_set

        # try again:
        data_set = RemoteFile(sample_data_set_url, sample_data_set_sha256)
        assert data_set.exists()
        data_set.unlink()

    def test_expired_remote_file(self, sample_data_set_url):
        remote_file = RemoteFile(sample_data_set_url)
        EXPIRED = (
            datetime.datetime.now()
            - remote_file.max_cache_age
            - datetime.timedelta(days=1)
        ).timestamp()
        os.utime(remote_file, (EXPIRED, EXPIRED))

        del remote_file

        remote_file = RemoteFile(sample_data_set_url)
        assert remote_file.stat().st_mtime > EXPIRED
