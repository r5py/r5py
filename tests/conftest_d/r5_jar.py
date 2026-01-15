#!/usr/bin/env python3


"""Fixtures related to the R5 classpath."""


import pathlib

import pytest


R5_JAR_URL = (
    "https://github.com/r5py/r5/releases/download/v7.4-r5py/r5-v7.4-r5py-all.jar"
)
R5_JAR_SHA256 = "c51b566671165d113add84e10e60fb9273014ca4a2e2a52591446954f68e7340"
R5_JAR_SHA256_INVALID = "adfadsfadsfadsfasdfasdf"
R5_JAR_SHA256_GITHUB_ERROR_MESSAGE_WHEN_POSTING = (
    "1e0a6adb25d2cc8cf1fe7170ef0ce6206e7a0cb7fc98a9a13af26df74afaa08b"
)


@pytest.fixture(scope="session")
def r5_jar_cached():
    """Return a cache path for the R5 jar."""
    from r5py.util.config import Config

    yield str(Config().CACHE_DIR / pathlib.Path(R5_JAR_URL).name)


@pytest.fixture
def r5_jar_cached_invalid():
    """Return an invalid cache path for the R5 jar."""
    yield "/definitely/invalid/path/to/r5.jar"


@pytest.fixture
def r5_jar_sha256():
    """Return the SHA256 hash for the R5 jar."""
    yield R5_JAR_SHA256


@pytest.fixture
def r5_jar_sha256_invalid():
    """Return an invalid SHA256 hash for the R5 jar."""
    yield R5_JAR_SHA256_INVALID


@pytest.fixture
def r5_jar_sha256_github_error_message_when_posting():
    """Return the SHA256 hash of the GitHub error message when accidently POSTing."""
    yield R5_JAR_SHA256_GITHUB_ERROR_MESSAGE_WHEN_POSTING


@pytest.fixture()
def r5_jar_url():
    """Return the URL of the R5 jar."""
    yield R5_JAR_URL
