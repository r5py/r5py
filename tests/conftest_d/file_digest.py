#!/usr/bin/env python3


"""Fixtures describing the expected routing results."""


import pytest

from .routing_results import ISOCHRONES_WALK


ISOCHRONES_WALK_SHA256 = (
    "e0ff69b3e6ac80b8798f2033953a2d65817bf94af014136ad842764c11e8d7c0"
)
ISOCHRONES_WALK_BLAKE2B = "4d1c6d91fd548420dbd81f6dec84d948da91172809461bcc29794c04337a6b6145fc6fb1de7369b40d68ba94e0f5ed67b168a287bfcd7765ca9f62920c0d2fcc"
ISOCHRONES_WALK_BLAKE2S = (
    "4b3dcddca75127414325a43b3a5de77bda48e6741bc45a68cecb48b5b80f8426"
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
