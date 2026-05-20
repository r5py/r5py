#!/usr/bin/env python

"""Extends requests.Session to enable simple checksum testing."""

__all__ = ["ValidatingRequestsSession"]

import hashlib

import requests

from .exceptions import ChecksumFailed


class ValidatingRequestsSession(requests.Session):
    """Download a file and test whether it matches a checksum."""

    def __init__(self, *args, checksum_algorithm=hashlib.sha256, **kwargs):
        """
        Download a file and test whether it matches a checksum.

        Arguments
        ---------
        checksum_algorithm : function
            algorithm to use to create checksum of downloaded file,
            default: hashlib.sha256
        *args, **kwargs
            any argument accepted by `requests.Session`
        """
        super().__init__(*args, **kwargs)
        self._algorithm = checksum_algorithm

    def get(self, *args, checksum=None, **kwargs):
        """Send a GET request, tests checksum."""
        kwargs.setdefault("allow_redirects", True)
        return self.request("GET", *args, checksum=checksum, **kwargs)

    def post(self, *args, checksum=None, **kwargs):
        """Send a POST request, tests checksum."""
        return self.request("POST", *args, checksum=checksum, **kwargs)

    # delete, put, head don’t return data,
    # testing checksums does not apply

    def request(self, *args, checksum=None, **kwargs):
        """
        Retrieve file from cache or proxy requests.request.

        Raise `ChecksumFailed` if the file’s digest and `checksum` differ.
        """
        response = super().request(*args, **kwargs)
        digest = self._algorithm(response.content).hexdigest()

        if digest != checksum:
            raise ChecksumFailed(
                f"Checksum failed for {args[1]}, expected {checksum}, got {digest}"
            )

        return response
