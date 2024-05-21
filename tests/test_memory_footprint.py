#!/usr/bin/env python3


import pytest

from r5py.util.memory_footprint import (
    _get_max_memory,
    _interpret_power_of_two_units,
    _parse_value_and_unit,
    _share_of_ram,
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
    def test_parse_value_and_unit(self, memory_input, expected):
        assert _parse_value_and_unit(memory_input) == expected

    def test_incorrect_memory_input(self):
        # Totally incorrect input
        value = "incorrect_value"
        with pytest.raises(ValueError, match="Could not interpret .*"):
            _get_max_memory(value)

        # Incorrect suffix
        value = "1000J"
        with pytest.raises(ValueError, match="Could not interpret unit .*"):
            _get_max_memory(value)

    @pytest.mark.parametrize(
        ["value", "unit", "expected"],
        [
            (5, "G", 5368709120),
            (1.5, "G", 1610612736),
            (1000, "M", 1048576000),
            (1, "T", 1099511627776),
            (1048576, "K", 1073741824),
            (1073741824, None, 1073741824),
        ],
    )
    def test_interpret_power_of_two_units(self, value, unit, expected):
        assert _interpret_power_of_two_units(value, unit) == expected

    def test_lower_than_allowed_memory_input(self):
        value = "1"
        with pytest.warns(
            RuntimeWarning, match="Requested maximum JVM heap size is too low for R5"
        ):
            assert _get_max_memory(value) == 209715200

    @pytest.mark.parametrize(
        ["share", "leave_at_least", "expected"],
        [
            (0.8, 0, psutil.virtual_memory().total * 0.8),
            (0.1, 0, psutil.virtual_memory().total * 0.1),
            (1.0, 2000, psutil.virtual_memory().total - 2000),
        ],
    )
    def test_share_of_ram_leaving_zero(self, share, leave_at_least, expected):
        # NOTE: this can never match exactly, as memory is consumed
        # in the computation of the share, and most likely
        # by other processes running at the same time.

        # Let’s try to see whether we get to within 100MiB
        assert _share_of_ram(share, leave_at_least) == pytest.approx(
            expected, 100 * 1024**2
        )

    # There remain two tricky cases untested:
    #    - share_of_ram() with leave_at_least > 0:
    #      very tricky to test without reproducing the to-be-tested
    #      code 1:1, dynamically depending on available RAM
    #    - share_of_ram() with a leave_at_least > (total - share).
    #      Even more complicated ;)
