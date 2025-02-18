#!/usr/bin/env python3


"""Fixtures describing the expected routing results."""


import pytest

from .routing_results import ISOCHRONES_WALK


ISOCHRONES_WALK_SHA256 = (
    "4ccdb2c48c55054d2c6f5de60d47eaf50df8e637ff2e9836111a9519e7450d85"
)
ISOCHRONES_WALK_BLAKE2B = "72c129837f757d72a214c57cbb9545d3bd2ecc499053a5d941b012a479a1a7739b9622dbef7bb93c3f1ba95834bf84aed0aa73257956209ba1237bc690fc6ce6"
ISOCHRONES_WALK_BLAKE2S = (
    "e01d5543a03eb458b97959d4f1ea9b28c5d1e765751a5ae347a6b43df7cfdc51"
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
