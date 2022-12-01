#!/usr/bin/env python3


import pytest  # noqa: F401

import datetime
import shapely.geometry

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
        ["regional_task", "max_time_cycling", "expected", "expected_java"],
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
    def test_max_time_cycling_setter(
        self, regional_task, max_time_cycling, expected, expected_java
    ):
        regional_task.max_time_cycling = max_time_cycling
        assert regional_task.max_time_cycling == expected
        assert regional_task._regional_task.maxBikeTime == expected_java

    @pytest.mark.parametrize(
        ["regional_task", "max_time_driving", "expected", "expected_java"],
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
    def test_max_time_driving_setter(
        self, regional_task, max_time_driving, expected, expected_java
    ):
        regional_task.max_time_driving = max_time_driving
        assert regional_task.max_time_driving == expected
        assert regional_task._regional_task.maxCarTime == expected_java

    @pytest.mark.parametrize(
        ["regional_task", "max_time_walking", "expected", "expected_java"],
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
    def test_max_time_walking_setter(
        self, regional_task, max_time_walking, expected, expected_java
    ):
        regional_task.max_time_walking = max_time_walking
        assert regional_task.max_time_walking == expected
        assert regional_task._regional_task.maxWalkTime == expected_java

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

    @pytest.mark.parametrize(
        ["regional_task"], [(pytest.lazy_fixture("blank_regional_task"),)]
    )
    def test_scenario(self, regional_task):
        from r5py.r5 import Scenario

        scenario = Scenario()
        regional_task.scenario = scenario
        assert regional_task.scenario == scenario
        assert regional_task._regional_task.scenarioId == scenario.id

    @pytest.mark.parametrize(
        ["regional_task", "speed_cycling", "expected", "expected_java"],
        [
            (pytest.lazy_fixture("blank_regional_task"), 14.4, 14.4, 4.0),
            (pytest.lazy_fixture("blank_regional_task"), 18, 18.0, 5.0),
            (pytest.lazy_fixture("blank_regional_task"), 19.8, 19.8, 5.5),
            (pytest.lazy_fixture("blank_regional_task"), 28.8, 28.8, 8.0),
            (pytest.lazy_fixture("blank_regional_task"), 36, 36, 10.0),
        ],
    )
    def test_speed_cycling_setter(
        self, regional_task, speed_cycling, expected, expected_java
    ):
        regional_task.speed_cycling = speed_cycling
        assert regional_task.speed_cycling == expected
        assert regional_task._regional_task.bikeSpeed == pytest.approx(expected_java)

    @pytest.mark.parametrize(
        ["regional_task", "speed_walking", "expected", "expected_java"],
        [
            (pytest.lazy_fixture("blank_regional_task"), 3.6, 3.6, 1.0),
            (pytest.lazy_fixture("blank_regional_task"), 5.4, 5.4, 1.5),
            (pytest.lazy_fixture("blank_regional_task"), 7.2, 7.2, 2.0),
            (pytest.lazy_fixture("blank_regional_task"), 9.0, 9.0, 2.5),
        ],
    )
    def test_speed_walking_setter(
        self, regional_task, speed_walking, expected, expected_java
    ):
        regional_task.speed_walking = speed_walking
        assert regional_task.speed_walking == expected
        assert regional_task._regional_task.walkSpeed == pytest.approx(expected_java)

    @pytest.mark.parametrize(
        ["regional_task", "breakdown"],
        [
            (pytest.lazy_fixture("blank_regional_task"), True),
            (pytest.lazy_fixture("blank_regional_task"), False),
        ],
    )
    def test_breakdown_setter_getter(self, regional_task, breakdown):
        regional_task.breakdown = breakdown
        assert regional_task.breakdown == breakdown

    @pytest.mark.parametrize(
        ["regional_task", "origin"],
        [
            (
                pytest.lazy_fixture("blank_regional_task"),
                shapely.geometry.Point(60, 24),
            ),
            (
                pytest.lazy_fixture("blank_regional_task"),
                shapely.geometry.Point(61, 25),
            ),
        ],
    )
    def test_origin_setter_getter(self, regional_task, origin):
        regional_task.origin = origin
        assert regional_task.origin == origin

    # TODO: all other methods and attributes!
