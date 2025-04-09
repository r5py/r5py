#!/usr/bin/env python3


"""Fixtures describing the expected routing results."""


import pytest

from .routing_results import ISOCHRONES_WALK


ISOCHRONES_WALK_BLAKE2B = "e5c0fe9d34b512363c876eec81439b2708a1171272dd721a40aefe502c6e0dc73811aab0f109a45ab83645b88dea38051112ede7fc4b99a1231d92e3b4492e11"
ISOCHRONES_WALK_BLAKE2S = (
    "3d46b490841df409cbb962e25d4201bda0eea5b825fc1181cb0babfddf457299"
)
ISOCHRONES_WALK_SHA256 = (
    "1d899da67faed2f49a0dd870b1dc33b4c7bd695b18eafc08640a662b442e935c"
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
