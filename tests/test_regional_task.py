#!/usr/bin/env python3


import pytest

import datetime
import geopandas
import pytest_lazy_fixtures
import shapely.geometry

import r5py
from r5py.util import start_jvm

import com.conveyal.r5
import java.time


start_jvm()


class TestRegionalTask:
    @pytest.mark.parametrize(
        ["access_modes", "expected"],
        [
            (
                [r5py.TransportMode.WALK],
                set([r5py.TransportMode.WALK]),
            ),
            (
                [r5py.TransportMode.BICYCLE],
                set([r5py.TransportMode.BICYCLE]),
            ),
            (
                [r5py.TransportMode.CAR],
                set([r5py.TransportMode.CAR]),
            ),
            (
                [r5py.TransportMode.WALK, r5py.TransportMode.BICYCLE],
                set([r5py.TransportMode.WALK, r5py.TransportMode.BICYCLE]),
            ),
            (
                [
                    r5py.TransportMode.WALK,
                    r5py.TransportMode.BICYCLE,
                    r5py.TransportMode.CAR,
                ],
                set(
                    [
                        r5py.TransportMode.WALK,
                        r5py.TransportMode.BICYCLE,
                        r5py.TransportMode.CAR,
                    ]
                ),
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
        ["access_modes", "expected"],
        [
            (
                ["WALK"],
                set([r5py.TransportMode.WALK]),
            ),
            (
                ["BICYCLE"],
                set([r5py.TransportMode.BICYCLE]),
            ),
            (
                ["CAR"],
                set([r5py.TransportMode.CAR]),
            ),
            (
                ["WALK", "BICYCLE"],
                set([r5py.TransportMode.WALK, r5py.TransportMode.BICYCLE]),
            ),
            (
                ["WALK", "BICYCLE", "CAR"],
                set(
                    [
                        r5py.TransportMode.WALK,
                        r5py.TransportMode.BICYCLE,
                        r5py.TransportMode.CAR,
                    ]
                ),
            ),
        ],
    )
    def test_access_mode_setter_with_strings(
        self, regional_task, access_modes, expected
    ):
        regional_task.access_modes = access_modes
        assert regional_task.access_modes == expected
        assert regional_task._regional_task.accessModes == r5py.RegionalTask._enum_set(
            expected, com.conveyal.r5.api.util.LegMode
        )

    @pytest.mark.parametrize(
        [
            "departure",
            "expected",
            "expected_java_date",
            "expected_java_from_time",
        ],
        [
            (
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
        ["egress_modes", "expected"],
        [
            (
                [r5py.TransportMode.WALK],
                set([r5py.TransportMode.WALK]),
            ),
            (
                [r5py.TransportMode.BICYCLE],
                set([r5py.TransportMode.BICYCLE]),
            ),
            (
                [r5py.TransportMode.CAR],
                set([r5py.TransportMode.CAR]),
            ),
            (
                [r5py.TransportMode.WALK, r5py.TransportMode.BICYCLE],
                set([r5py.TransportMode.WALK, r5py.TransportMode.BICYCLE]),
            ),
            (
                [
                    r5py.TransportMode.WALK,
                    r5py.TransportMode.BICYCLE,
                    r5py.TransportMode.CAR,
                ],
                set(
                    [
                        r5py.TransportMode.WALK,
                        r5py.TransportMode.BICYCLE,
                        r5py.TransportMode.CAR,
                    ]
                ),
            ),
        ],
    )
    def test_egress_mode_setter(self, regional_task, egress_modes, expected):
        regional_task.egress_modes = egress_modes
        assert regional_task.egress_modes == expected
        assert regional_task._regional_task.egressModes == r5py.RegionalTask._enum_set(
            expected, com.conveyal.r5.api.util.LegMode
        )

    @pytest.mark.parametrize(
        ["egress_modes", "expected"],
        [
            (
                ["WALK"],
                set([r5py.TransportMode.WALK]),
            ),
            (
                ["BICYCLE"],
                set([r5py.TransportMode.BICYCLE]),
            ),
            (
                ["CAR"],
                set([r5py.TransportMode.CAR]),
            ),
            (
                ["WALK", "BICYCLE"],
                set([r5py.TransportMode.WALK, r5py.TransportMode.BICYCLE]),
            ),
            (
                ["WALK", "BICYCLE", "CAR"],
                set(
                    [
                        r5py.TransportMode.WALK,
                        r5py.TransportMode.BICYCLE,
                        r5py.TransportMode.CAR,
                    ]
                ),
            ),
        ],
    )
    def test_egress_mode_setter_with_strings(
        self, regional_task, egress_modes, expected
    ):
        regional_task.egress_modes = egress_modes
        assert regional_task.egress_modes == expected
        assert regional_task._regional_task.egressModes == r5py.RegionalTask._enum_set(
            expected, com.conveyal.r5.api.util.LegMode
        )

    @pytest.mark.parametrize(
        ["bicycle_stress", "expected"],
        [
            (1, 1),
            (2, 2),
            (3, 3),
            (4, 4),
        ],
    )
    def test_max_bicycle_traffic_stress_setter(
        self,
        regional_task,
        bicycle_stress,
        expected,
    ):
        regional_task.max_bicycle_traffic_stress = bicycle_stress
        assert regional_task.max_bicycle_traffic_stress == expected
        assert regional_task._regional_task.bikeTrafficStress == expected

    @pytest.mark.parametrize(
        ["max_pt_rides", "expected"],
        [
            (1, 1),
            (1232, 1232),
            (31, 31),
            (999, 999),
        ],
    )
    def test_max_public_transport_rides_setter(
        self,
        regional_task,
        max_pt_rides,
        expected,
    ):
        regional_task.max_public_transport_rides = max_pt_rides
        assert regional_task.max_public_transport_rides == expected
        assert regional_task._regional_task.maxRides == expected

    @pytest.mark.parametrize(
        ["max_time", "expected", "expected_java"],
        [
            (
                datetime.timedelta(hours=1),
                datetime.timedelta(hours=1),
                60,
            ),
            (
                datetime.timedelta(minutes=15),
                datetime.timedelta(minutes=15),
                15,
            ),
            (
                datetime.timedelta(hours=7, minutes=23),
                datetime.timedelta(hours=7, minutes=23),
                443,
            ),
        ],
    )
    def test_max_time_setter(
        self,
        regional_task,
        max_time,
        expected,
        expected_java,
    ):
        regional_task.max_time = max_time
        assert regional_task.max_time == expected
        assert regional_task._regional_task.streetTime == expected_java
        assert regional_task._regional_task.maxTripDurationMinutes == expected_java
        assert regional_task._regional_task.maxCarTime == expected_java

    @pytest.mark.parametrize(
        ["max_time_cycling", "expected", "expected_java"],
        [
            (
                datetime.timedelta(hours=1),
                datetime.timedelta(hours=1),
                60,
            ),
            (
                datetime.timedelta(minutes=15),
                datetime.timedelta(minutes=15),
                15,
            ),
            (
                datetime.timedelta(hours=7, minutes=23),
                datetime.timedelta(hours=7, minutes=23),
                443,
            ),
        ],
    )
    def test_max_time_cycling_setter(
        self,
        regional_task,
        max_time_cycling,
        expected,
        expected_java,
    ):
        regional_task.max_time_cycling = max_time_cycling
        assert regional_task.max_time_cycling == expected
        assert regional_task._regional_task.maxBikeTime == expected_java

    @pytest.mark.parametrize(
        ["max_time_driving", "expected", "expected_java"],
        [
            (
                datetime.timedelta(hours=1),
                datetime.timedelta(hours=1),
                60,
            ),
            (
                datetime.timedelta(minutes=15),
                datetime.timedelta(minutes=15),
                15,
            ),
            (
                datetime.timedelta(hours=7, minutes=23),
                datetime.timedelta(hours=7, minutes=23),
                443,
            ),
        ],
    )
    def test_max_time_driving_setter(
        self,
        regional_task,
        max_time_driving,
        expected,
        expected_java,
    ):
        regional_task.max_time_driving = max_time_driving
        assert regional_task.max_time_driving == expected
        assert regional_task._regional_task.maxCarTime == expected_java

    @pytest.mark.parametrize(
        ["max_time_walking", "expected", "expected_java"],
        [
            (
                datetime.timedelta(hours=1),
                datetime.timedelta(hours=1),
                60,
            ),
            (
                datetime.timedelta(minutes=15),
                datetime.timedelta(minutes=15),
                15,
            ),
            (
                datetime.timedelta(hours=7, minutes=23),
                datetime.timedelta(hours=7, minutes=23),
                443,
            ),
        ],
    )
    def test_max_time_walking_setter(
        self,
        regional_task,
        max_time_walking,
        expected,
        expected_java,
    ):
        regional_task.max_time_walking = max_time_walking
        assert regional_task.max_time_walking == expected
        assert regional_task._regional_task.maxWalkTime == expected_java

    @pytest.mark.parametrize(
        ["percentiles"],
        [
            ([],),
            ([50],),
            ([33, 66],),
            ([25, 50, 75],),
            ([20, 40, 60, 80],),
            ([16, 33, 50, 66, 83],),
        ],
    )
    def test_allowed_number_of_percentiles(self, regional_task, percentiles):
        regional_task.percentiles = percentiles

    @pytest.mark.parametrize(
        ["percentiles"],
        [
            ([10, 20, 30, 40, 50, 60, 70, 90],),
            ([i for i in range(101)],),
        ],
    )
    def test_out_of_range_percentiles(self, regional_task, percentiles):
        with pytest.raises(
            ValueError, match="Maximum number of percentiles allowed is 5"
        ):
            regional_task.percentiles = percentiles

    def test_scenario(self, regional_task):
        from r5py.r5 import Scenario

        scenario = Scenario()
        regional_task.scenario = scenario
        assert regional_task.scenario == scenario
        assert regional_task._regional_task.scenarioId == scenario.id

    @pytest.mark.parametrize(
        ["speed_cycling", "expected", "expected_java"],
        [
            (14.4, 14.4, 4.0),
            (18, 18.0, 5.0),
            (19.8, 19.8, 5.5),
            (28.8, 28.8, 8.0),
            (36, 36, 10.0),
        ],
    )
    def test_speed_cycling_setter(
        self,
        regional_task,
        speed_cycling,
        expected,
        expected_java,
    ):
        regional_task.speed_cycling = speed_cycling
        assert regional_task.speed_cycling == expected
        assert regional_task._regional_task.bikeSpeed == pytest.approx(expected_java)

    @pytest.mark.parametrize(
        ["speed_walking", "expected", "expected_java"],
        [
            (3.6, 3.6, 1.0),
            (5.4, 5.4, 1.5),
            (7.2, 7.2, 2.0),
            (9.0, 9.0, 2.5),
        ],
    )
    def test_speed_walking_setter(
        self,
        regional_task,
        speed_walking,
        expected,
        expected_java,
    ):
        regional_task.speed_walking = speed_walking
        assert regional_task.speed_walking == expected
        assert regional_task._regional_task.walkSpeed == pytest.approx(expected_java)

    @pytest.mark.parametrize(
        ["origin"],
        [
            (shapely.geometry.Point(60, 24),),
            (shapely.geometry.Point(61, 25),),
        ],
    )
    def test_origin_setter_getter(self, regional_task, origin):
        regional_task.origin = origin
        assert regional_task.origin == origin

    @pytest.mark.parametrize(
        ["destinations"],
        [
            (pytest_lazy_fixtures.lf("population_grid_points"),),
            (pytest_lazy_fixtures.lf("population_grid_points_first_three"),),
            (pytest_lazy_fixtures.lf("population_grid_points_second_three"),),
        ],
    )
    def test_destinations_setter_getter(self, regional_task, destinations):
        regional_task.destinations = destinations
        geopandas.testing.assert_geodataframe_equal(
            regional_task.destinations,
            destinations,
        )

    @pytest.mark.parametrize(
        ["transport_modes", "expected"],
        [
            (
                ["WALK"],
                set([r5py.TransportMode.WALK]),
            ),
            (
                ["TRANSIT", "WALK"],
                set([r5py.TransportMode.TRANSIT, r5py.TransportMode.WALK]),
            ),
            (
                ["GONDOLA", "SUBWAY"],
                set([r5py.TransportMode.GONDOLA, r5py.TransportMode.SUBWAY]),
            ),
        ],
    )
    def test_transport_modes_setter_with_strings(
        self, regional_task, transport_modes, expected
    ):
        regional_task.transport_modes = transport_modes
        assert regional_task.transport_modes == expected

    # TODO: all other methods and attributes!
