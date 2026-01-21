#!/usr/bin/env python3


"""Fixtures describing the expected routing results."""

import pytest

from .routing_results import ISOCHRONES_WALK

ISOCHRONES_WALK_BLAKE2B = (
    "d4eb942274a4305fa5a66eac3c1157ea040a564dccb4284757df579b5c889edb"
    "f415f2c1a81114b3e36a503ced346a9788c4d5b6f2c2ccb3b6f81da86699f9ae"
)
ISOCHRONES_WALK_BLAKE2S = (
    "5213d4ffa8c6a0b9836b827f0f7455523f1542183e1936046ffb0fde776a36cc"
)
ISOCHRONES_WALK_SHA256 = (
    "18a384d2567d42dbb72f10666f8c4e0509dd814848bfb53b184896f920ddce9d"
)


@pytest.fixture
def file_digest_test_file_as_pathlib_path():
    """Return the path of a test file as a pathlib.Path."""
    yield ISOCHRONES_WALK


@pytest.fixture
def file_digest_test_file_as_str(file_digest_test_file_as_pathlib_path):
    """Return the path of a test file as a str."""
    yield f"{file_digest_test_file_as_pathlib_path}"


@pytest.fixture()
def file_digest_sha256():
    """Return the expected SHA256 hash for the test file."""
    yield ISOCHRONES_WALK_SHA256


@pytest.fixture()
def file_digest_blake2b():
    """Return the expected BLAKE2B hash for the test file."""
    yield ISOCHRONES_WALK_BLAKE2B


@pytest.fixture()
def file_digest_blake2s():
    """Return the expected BLAKE2S hash for the test file."""
    yield ISOCHRONES_WALK_BLAKE2S
