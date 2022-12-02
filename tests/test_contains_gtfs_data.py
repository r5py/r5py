#!/usr/bin/env python3


import pytest

import r5py


class TestContainsGtfsData:
    @pytest.mark.parametrize(
        ["path", "expected"],
        [
            (pytest.lazy_fixture("gtfs_file_path"), True),
            (pytest.lazy_fixture("osm_pbf_file_path"), False),
        ],
    )
    def test_contains_gtfs_data_path(self, path, expected):
        assert r5py.util.contains_gtfs_data(path) == expected

    @pytest.mark.parametrize(
        ["path", "expected"],
        [
            (pytest.lazy_fixture("gtfs_file_path"), True),
            (pytest.lazy_fixture("osm_pbf_file_path"), False),
        ],
    )
    def test_contains_gtfs_data_str(self, path, expected):
        assert r5py.util.contains_gtfs_data(str(path)) == expected

    @pytest.mark.parametrize(
        ["path", "expected"],
        [
            (pytest.lazy_fixture("gtfs_file_path"), True),
            (pytest.lazy_fixture("osm_pbf_file_path"), False),
        ],
    )
    def test_contains_gtfs_data_filehandle(self, path, expected):
        assert r5py.util.contains_gtfs_data(open(path, "rb")) == expected
