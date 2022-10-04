#!/usr/bin/env python3


import pytest  # noqa: F401

import datetime

import r5py
from r5py.util import start_jvm

import com.conveyal.r5
import java.time


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
            (
                pytest.lazy_fixture("blank_regional_task"),
                [r5py.LegMode.BICYCLE],
                set([r5py.LegMode.BICYCLE]),
            ),
            (
                pytest.lazy_fixture("blank_regional_task"),
                [r5py.LegMode.CAR],
                set([r5py.LegMode.CAR]),
            ),
            (
                pytest.lazy_fixture("blank_regional_task"),
                [r5py.LegMode.WALK, r5py.LegMode.BICYCLE],
                set([r5py.LegMode.WALK, r5py.LegMode.BICYCLE]),
            ),
            (
                pytest.lazy_fixture("blank_regional_task"),
                [r5py.LegMode.WALK, r5py.LegMode.BICYCLE, r5py.LegMode.CAR],
                set([r5py.LegMode.WALK, r5py.LegMode.BICYCLE, r5py.LegMode.CAR]),
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
        [
            "regional_task",
            "departure",
            "expected",
            "expected_java_date",
            "expected_java_from_time",
        ],
        [
            (
                pytest.lazy_fixture("blank_regional_task"),
                datetime.datetime(2022, 2, 22, 8, 30),
                datetime.datetime(2022, 2, 22, 8, 30),
                java.time.LocalDate.of(2022, 2, 22),
                30600,
            )
        ],
    )
    def test_departure_setter(
        self,
        regional_task,
        departure,
        expected,
        expected_java_date,
        expected_java_from_time,
    ):
        regional_task.departure = departure
        assert regional_task.departure == expected
        assert regional_task._regional_task.date == expected_java_date
        assert regional_task._regional_task.fromTime == expected_java_from_time

    @pytest.mark.parametrize(
        ["regional_task", "bicycle_stress", "expected"],
        [
            (pytest.lazy_fixture("blank_regional_task"), 1, 1),
            (pytest.lazy_fixture("blank_regional_task"), 2, 2),
            (pytest.lazy_fixture("blank_regional_task"), 3, 3),
            (pytest.lazy_fixture("blank_regional_task"), 4, 4),
        ],
    )
    def test_max_bicycle_traffic_stress_setter(
        self, regional_task, bicycle_stress, expected
    ):
        regional_task.max_bicycle_traffic_stress = bicycle_stress
        assert regional_task.max_bicycle_traffic_stress == expected
        assert regional_task._regional_task.bikeTrafficStress == expected

    @pytest.mark.parametrize(
        ["regional_task", "max_pt_rides", "expected"],
        [
            (pytest.lazy_fixture("blank_regional_task"), 1, 1),
            (pytest.lazy_fixture("blank_regional_task"), 1232, 1232),
            (pytest.lazy_fixture("blank_regional_task"), 31, 31),
            (pytest.lazy_fixture("blank_regional_task"), 999, 999),
        ],
    )
    def test_max_public_transport_rides_setter(
        self, regional_task, max_pt_rides, expected
    ):
        regional_task.max_public_transport_rides = max_pt_rides
        assert regional_task.max_public_transport_rides == expected
        assert regional_task._regional_task.maxRides == expected

    @pytest.mark.parametrize(
        ["regional_task", "max_time", "expected", "expected_java"],
        [
            (
                pytest.lazy_fixture("blank_regional_task"),
                datetime.timedelta(hours=1),
                datetime.timedelta(hours=1),
                60,
            ),
            (
                pytest.lazy_fixture("blank_regional_task"),
                datetime.timedelta(minutes=15),
                datetime.timedelta(minutes=15),
                15,
            ),
            (
                pytest.lazy_fixture("blank_regional_task"),
                datetime.timedelta(hours=7, minutes=23),
                datetime.timedelta(hours=7, minutes=23),
                443,
            ),
        ],
    )
    def test_max_time_setter(self, regional_task, max_time, expected, expected_java):
        regional_task.max_time = max_time
        assert regional_task.max_time == expected
        assert regional_task._regional_task.streetTime == expected_java
        assert regional_task._regional_task.maxTripDurationMinutes == expected_java
        assert regional_task._regional_task.maxCarTime == expected_java

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
