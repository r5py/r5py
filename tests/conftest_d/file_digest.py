#!/usr/bin/env python3


"""Fixtures describing the expected routing results."""


import pytest

from .routing_results import ISOCHRONES_WALK


ISOCHRONES_WALK_BLAKE2B = "163f6b2bc985e7eb347020320392a151ba1c156a09e82f87c0149273de2714516a098984e581bf99742c075232e18d69f5171370589cb5ec64d70f42f539f76c"
ISOCHRONES_WALK_BLAKE2S = (
    "9f0af2c9946982b2e7d17a0b2205b596cbef01b1037874f5ad72348407ad381e"
)
ISOCHRONES_WALK_SHA256 = (
    "b632d148ca5d9875482197461809f25fe790d71827e821983cefe2394841b417"
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
