#!/usr/bin/env python3

"""R5py-specific exceptions."""


import requests


# base class for r5py-related exceptions
class R5pyError(Exception):
    """Generic base exception for r5py errors."""


# more specific exceptions
class GtfsFileError(R5pyError):
    """GTFS file contained errors."""


class ChecksumFailed(requests.RequestException, R5pyError):
    """Requested resource did not pass checksum test."""


class MissingColumnError(ValueError, R5pyError):
    """An input data set is missing a required column."""


class NoCrsError(ValueError, R5pyError):
    """An input data set’s geometry column does not have a reference system defined."""


class NonUniqueIDError(ValueError, R5pyError):
    """An input data set’s `id` column has non-unique values."""


class NoIDColumnError(MissingColumnError):
    """An input data set does not have a required `id` column."""


class UnexpectedClasspathSchema(ValueError, R5pyError):
    """A classpath was supplied as an URI, but could not be parsed."""


class UnexpectedCrsError(ValueError, R5pyError):
    """A geometry is in an unexpected reference system."""
