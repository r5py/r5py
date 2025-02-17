#!/usr/bin/env python3


"""Fixtures describing the expected routing results."""


import pytest

from .routing_results import TRAVEL_TIMES_WALK


TRAVEL_TIMES_WALK_SHA256 = "fefe71155352c8daddfa84ea3f1bcc6c17dd7f358b1a17d0c3e361d6c8a9ada6"
TRAVEL_TIMES_WALK_BLAKE2B = "a4227c5dcd2ad7275b6bd240a8cdd9fecdedb0677e6b9b0232fd7af48695741a6667c47ff2cf27add7b17139976e235c569e72efe65d5e363b8b5f37e4bdd0fe"
TRAVEL_TIMES_WALK_BLAKE2S = "fa48e033de6894948c23405134fe4a1c708ce2aa126f68f9b45e3bec0fd4b99d"


@pytest.fixture
def file_digest_test_file_as_pathlib_path():
    """Return the path of a test file as a pathlib.Path."""
    yield TRAVEL_TIMES_WALK


@pytest.fixture
def file_digest_test_file_as_str(file_digest_test_file_as_pathlib_path):
    """Return the path of a test file as a str."""
    yield f"{file_digest_test_file_as_pathlib_path}"


@pytest.fixture()
def file_digest_sha256():
    """Return the expected SHA256 hash for the test file."""
    yield TRAVEL_TIMES_WALK_SHA256


@pytest.fixture()
def file_digest_blake2b():
    """Return the expected BLAKE2B hash for the test file."""
    yield TRAVEL_TIMES_WALK_BLAKE2B


@pytest.fixture()
def file_digest_blake2s():
    """Return the expected BLAKE2S hash for the test file."""
    yield TRAVEL_TIMES_WALK_BLAKE2S
