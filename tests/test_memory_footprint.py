#!/usr/bin/env python3


import pytest  # noqa: F401

from r5py.util.memory_footprint import max_memory, share_of_ram
import psutil


class TestMemoryFootprint:
    @pytest.mark.parametrize(
        ["memory_input", "expected"],
        [
            ("5G", 5*1024),
            ("1000M", 1000),
            ("1T", 1024*1024)
        ],
    )
    def test_max_memory(self, memory_input, expected):
        assert max_memory(memory_input) == expected

    def test_incorrect_memory_input(self):
        value = "incorrect_value"
        with pytest.raises(ValueError, match=f"Could not interpret --max-memory: {value}"):
            max_memory(value)

    def test_lower_than_allowed_memory_input(self):
        value = "100M"
        with pytest.warns(RuntimeWarning, match=f"Requested maximum JVM heap size is too low for R5"):
            assert max_memory(value) == 200

    @pytest.mark.parametrize(
        ["share", "leave_at_least", "expected"],
        [
            (0.8, 2000, 0.8 * psutil.virtual_memory().total / (2**20)),
            (0.8, 10000, psutil.virtual_memory().total / (2**20) - 10000),
            (0.1, 1000000, psutil.virtual_memory().total / (2 ** 20) - 1000000) # todo in the future this should return 0
        ]
    )
    def test_share_or_ram(self, share, leave_at_least, expected):
        assert round(share_of_ram(share, leave_at_least), 0) == round(expected, 0)

