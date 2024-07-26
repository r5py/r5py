#!/usr/bin/env python3

import datetime

import geopandas
import geopandas.testing
import pandas
import pytest
import pytest_lazy_fixtures

import r5py
import r5py.util.exceptions


class TestDetailedItinerariesComputerInputValidation:
    @pytest.mark.parametrize(
        [
            "origins",
            "expected_error",
        ],
        [
            (
                pytest_lazy_fixtures.lf("origins_invalid_no_id"),
                r5py.util.exceptions.NoIDColumnError,
            ),
            (
                pytest_lazy_fixtures.lf("origins_invalid_duplicate_ids"),
                r5py.util.exceptions.NonUniqueIDError,
            ),
        ],
    )
    def test_origins_invalid_data(
        self,
        transport_network,
        origins,
        departure_datetime,
        expected_error,
    ):
        with pytest.raises(expected_error):
            detailed_itineraries_computer_computer = r5py.DetailedItinerariesComputer(
                transport_network,
                origins=origins,
                departure=departure_datetime,
            )
            del detailed_itineraries_computer_computer

    def test_origins_valid_data(
        self,
        transport_network,
        origins_valid_ids,
        departure_datetime,
    ):
        detailed_itineraries_computer_computer = r5py.DetailedItinerariesComputer(
            transport_network,
            origins=origins_valid_ids,
            departure=departure_datetime,
        )
        del detailed_itineraries_computer_computer

    @pytest.mark.parametrize(
        [
            "origins",
            "destinations",
            "expected_error",
        ],
        [
            (
                pytest_lazy_fixtures.lf("origins_invalid_no_id"),
                pytest_lazy_fixtures.lf("origins_invalid_no_id"),
                r5py.util.exceptions.NoIDColumnError,
            ),
            (
                pytest_lazy_fixtures.lf("origins_invalid_duplicate_ids"),
                pytest_lazy_fixtures.lf("origins_invalid_duplicate_ids"),
                r5py.util.exceptions.NonUniqueIDError,
            ),
            (
                pytest_lazy_fixtures.lf("origins_invalid_no_id"),
                pytest_lazy_fixtures.lf("origins_invalid_duplicate_ids"),
                r5py.util.exceptions.NoIDColumnError,
            ),
            (
                pytest_lazy_fixtures.lf("origins_invalid_duplicate_ids"),
                pytest_lazy_fixtures.lf("origins_invalid_no_id"),
                r5py.util.exceptions.NonUniqueIDError,
            ),
        ],
    )
    def test_origins_and_destinations_invalid_data(
        self,
        transport_network,
        origins,
        destinations,
        departure_datetime,
        expected_error,
    ):
        with pytest.raises(expected_error):
            detailed_itineraries_computer_computer = r5py.DetailedItinerariesComputer(
                transport_network,
                origins=origins,
                destinations=destinations,
                departure=departure_datetime,
            )
            del detailed_itineraries_computer_computer

    @pytest.mark.parametrize(
        [
            "origins",
            "destinations",
        ],
        [
            (
                pytest_lazy_fixtures.lf("origins_valid_ids"),
                pytest_lazy_fixtures.lf("origins_valid_ids"),
            )
        ],
    )
    def test_origins_and_destinations_valid_data(
        self,
        transport_network,
        origins,
        destinations,
        departure_datetime,
    ):
        detailed_itineraries_computer_computer = r5py.DetailedItinerariesComputer(
            transport_network,
            origins=origins,
            destinations=destinations,
            departure=departure_datetime,
        )
        _ = detailed_itineraries_computer_computer.compute_travel_details()

    def test_try_to_route_without_origins(
        self,
        transport_network,
        departure_datetime,
    ):
        detailed_itineraries_computer_computer = r5py.DetailedItinerariesComputer(
            transport_network,
            departure=departure_datetime,
        )
        with pytest.raises(ValueError, match="No routing origins defined"):
            _ = detailed_itineraries_computer_computer.compute_travel_details()

    def test_try_to_route_without_destinations(
        self,
        transport_network,
        population_grid_points,
        departure_datetime,
    ):
        detailed_itineraries_computer = r5py.DetailedItinerariesComputer(
            transport_network,
            origins=population_grid_points[0:3],
            departure=departure_datetime,
        )
        _ = detailed_itineraries_computer.compute_travel_details()

        pandas.testing.assert_frame_equal(
            detailed_itineraries_computer.origins,
            detailed_itineraries_computer.destinations,
        )


class TestDetailedItinerariesComputer:
    def test_detailed_itineraries_initialization(
        self,
        transport_network,
        departure_datetime,
    ):
        detailed_itineraries_computer = r5py.DetailedItinerariesComputer(
            transport_network,
            departure=departure_datetime,
            transport_modes=[r5py.TransportMode.TRANSIT, r5py.TransportMode.WALK],
        )
        assert isinstance(
            detailed_itineraries_computer.transport_network, r5py.TransportNetwork
        )

    def test_detailed_itineraries_initialization_with_files(
        self,
        transport_network_files_tuple,
        departure_datetime,
    ):
        detailed_itineraries_computer = r5py.DetailedItinerariesComputer(
            transport_network_files_tuple,
            departure=departure_datetime,
            transport_modes=[r5py.TransportMode.TRANSIT, r5py.TransportMode.WALK],
        )
        assert isinstance(
            detailed_itineraries_computer.transport_network, r5py.TransportNetwork
        )

    @pytest.mark.parametrize(
        [
            "origins",
            "destinations",
            "force_all_to_all",
            "expected_all_to_all",
            "expected_od_pairs_len",
        ],
        [
            (
                pytest_lazy_fixtures.lf("population_grid_points_first_three"),
                None,
                False,
                True,
                9,
            ),
            (
                pytest_lazy_fixtures.lf("population_grid_points_first_three"),
                pytest_lazy_fixtures.lf("population_grid_points_second_three"),
                False,
                False,
                3,
            ),
            (
                pytest_lazy_fixtures.lf("population_grid_points_first_three"),
                pytest_lazy_fixtures.lf("population_grid_points_second_three"),
                True,
                True,
                9,
            ),
            (
                pytest_lazy_fixtures.lf("population_grid_points_first_three"),
                pytest_lazy_fixtures.lf("population_grid_points_four"),
                False,
                True,
                12,
            ),
        ],
    )
    def test_od_pairs_all_to_all(
        self,
        transport_network,
        origins,
        destinations,
        force_all_to_all,
        departure_datetime,
        expected_all_to_all,
        expected_od_pairs_len,
    ):
        detailed_itineraries_computer = r5py.DetailedItinerariesComputer(
            transport_network,
            origins=origins,
            destinations=destinations,
            force_all_to_all=force_all_to_all,
            departure=departure_datetime,
            transport_modes=[r5py.TransportMode.WALK],
        )
        _ = detailed_itineraries_computer.compute_travel_details()
        assert detailed_itineraries_computer.all_to_all == expected_all_to_all
        assert len(detailed_itineraries_computer.od_pairs) == expected_od_pairs_len

    @pytest.mark.filterwarnings(
        "ignore:Departure time .* is outside of the time range covered by currently loaded GTFS data sets."
    )
    def test_gtfs_date_range_warnings(
        self,
        transport_network,
        population_grid_points,
        origin_point,
        departure_datetime,
    ):
        with pytest.warns(RuntimeWarning):
            travel_details_matrix_computer = r5py.DetailedItinerariesComputer(
                transport_network,
                origins=origin_point,
                destinations=population_grid_points,
                departure=datetime.datetime(2021, 2, 22, 8, 30),  # not in GTFS data set
                transport_modes=[r5py.TransportMode.TRANSIT, r5py.TransportMode.WALK],
            )
            del travel_details_matrix_computer

    @pytest.mark.filterwarnings(
        "ignore:Departure time .* is outside of the time range covered by currently loaded GTFS data sets."
    )
    def test_gtfs_date_range_warnings_without_gtfs_file(
        self,
        transport_network_from_test_files_without_gtfs,
        population_grid_points,
        origin_point,
        departure_datetime,
    ):
        with pytest.warns(RuntimeWarning):
            detailed_itineraries_computer = r5py.DetailedItinerariesComputer(
                transport_network_from_test_files_without_gtfs,
                origins=origin_point,
                destinations=population_grid_points,
                departure=departure_datetime,
                transport_modes=[r5py.TransportMode.TRANSIT, r5py.TransportMode.WALK],
            )
            del detailed_itineraries_computer

    @pytest.mark.parametrize(
        [
            "snap_to_network",
            "expected_snap_to_network",
        ],
        [
            (
                True,
                True,
            ),
            (
                False,
                False,
            ),
        ],
    )
    def test_snap_to_network_parameter(
        self,
        transport_network,
        population_grid_points,
        departure_datetime,
        snap_to_network,
        expected_snap_to_network,
    ):
        detailed_itineraries_computer = r5py.DetailedItinerariesComputer(
            transport_network,
            population_grid_points,
            departure=departure_datetime,
            snap_to_network=snap_to_network,
        )
        assert detailed_itineraries_computer.snap_to_network == expected_snap_to_network

    @pytest.mark.parametrize(
        [
            "snap_to_network",
            "expected_travel_details",
        ],
        [
            (
                True,
                pytest_lazy_fixtures.lf("walking_details_snapped"),
            ),
            (
                False,
                pytest_lazy_fixtures.lf("walking_details_not_snapped"),
            ),
        ],
    )
    def test_snap_to_network(
        self,
        transport_network,
        population_grid_points,
        departure_datetime,
        snap_to_network,
        expected_travel_details,
    ):
        # subset to keep test comparison data sets small
        origins = population_grid_points[::5]
        detailed_itineraries_computer = r5py.DetailedItinerariesComputer(
            transport_network,
            origins=origins,
            departure=departure_datetime,
            snap_to_network=snap_to_network,
            transport_modes=[r5py.TransportMode.WALK],
        )
        travel_details = detailed_itineraries_computer.compute_travel_details()

        travel_details = (
            travel_details.groupby(["from_id", "to_id", "option"])
            .sum(["travel_time", "distance"])
            .reset_index()
        )

        travel_details = travel_details.set_index(["from_id", "to_id"]).sort_index()
        expected_travel_details = expected_travel_details.set_index(
            ["from_id", "to_id"]
        ).sort_index()

        pandas.testing.assert_frame_equal(travel_details, expected_travel_details)

    def test_snap_to_network_with_unsnappable_origins(
        self,
        transport_network,
        unsnappable_points,
        population_grid_points,
        departure_datetime,
    ):
        origins = pandas.concat(
            [population_grid_points[-3:], unsnappable_points]
        ).reset_index(drop=False)
        with pytest.warns(
            RuntimeWarning,
            match="Some (origin|destination) points could not be snapped to the street network",
        ):
            travel_time_matrix = r5py.TravelTimeMatrixComputer(
                transport_network,
                origins,
                departure=departure_datetime,
                snap_to_network=True,
                transport_modes=[r5py.TransportMode.WALK],
            )
            _ = travel_time_matrix.compute_travel_times()

    def test_snap_to_network_with_only_unsnappable_origins(
        self,
        transport_network,
        unsnappable_points,
        departure_datetime,
    ):
        with pytest.raises(
            ValueError, match="After snapping, no valid origin points remain"
        ):
            with pytest.warns(
                RuntimeWarning,
                match="Some (origin|destination) points could not be snapped to the street network",
            ):
                travel_time_matrix = r5py.TravelTimeMatrixComputer(
                    transport_network,
                    unsnappable_points,
                    departure=departure_datetime,
                    snap_to_network=True,
                    transport_modes=[r5py.TransportMode.WALK],
                )
                _ = travel_time_matrix.compute_travel_times()

    def test_snap_to_network_with_unsnappable_destinations(
        self,
        transport_network,
        population_grid_points,
        unsnappable_points,
        departure_datetime,
    ):
        destinations = pandas.concat(
            [population_grid_points[-3:], unsnappable_points]
        ).reset_index(drop=False)
        with pytest.warns(
            RuntimeWarning,
            match="Some destination points could not be snapped to the street network",
        ):
            travel_time_matrix = r5py.TravelTimeMatrixComputer(
                transport_network,
                origins=population_grid_points,
                destinations=destinations,
                departure=departure_datetime,
                snap_to_network=True,
                transport_modes=[r5py.TransportMode.WALK],
            )
            _ = travel_time_matrix.compute_travel_times()

    def test_snap_to_network_with_only_unsnappable_destinations(
        self,
        transport_network,
        population_grid_points,
        unsnappable_points,
        departure_datetime,
    ):
        with pytest.raises(
            ValueError, match="After snapping, no valid destination points remain"
        ):
            with pytest.warns(
                RuntimeWarning,
                match="Some destination points could not be snapped to the street network",
            ):
                travel_time_matrix = r5py.TravelTimeMatrixComputer(
                    transport_network,
                    origins=population_grid_points,
                    destinations=unsnappable_points,
                    departure=departure_datetime,
                    snap_to_network=True,
                    transport_modes=[r5py.TransportMode.WALK],
                )
                _ = travel_time_matrix.compute_travel_times()

    @pytest.mark.parametrize("snap_to_network", [True, False])
    def test_travel_details_between_identical_from_and_to_ids(
        self,
        transport_network,
        population_grid_points,
        departure_datetime,
        snap_to_network,
    ):
        detailed_itineraries = r5py.DetailedItinerariesComputer(
            transport_network,
            origins=population_grid_points,
            transport_modes=[r5py.TransportMode.WALK],
            departure=departure_datetime,
            snap_to_network=snap_to_network,
        ).compute_travel_details()

        assert detailed_itineraries[
            detailed_itineraries["from_id"] == detailed_itineraries["to_id"]
        ].travel_time.max() == datetime.timedelta(seconds=0)

    @pytest.mark.parametrize(
        [
            "transport_mode",
            "expected_travel_details",
        ],
        [
            (
                r5py.TransportMode.BICYCLE,
                pytest_lazy_fixtures.lf("detailed_itineraries_bicycle"),
            ),
            (
                r5py.TransportMode.CAR,
                pytest_lazy_fixtures.lf("detailed_itineraries_car"),
            ),
            (
                r5py.TransportMode.TRANSIT,
                pytest_lazy_fixtures.lf("detailed_itineraries_transit"),
            ),
            (
                r5py.TransportMode.WALK,
                pytest_lazy_fixtures.lf("detailed_itineraries_walk"),
            ),
        ],
    )
    def test_travel_details_by_transport_mode(
        self,
        transport_network,
        population_grid_points,
        departure_datetime,
        transport_mode,
        expected_travel_details,
    ):
        # subset to keep test comparison data sets small
        origins = population_grid_points[::5].copy()
        detailed_itineraries_computer = r5py.DetailedItinerariesComputer(
            transport_network,
            origins=origins,
            departure=departure_datetime,
            departure_time_window=datetime.timedelta(
                hours=1
            ),  # using old default for simplicity
            transport_modes=[transport_mode],
        )
        travel_details = detailed_itineraries_computer.compute_travel_details()

        travel_details.travel_time = travel_details.travel_time.apply(
            lambda t: t.total_seconds()
        )
        travel_details.wait_time = travel_details.wait_time.apply(
            lambda t: t.total_seconds()
        )
        travel_details.transport_mode = travel_details.transport_mode.apply(
            lambda t: t.value
        )
        travel_details["departure_time"] = travel_details["departure_time"].astype(
            "datetime64[ms]"
        )

        travel_details = geopandas.GeoDataFrame(travel_details, crs="EPSG:4326")

        geopandas.testing.assert_geodataframe_equal(
            travel_details,
            expected_travel_details,
            check_less_precise=True,  # geometries
            check_dtype=False,
            normalize=True,
        )
