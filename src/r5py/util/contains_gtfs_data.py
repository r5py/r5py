#!/usr/bin/env python3

"""Check whether a file contains a GTFS data set."""


import zipfile


__all__ = ["contains_gtfs_data"]


# https://developers.google.com/transit/gtfs/reference#field_definitions
GTFS_REQUIRED_FILES = (
    "agency.txt",
    "stops.txt",
    "routes.txt",
    "trips.txt",
    "stop_times.txt",
)


def contains_gtfs_data(path):
    """
    Check whether the file in `path` contains a GTFS dataset.

    This is a rather heuristic approach: it tries to open the file
    as a ZIP archive, and confirm the presence of the files required
    by the GTFS standard reference.

    Arguments:
    ----------
    path : str | pathlib.Path | file-like
        The file to check. Should be opened in binary mode, if passed as a
        file-like object.

    Returns:
    --------
    bool : `True` if `path` likely contains a GTFS dataset, `False` if not.
    """
    try:
        archive = zipfile.ZipFile(path)
        assert all(
            gtfs_field in archive.namelist() for gtfs_field in GTFS_REQUIRED_FILES
        )
        contains_gtfs_data = True
    except (AssertionError, FileNotFoundError, zipfile.BadZipFile):
        contains_gtfs_data = False
    return contains_gtfs_data
