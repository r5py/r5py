#!/usr/bin/env python3


import pytest
import pytest_lazy_fixtures

import r5py.util


class TestFileDigest:
    @pytest.mark.parametrize(
        ["input_file", "expected_digest"],
        [
            (
                pytest_lazy_fixtures.lf("file_digest_test_file_as_pathlib_path"),
                pytest_lazy_fixtures.lf("file_digest_blake2s"),
            ),
            (
                pytest_lazy_fixtures.lf("file_digest_test_file_as_str"),
                pytest_lazy_fixtures.lf("file_digest_blake2s"),
            ),
        ],
    )
    def test_file_digest(self, input_file, expected_digest):
        assert r5py.util.FileDigest(input_file) == expected_digest

    @pytest.mark.parametrize(
        ["input_file", "digest_algorithm", "expected_digest"],
        [
            (
                pytest_lazy_fixtures.lf("file_digest_test_file_as_pathlib_path"),
                "blake2s",
                pytest_lazy_fixtures.lf("file_digest_blake2s"),
            ),
            (
                pytest_lazy_fixtures.lf("file_digest_test_file_as_str"),
                "blake2s",
                pytest_lazy_fixtures.lf("file_digest_blake2s"),
            ),
            (
                pytest_lazy_fixtures.lf("file_digest_test_file_as_pathlib_path"),
                "blake2b",
                pytest_lazy_fixtures.lf("file_digest_blake2b"),
            ),
            (
                pytest_lazy_fixtures.lf("file_digest_test_file_as_str"),
                "blake2b",
                pytest_lazy_fixtures.lf("file_digest_blake2b"),
            ),
            (
                pytest_lazy_fixtures.lf("file_digest_test_file_as_pathlib_path"),
                "sha256",
                pytest_lazy_fixtures.lf("file_digest_sha256"),
            ),
            (
                pytest_lazy_fixtures.lf("file_digest_test_file_as_str"),
                "sha256",
                pytest_lazy_fixtures.lf("file_digest_sha256"),
            ),
        ],
    )
    def test_file_digest_algorithms(
        self, input_file, digest_algorithm, expected_digest
    ):
        assert r5py.util.FileDigest(input_file, digest_algorithm) == expected_digest
