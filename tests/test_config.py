#!/usr/bin/env python3


import datetime
import importlib
import pathlib
import os
import sys

import r5py.util.config
from r5py.util.config import CACHE_MAX_AGE


class TestConfig:
    def test_setdefaulthome(self):
        original_home = os.environ["HOME"]
        del os.environ["HOME"]
        importlib.reload(r5py.util.config)
        assert os.environ["HOME"] == "."
        os.environ["HOME"] = original_home

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

    def test_cache_clearing(self):
        config = r5py.util.config.Config()

        past_best_by_date = (
            datetime.datetime.now() - CACHE_MAX_AGE - datetime.timedelta(seconds=1)
        ).timestamp()

        expired_file = pathlib.Path(config.CACHE_DIR / "expired-file")
        expired_file.touch()
        os.utime(expired_file, (past_best_by_date, past_best_by_date))

        config.__dict__.pop("CACHE_DIR", None)  # clear functools.cached_property
        _ = config.CACHE_DIR  # re-evaluate cache dir contents

        assert not expired_file.exists()

    def test_cache_clearing_skip_directory(self):
        config = r5py.util.config.Config()

        past_best_by_date = (
            datetime.datetime.now() - CACHE_MAX_AGE - datetime.timedelta(seconds=1)
        ).timestamp()

        expired_directory = pathlib.Path(config.CACHE_DIR / "expired-dir")
        expired_directory.mkdir()
        os.utime(expired_directory, (past_best_by_date, past_best_by_date))

        config.__dict__.pop("CACHE_DIR", None)  # clear functools.cached_property
        _ = config.CACHE_DIR  # re-evaluate cache dir contents

        assert expired_directory.exists()
        try:
            expired_directory.rmdir()
        except PermissionError:
            pass  # Windows ...
