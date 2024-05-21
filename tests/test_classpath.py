#!/usr/bin/env python3


import pytest

import hashlib
import os
import pathlib
import sys

from r5py.util.classpath import find_r5_classpath
from r5py.util.config import Config
from r5py.util.exceptions import UnexpectedClasspathSchema


class TestClassPath:
    @pytest.mark.skipif(
        sys.platform == "win32", reason="Windows cannot delete jar while JVM runs"
    )
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

        try:
            pathlib.Path(r5_jar_cached).unlink()  # delete cached jar!
        except FileNotFoundError:
            pass

        with pytest.warns(RuntimeWarning, match="Could not find R5 jar"):
            r5_classpath = find_r5_classpath(Config().arguments)
        with open(r5_classpath, "rb") as r5_jar:
            digest = hashlib.sha256(r5_jar.read()).hexdigest()
        assert digest == r5_jar_sha256

        sys.argv = sys.argv[:-3]

    def test_use_classpath_from_local_file(
        self, r5_jar_url, r5_jar_sha256, r5_jar_cached
    ):
        # run `find_r5_classpath` once in order to download the jar into cache
        find_r5_classpath(Config().arguments)

        sys.argv.extend(["--r5-classpath", r5_jar_cached])

        r5_classpath = find_r5_classpath(Config().arguments)

        with open(r5_classpath, "rb") as r5_jar:
            digest = hashlib.sha256(r5_jar.read()).hexdigest()

        assert digest == r5_jar_sha256
        assert r5_classpath == r5_jar_cached

        sys.argv = sys.argv[:-2]

    def test_use_classpath_from_local_uri(
        self, r5_jar_url, r5_jar_sha256, r5_jar_cached
    ):
        # run `find_r5_classpath` once in order to download the jar into cache
        find_r5_classpath(Config().arguments)

        sys.argv.extend(["--r5-classpath", f"file://{r5_jar_cached}"])

        r5_classpath = find_r5_classpath(Config().arguments)

        with open(r5_classpath, "rb") as r5_jar:
            digest = hashlib.sha256(r5_jar.read()).hexdigest()

        assert digest == r5_jar_sha256
        assert r5_classpath == r5_jar_cached

        sys.argv = sys.argv[:-2]

    def test_use_classpath_from_remote_uri(
        self, r5_jar_url, r5_jar_sha256, r5_jar_cached
    ):
        sys.argv.extend(["--r5-classpath", r5_jar_url])

        r5_classpath = find_r5_classpath(Config().arguments)

        with open(r5_classpath, "rb") as r5_jar:
            digest = hashlib.sha256(r5_jar.read()).hexdigest()

        assert digest == r5_jar_sha256
        assert r5_classpath == r5_jar_cached

        sys.argv = sys.argv[:-2]

    def test_use_classpath_from_invalid_uri(self):
        sys.argv.extend(["--r5-classpath", "invalid://schema/and/path"])

        with pytest.raises(UnexpectedClasspathSchema):
            _ = find_r5_classpath(Config().arguments)

        sys.argv = sys.argv[:-2]

    def test_find_classpath_download(
        self, r5_jar_url, r5_jar_sha256, r5_jar_cached_invalid
    ):
        sys.argv.extend(["--r5-classpath", r5_jar_cached_invalid])
        r5_classpath = find_r5_classpath(Config().arguments)
        with open(r5_classpath, "rb") as r5_jar:
            digest = hashlib.sha256(r5_jar.read()).hexdigest()
        assert digest == r5_jar_sha256

        sys.argv = sys.argv[:-2]

    @pytest.mark.skipif(
        sys.platform == "win32", reason="No signal chaining library for Windows"
    )
    def test_signal_chaining(self):
        if sys.platform == "linux":
            assert "LD_PRELOAD" in os.environ
            assert pathlib.Path(os.environ["LD_PRELOAD"]).exists()
        elif sys.platform == "darwin":
            assert "DYLD_INSERT_LIBRARIES" in os.environ
            assert pathlib.Path(os.environ["DYLD_INSERT_LIBRARIES"]).exists()
