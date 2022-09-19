#!/usr/bin/env python3

"""R5py-specific exceptions."""


import requests


class R5pyError(Exception):
    """Generic base exception for r5py errors."""


class ChecksumFailed(requests.RequestException, R5pyError):
    """Requested resource did not pass checksum test."""


class NonUniqueIDError(ValueError, R5pyError):
    """An input data set’s `id` column has non-unique values."""


class MissingColumnError(ValueError, R5pyError):
    """An input data set is missing a required column."""


class NoIDColumnError(MissingColumnError):
    """An input data set does not have a required `id` column."""
