#!/usr/bin/env python3


"""Fixtures related to the R5 classpath."""

import pathlib

import pytest

R5_JAR_URL = (
    "https://github.com/r5py/r5/releases/download/v7.5.1-r5py/r5-v7.5.1-r5py-all.jar"
)
R5_JAR_SHA256 = "d50be106cadd7b636cfc0e209052767d7df570629f79fdf98ecd5cf5d2d89be7"
R5_JAR_SHA256_INVALID = "adfadsfadsfadsfasdfasdf"
R5_JAR_SHA256_GITHUB_ERROR_MESSAGE_WHEN_POSTING = (
    "b59e00f33be883c77f90849a5abd589a74bc3076668607fe453c9b48000f4fa9"
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
