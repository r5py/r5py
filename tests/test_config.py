#!/usr/bin/env python3


import importlib
import os
import sys

import r5py.util.config


class TestConfig:
    def test_setdefaulthome(self):
        del os.environ["HOME"]
        importlib.reload(r5py.util.config)
        assert os.environ["HOME"] == "."

    def test_custom_temporary_directory(self, tmp_path):
        sys.argv.extend(
            [
                "--temporary-directory",
                f"{tmp_path}",
            ]
        )
        assert r5py.util.config.Config().arguments.temporary_directory.is_relative_to(
            tmp_path
        )
        sys.argv = sys.argv[:-2]
