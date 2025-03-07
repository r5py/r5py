#!/usr/bin/env python3


"""Fixtures describing the expected routing results."""


import pytest

from .routing_results import ISOCHRONES_WALK


ISOCHRONES_WALK_BLAKE2B = "5e91181cfdff18a3ebcf289eba1955b61b27260fa40d1cd669bb2f754c31b23b59ecd74ee9d3a31f2d51c9de32aff0781ff5c948eb4ea220b622525d94e6a625"
ISOCHRONES_WALK_BLAKE2S = (
    "da098b9fcf440e7252b2b213160dd810392c03ee07c58ababfddf7d4c5d8d502"
)
ISOCHRONES_WALK_SHA256 = (
    "2a444c35ef676928d2a70914c64e34c569b10a6473ee6d61c74d9740351d80cc"
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
