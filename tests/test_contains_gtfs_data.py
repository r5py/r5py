#!/usr/bin/env python3


import pytest  # noqa: F401

import r5py


class TestContainsGtfsData:
    @pytest.mark.parametrize(
        ["path", "expected"],
        [
            (pytest.lazy_fixture("gtfs_file"), True),
            (pytest.lazy_fixture("not_a_gtfs_file"), False),
        ],
    )
    def test_contains_gtfs_data(self, path, expected):
        assert r5py.util.contains_gtfs_data(path) == expected
        assert r5py.util.contains_gtfs_data(str(path)) == expected
        with open(path, "rb") as f:
            r5py.util.contains_gtfs_data(f)
