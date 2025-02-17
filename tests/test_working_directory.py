#!/usr/bin/env python3


import filecmp
import pathlib
import random

from .temporary_directory import TemporaryDirectory

import r5py.util


class TestWorkingDirectory:
    def test_working_directory(self):
        with TemporaryDirectory() as temp_directory:
            input_file = pathlib.Path(temp_directory) / "test_input.txt"
            input_file.write_text(f"{random.randrange(16**5):032x}")

            working_copy = r5py.util.WorkingCopy(input_file)

            assert filecmp.cmp(input_file, working_copy, shallow=False)
