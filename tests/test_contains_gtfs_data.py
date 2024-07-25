#!/usr/bin/env python3


import pytest
import pytest_lazy_fixtures

import r5py


class TestContainsGtfsData:
    @pytest.mark.parametrize(
        ["path", "expected"],
        [
            (pytest_lazy_fixtures.lf("gtfs_file_path"), True),
            (pytest_lazy_fixtures.lf("not_a_gtfs_file"), False),
        ],
    )
    def test_contains_gtfs_data(self, path, expected):
        assert r5py.util.contains_gtfs_data(path) == expected
        assert r5py.util.contains_gtfs_data(str(path)) == expected
        with open(path, "rb") as f:
            r5py.util.contains_gtfs_data(f)
