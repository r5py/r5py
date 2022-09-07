#!/usr/bin/env python3

import os
import geopandas
import pandas
import pathlib
import datetime
from shapely.geometry import Point
import pytest  # noqa: F401

import r5py

# test data sets
DATA_DIRECTORY = pathlib.Path(__file__).absolute().parent.parent / "docs" / "data"
OSM_PBF = DATA_DIRECTORY / "Helsinki" / "kantakaupunki.osm.pbf"
GTFS = DATA_DIRECTORY / "Helsinki" / "GTFS.zip"
POP_POINTS = DATA_DIRECTORY / "Helsinki" / "population_points_2020.gpkg"


class TestTravelTimeMatrixComputer:
    @pytest.fixture(scope="session")
    def transport_network(self):
        transport_network = r5py.TransportNetwork(OSM_PBF, [GTFS])
        yield transport_network

    @pytest.fixture
    def population_points(self):
        yield geopandas.read_file(POP_POINTS)

    @pytest.fixture
    def origin_point(self):
        data = {"geometry": Point(24.939858, 60.165964),
                "id": 0,
                "name": "Vanha Kirkkopuisto, Helsinki"}
        yield geopandas.GeoDataFrame(data, index=[0], crs="epsg:4326")

    def test_travel_time_matrix_initialization(self, transport_network, population_points, origin_point):
        travel_time_matrix_computer = r5py.TravelTimeMatrixComputer(
            transport_network,
            origins=origin_point,
            destinations=population_points,
            departure=datetime.datetime(2022, 2, 22, 8, 30),
            transport_modes=[r5py.TransitMode.TRANSIT, r5py.LegMode.WALK],
        )
        assert isinstance(travel_time_matrix_computer.transport_network, r5py.TransportNetwork)
        assert isinstance(travel_time_matrix_computer.origins, geopandas.GeoDataFrame)
        assert isinstance(travel_time_matrix_computer.destinations, geopandas.GeoDataFrame)

        assert travel_time_matrix_computer.origins.shape == origin_point.shape
        assert travel_time_matrix_computer.destinations.shape == population_points.shape
        assert travel_time_matrix_computer.breakdown is False
        assert travel_time_matrix_computer.breakdown_stat == r5py.BreakdownStat.MEAN

    def test_all_to_all(self, transport_network, population_points):
        travel_time_matrix_computer = r5py.TravelTimeMatrixComputer(
            transport_network,
            origins=population_points,
            departure=datetime.datetime(2022, 2, 22, 8, 30),
            transport_modes=[r5py.TransitMode.TRANSIT, r5py.LegMode.WALK],

        )
        travel_time_matrix = travel_time_matrix_computer.compute_travel_times()

        assert isinstance(travel_time_matrix, pandas.DataFrame)
        # TODO: Add more tests

    def test_one_to_all(self, transport_network, population_points, origin_point):
        travel_time_matrix_computer = r5py.TravelTimeMatrixComputer(
            transport_network,
            origins=origin_point,
            destinations=population_points,
            departure=datetime.datetime(2022, 2, 22, 8, 30),
            transport_modes=[r5py.TransitMode.TRANSIT, r5py.LegMode.WALK],

        )
        travel_time_matrix = travel_time_matrix_computer.compute_travel_times()

        assert isinstance(travel_time_matrix, pandas.DataFrame)
        # TODO: Add more tests