#!/usr/bin/env python3

import geopandas

import r5py
import r5py.util.exceptions


class TestDetailedItinerariesComputer:
    def test_detailed_itineraries_initialization(
        self,
        transport_network,
        population_grid_points,
        origin_point,
        departure_datetime,
    ):
        detailed_itineraries_computer = r5py.DetailedItinerariesComputer(
            transport_network,
            origins=origin_point,
            destinations=population_grid_points,
            departure=departure_datetime,
            transport_modes=[r5py.TransitMode.TRANSIT, r5py.LegMode.WALK],
        )
        assert isinstance(
            detailed_itineraries_computer.transport_network, r5py.TransportNetwork
        )
        assert isinstance(detailed_itineraries_computer.origins, geopandas.GeoDataFrame)
        assert isinstance(
            detailed_itineraries_computer.destinations, geopandas.GeoDataFrame
        )

        assert detailed_itineraries_computer.origins.shape == origin_point.shape
        assert (
            detailed_itineraries_computer.destinations.shape
            == population_grid_points.shape
        )

    def test_detailed_itineraries_initialization_with_files(
        self,
        transport_network_files_tuple,
        population_grid_points,
        origin_point,
        departure_datetime,
    ):
        detailed_itineraries_computer = r5py.DetailedItinerariesComputer(
            transport_network_files_tuple,
            origins=origin_point,
            destinations=population_grid_points,
            departure=departure_datetime,
            transport_modes=[r5py.TransitMode.TRANSIT, r5py.LegMode.WALK],
        )
        assert isinstance(
            detailed_itineraries_computer.transport_network, r5py.TransportNetwork
        )

    def test_one_to_all_with_breakdown(
        self,
        transport_network,
        population_grid_points,
        origin_point,
        departure_datetime,
        data_columns_with_breakdown,
    ):
        detailed_itineraries_computer = r5py.DetailedItinerariesComputer(
            transport_network,
            origins=origin_point,
            destinations=population_grid_points,
            departure=departure_datetime,
            # transport_modes=[r5py.TransitMode.TRANSIT, r5py.LegMode.WALK],
            transport_modes=[r5py.LegMode.WALK],
        )
        detailed_itineraries = detailed_itineraries_computer.compute_travel_times()

        # assert detailed_itineraries.shape == (689, 12)  # number of rows varies greatly
        assert len(detailed_itineraries.columns) == 12

        for col in detailed_itineraries.columns.to_list():
            assert col in data_columns_with_breakdown
        assert detailed_itineraries["n_iterations"].min() > 0
        assert detailed_itineraries["total_time"].min() > 0
        assert detailed_itineraries["transfer_time"].min() >= 0
