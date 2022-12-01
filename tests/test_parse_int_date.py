#!/usr/bin/env python3


import datetime

import pytest

import r5py.util


class TestParseIntDate:
    @pytest.mark.parametrize(
        ["int_date", "expected"],
        [
            (20220202, datetime.datetime(2022, 2, 2)),
            (19990202, datetime.datetime(1999, 2, 2)),
            (20191231, datetime.datetime(2019, 12, 31)),
        ],
    )
    def test_parse_int_date(self, int_date, expected):
        assert r5py.util.parse_int_date(int_date) == expected
