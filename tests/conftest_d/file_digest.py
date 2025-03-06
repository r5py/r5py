#!/usr/bin/env python3


"""Fixtures describing the expected routing results."""


import pytest

from .routing_results import ISOCHRONES_WALK


ISOCHRONES_WALK_SHA256 = (
    "514c2a2fe59e399f1557b2bf145fc32390a42d2b0285142ad04cffbf1472afea"
)
ISOCHRONES_WALK_BLAKE2B = "1ee14b5a55dfa5d9af10ca9f50770c825612e32d6bcb690dba8d618aefbef14df2fd615b2dfe5dd3365059912842be8437470bbe902f662162a767ef8bf68772"
ISOCHRONES_WALK_BLAKE2S = (
    "f7e34c777f057ffe94ccb9de0739b549f7504acc2c7eb1a0cc630973854818b8"
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
