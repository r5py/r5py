#!/usr/bin/env python3


import pytest  # noqa: F401

from r5py.util.memory_footprint import (
    _get_max_memory,
    _share_of_ram,
    _parse_max_memory_string,
)
import psutil


class TestMemoryFootprint:
    @pytest.mark.parametrize(
        ["memory_input", "expected"],
        [
            ("5G", (5, "G")),
            ("1000M", (1000, "M")),
            ("1T", (1, "T")),
            ("1073741824K", (1073741824, "K")),
            ("1073741824", (1073741824, None)),
        ],
    )
    def test_parse_max_memory_string(self, memory_input, expected):
        assert _parse_max_memory_string(memory_input) == expected

    def test_incorrect_memory_input(self):
        # Totally incorrect input
        value = "incorrect_value"
        with pytest.raises(
            ValueError, match=f"Could not interpret --max-memory: {value}"
        ):
            _parse_max_memory_string(value)
        # Incorrect suffix
        value = "1000J"
        with pytest.raises(ValueError) as e:
            _parse_max_memory_string(value)
            assert "Could not interprect --max-memory" in str(e)

    @pytest.mark.parametrize(
        ["memory_input", "expected"],
        [
            ("5G", 5 * 1024),
            ("1000M", 1024),
            ("1T", 1024 * 1024),
            ("1048576K", 1024),
            ("1073741824", 1024),
        ],
    )
    def test_max_memory(self, memory_input, expected):
        assert _get_max_memory(memory_input) == expected

    def test_lower_than_allowed_memory_input(self):
        value = "1"
        with pytest.warns(
            RuntimeWarning, match="Requested maximum JVM heap size is too low for R5"
        ):
            assert _get_max_memory(value) == 200

    @pytest.mark.parametrize(
        ["share", "leave_at_least", "expected"],
        [
            (0.8, 2000, [round(0.8 * (psutil.virtual_memory().total / (2**20)))]),
            (0.8, 10000, [round(psutil.virtual_memory().total / (2**20) - 10000)]),
            (0.1, 1000000, [round(psutil.virtual_memory().total / (2**20) - 1000000)])
            # todo in the future this should return 0
        ],
    )
    def test_share_or_ram(self, share, leave_at_least, expected):
        assert round(_share_of_ram(share, leave_at_least), 0) in expected
