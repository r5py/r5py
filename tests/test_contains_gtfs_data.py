#!/usr/bin/env python3


import pathlib

import pytest  # noqa: F401

import r5py

DATA_DIRECTORY = pathlib.Path(__file__).absolute().parents[1] / "docs/data"
GTFS_FILE = DATA_DIRECTORY / "GTFS.zip"
NOT_GTFS_FILE = DATA_DIRECTORY / "kantakaupunki.osm.pbf"


class TestContainsGtfsData:
    @pytest.mark.parametrize(
        ["path", "expected"],
        [
            (GTFS_FILE, True),
            (str(GTFS_FILE), True),
            (open(GTFS_FILE, "rb"), True),
            (NOT_GTFS_FILE, False),
            (str(NOT_GTFS_FILE), False),
            (open(NOT_GTFS_FILE, "rb"), False),
        ],
    )
    def test_contains_gtfs_data(self, path, expected):
        assert r5py.util.contains_gtfs_data(path) == expected
