#!/usr/bin/env python3


import filecmp
import pathlib
import random

import pytest

from .temporary_directory import TemporaryDirectory

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

    @pytest.mark.parametrize(
        ["input_file_text_a", "input_file_text_b"],
        [("foo", "bar")],
    )
    def test_working_copy_change_source_file(
        self,
        input_file_text_a,
        input_file_text_b,
    ):
        with TemporaryDirectory() as temp_directory:
            input_file = pathlib.Path(temp_directory) / "test_input.txt"

            input_file.write_text(input_file_text_a)
            working_copy_a = WorkingCopy(input_file)
            assert working_copy_a.read_text() == input_file_text_a

            input_file.write_text(input_file_text_b)
            working_copy_b = WorkingCopy(input_file)
            assert working_copy_b.read_text() == input_file_text_b

    def test_working_copy_from_temp_directory(self):
        with TemporaryDirectory() as temp_directory:
            input_file = pathlib.Path(temp_directory) / "test_input.txt"
            input_file.write_text(f"{random.randrange(16**5):032x}")

            working_copy = WorkingCopy(input_file)

            assert filecmp.cmp(input_file, working_copy, shallow=False)

            working_copy.unlink()

    def test_working_copy_failed_symlink(self, monkeypatch):
        def _symlink_to(*args, **kwargs):
            raise OSError

        monkeypatch.setattr(pathlib.Path, "symlink_to", _symlink_to)

        with TemporaryDirectory() as temp_directory:
            input_file = pathlib.Path(temp_directory) / "test_input.txt"
            input_file.write_text(f"{random.randrange(16**5):032x}")

            working_copy = WorkingCopy(input_file)

            assert filecmp.cmp(input_file, working_copy, shallow=False)

            working_copy.unlink()
