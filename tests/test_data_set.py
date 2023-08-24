#!/usr/bin/env python3


import pathlib
import sys

import pytest

from r5py.util.config import Config
from r5py.util.data_set import DataSet


class TestDataSet:
    def test_data_set_with_verbose(self, sample_data_set_url, sample_data_set_sha256):
        sys.argv.extend(
            [
                "--verbose",
            ]
        )
        try:
            (
                pathlib.Path(Config().CACHE_DIR)
                / pathlib.Path(sample_data_set_url).name
            ).unlink()
        except FileNotFoundError:
            pass

        data_set = DataSet(sample_data_set_url, sample_data_set_sha256)
        with pytest.warns(RuntimeWarning, match="First access to .*, downloading remote file to local cache"):
            assert data_set.exists()

        data_set.unlink()
        sys.argv = sys.argv[:-1]

    def test_data_set(self, sample_data_set_url, sample_data_set_sha256):
        data_set = DataSet(sample_data_set_url, sample_data_set_sha256)
        assert data_set.exists()
        data_set.unlink()

    def test_data_set_invalid_hash(self, sample_data_set_url, sample_data_set_sha256):
        data_set = DataSet(sample_data_set_url, sample_data_set_sha256)
        data_set.write_text("foobar")  # change file, invalidate checksum
        del data_set

        # try again:
        data_set = DataSet(sample_data_set_url, sample_data_set_sha256)
        assert data_set.exists()
        data_set.unlink()
