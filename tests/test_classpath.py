#!/usr/bin/env python3


import pytest  # noqa: F401

import hashlib
import pathlib
import sys

from r5py.util.classpath import find_r5_classpath
from r5py.util.config import arguments


class TestClassPath:
    def test_download_classpath_with_verbose(
        self, r5_jar_url, r5_jar_sha256, r5_jar_cached, r5_jar_cached_invalid
    ):
        sys.argv.extend(
            [
                "--verbose",
                "--r5-classpath",
                r5_jar_cached_invalid,
            ]
        )
        pathlib.Path(r5_jar_cached).unlink()  # delete cached jar!

        with pytest.warns(RuntimeWarning):
            r5_classpath = find_r5_classpath(arguments())
        digest = hashlib.sha256(open(r5_classpath, "rb").read()).hexdigest()
        assert digest == r5_jar_sha256

    def test_use_classpath_from_local_file(
        self, r5_jar_url, r5_jar_sha256, r5_jar_cached
    ):
        # run `find_r5_classpath` once in order to download the jar into cache
        find_r5_classpath(arguments())

        sys.argv.extend(["--r5-classpath", r5_jar_cached])

        r5_classpath = find_r5_classpath(arguments())

        digest = hashlib.sha256(open(r5_classpath, "rb").read()).hexdigest()

        assert digest == r5_jar_sha256
        assert r5_classpath == r5_jar_cached

    def test_find_classpath_download(
        self, r5_jar_url, r5_jar_sha256, r5_jar_cached_invalid
    ):
        sys.argv.extend(["--r5-classpath", r5_jar_cached_invalid])
        r5_classpath = find_r5_classpath(arguments())
        digest = hashlib.sha256(open(r5_classpath, "rb").read()).hexdigest()
        assert digest == r5_jar_sha256
