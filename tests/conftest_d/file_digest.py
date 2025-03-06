#!/usr/bin/env python3


"""Fixtures describing the expected routing results."""


import pytest

from .routing_results import ISOCHRONES_WALK


ISOCHRONES_WALK_BLAKE2B = "67f2f6aa6468c202e313d6096ca2490f767633eca6298ea8661dc5276316c81e70d48f21d76926ecd6b139433f5ca3a21d51b51094b0a8980db365013f3bd5bb"
ISOCHRONES_WALK_BLAKE2S = (
    "b4d9d947dd49f08c30cf7a5f01869de1c81655f1b3093a0c95338dda46ca7ba4"
)
ISOCHRONES_WALK_SHA256 = (
    "4ac9337e80211b82d6b5530ad815f5455eeb7ce2dfb79b017c7ce2fb3d9efc58"
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
