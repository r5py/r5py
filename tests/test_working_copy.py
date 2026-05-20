#!/usr/bin/env python3


import pathlib

from r5py.util.config import Config
from r5py.util.sample_data_set import SampleDataSet
from r5py.util.working_copy import WorkingCopy


class TestWorkingCopy:
    def test_working_copy_with_https_url(self, sample_data_set_url):
        working_copy = WorkingCopy(sample_data_set_url)
        assert pathlib.Path(Config().CACHE_DIR / working_copy.name).exists()

    def test_working_copy_with_file_url(
        self, sample_data_set_url, sample_data_set_sha256
    ):
        sample_data_set = SampleDataSet(sample_data_set_url, sample_data_set_sha256)
        working_copy = WorkingCopy(f"file://{sample_data_set}")
        assert pathlib.Path(Config().CACHE_DIR / working_copy.name).exists()
