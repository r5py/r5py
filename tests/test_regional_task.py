#!/usr/bin/env python3


import pytest  # noqa: F401

import r5py
from r5py.util import start_jvm

import com.conveyal.r5


start_jvm()


class TestRegionalTask:
    @pytest.mark.parametrize(
        ["regional_task", "access_modes", "expected"],
        [
            (pytest.lazy_fixture("blank_regional_task"), [], set([])),
            (
                pytest.lazy_fixture("blank_regional_task"),
                [r5py.LegMode.WALK],
                set([r5py.LegMode.WALK]),
            ),
        ],
    )
    def test_access_mode_setter(self, regional_task, access_modes, expected):
        regional_task.access_modes = access_modes
        assert regional_task.access_modes == expected
        assert regional_task._regional_task.accessModes == r5py.RegionalTask._enum_set(
            expected, com.conveyal.r5.api.util.LegMode
        )

    @pytest.mark.parametrize(
        ["regional_task", "percentiles"],
        [
            (pytest.lazy_fixture("blank_regional_task"), []),
            (pytest.lazy_fixture("blank_regional_task"), [50]),
            (pytest.lazy_fixture("blank_regional_task"), [33, 66]),
            (pytest.lazy_fixture("blank_regional_task"), [25, 50, 75]),
            (pytest.lazy_fixture("blank_regional_task"), [20, 40, 60, 80]),
            (pytest.lazy_fixture("blank_regional_task"), [16, 33, 50, 66, 83]),
        ],
    )
    def test_allowed_number_of_percentiles(self, regional_task, percentiles):
        regional_task.percentiles = percentiles

    @pytest.mark.parametrize(
        ["regional_task", "percentiles"],
        [
            (
                pytest.lazy_fixture("blank_regional_task"),
                [10, 20, 30, 40, 50, 60, 70, 90],
            ),
            (
                pytest.lazy_fixture("blank_regional_task"),
                [i for i in range(101)],
            ),
        ],
    )
    def test_out_of_range_percentiles(self, regional_task, percentiles):
        with pytest.raises(
            ValueError, match="Maximum number of percentiles allowed is 5"
        ):
            regional_task.percentiles = percentiles

    # TODO: all other methods and attributes!
