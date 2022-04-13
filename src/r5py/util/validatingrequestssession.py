#!/usr/bin/env python

"""Extends requests.Session to enable simple checksum testing."""

__all__ = ["ValidatingRequestsSession"]

import hashlib

import requests


class ChecksumFailed(requests.RequestException):
    """Requested resource did not pass checksum test."""


class ValidatingRequestsSession(requests.Session):
    """Download a file and test whether it matches a checksum."""

    def __init__(
            self,
            *args,
            checksum_algorithm=hashlib.sha256,
            **kwargs
    ):
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
        super().__init__(*args, checksum_algorithm=hashlib.sha256, **kwargs)
        self._algorithm = checksum_algorithm

    def request(self, method, url, checksum, *args, **kwargs):
        """
        Retrieve file from cache or proxy requests.request.

        Raise `ChecksumFailed` if the file’s digest and `checksum` differ.
        """
        response = super().request(method, url, *args, **kwargs)
        digest = self._algorithm(response.content)

        if digest != checksum:
            raise ChecksumFailed("Checksum failed for {}.".format(url))

        return response
