#!/usr/bin/env python3


import hashlib

import pytest

from r5py.util.validating_requests_session import (
    ChecksumFailed,
    ValidatingRequestsSession,
)


class TestValidatingRequestSession:
    def test_initialisation(self):
        validating_request_session = ValidatingRequestsSession()
        assert validating_request_session._algorithm == hashlib.sha256

    def test_get(self, r5_jar_url, r5_jar_sha256):
        with (
            ValidatingRequestsSession() as session,
            session.get(r5_jar_url, r5_jar_sha256) as response,
        ):
            assert response.content

    def test_get_invalid_checksum(self, r5_jar_url, r5_jar_sha256_invalid):
        with pytest.raises(ChecksumFailed):
            with (
                ValidatingRequestsSession() as session,
                session.get(r5_jar_url, r5_jar_sha256_invalid) as response,
            ):
                assert response.content

    def test_post(self, r5_jar_url, r5_jar_sha256_github_error_message_when_posting):
        with (
            ValidatingRequestsSession() as session,
            session.post(
                r5_jar_url, r5_jar_sha256_github_error_message_when_posting
            ) as response,
        ):
            assert response.content

    def test_post_invalid_checksum(self, r5_jar_url, r5_jar_sha256_invalid):
        with pytest.raises(ChecksumFailed):
            with (
                ValidatingRequestsSession() as session,
                session.post(r5_jar_url, r5_jar_sha256_invalid) as response,
            ):
                assert response.content
