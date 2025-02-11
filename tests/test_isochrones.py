#!/usr/bin/env python3

import datetime

import pandas
import pandas.testing
import geopandas
import pytest

import r5py
import r5py.util.exceptions


# TODO:
# - add tests for multiple origins
# - compare results against pre-computed test data sets


class TestIsochrones:
    def test_isochrones_initialization(
        self,
        transport_network,
        origin_point,
        departure_datetime,
    ):

        with pytest.warns():
            isochrones = r5py.Isochrones(
                transport_network,
                origins=origin_point,
                departure=departure_datetime,
                transport_modes=[r5py.TransportMode.TRANSIT],
                isochrones=pandas.timedelta_range(
                    start=datetime.timedelta(minutes=5),
                    end=datetime.timedelta(hours=0.5),
                    freq=datetime.timedelta(minutes=5),
                ),
                snap_to_network=True,
            )

        isochrones_ = isochrones.copy()
        isochrones_["travel_time"] = isochrones_["travel_time"].apply(
            lambda t: round(t.total_seconds() / 60)
        )
        isochrones_.to_file("/tmp/isochrones.gpkg")

        isochrones.destinations.to_file("/tmp/destinations.gpkg")

        assert isinstance(isochrones, r5py.Isochrones)
        assert isinstance(isochrones, geopandas.GeoDataFrame)
        print(isochrones.geometry.geom_type.unique())
        assert isochrones.geometry.geom_type.unique() == ["MultiPolygon"]

        assert isinstance(isochrones.transport_network, r5py.TransportNetwork)
        assert isinstance(isochrones.origins, geopandas.GeoDataFrame)

        assert isochrones.origins.shape == origin_point.shape

    def test_isochrones_origin_shapely_point(
        self,
        transport_network,
        origin_point,
        departure_datetime,
    ):
        _ = r5py.Isochrones(
            transport_network,
            origins=origin_point.iat[0, 2],
            departure=departure_datetime,
            transport_modes=[r5py.TransportMode.TRANSIT],
            isochrones=pandas.timedelta_range(
                start=datetime.timedelta(minutes=15),
                end=datetime.timedelta(hours=2),
                freq=datetime.timedelta(minutes=15),
            ),
        )

    @pytest.mark.parametrize(
        [
            "requested_isochrones",
            "expected_isochrones",
        ],
        [
            (
                [15, 30],
                pandas.TimedeltaIndex(
                    [datetime.timedelta(minutes=15), datetime.timedelta(minutes=30)]
                ),
            ),
        ],
    )
    def test_isochrones_integer_isochrones(
        self,
        transport_network,
        origin_point,
        departure_datetime,
        requested_isochrones,
        expected_isochrones,
    ):
        isochrones = r5py.Isochrones(
            transport_network,
            origins=origin_point.iat[0, 2],
            departure=departure_datetime,
            transport_modes=[r5py.TransportMode.TRANSIT],
            isochrones=requested_isochrones,
        )
        pandas.testing.assert_index_equal(isochrones.isochrones, expected_isochrones)

    def test_isochrones_unset_properties(
        self, transport_network, origin_point, departure_datetime
    ):
        isochrones = r5py.Isochrones(
            transport_network,
            origins=origin_point.iat[0, 2],
            departure=departure_datetime,
            transport_modes=[r5py.TransportMode.TRANSIT],
        )
        del isochrones._isochrones
        with pytest.raises(AttributeError):
            _ = isochrones.isochrones

    def test_isochrones_custom_percentiles(
        self,
        transport_network,
        origin_point,
        departure_datetime,
    ):
        _ = r5py.Isochrones(
            transport_network,
            origins=origin_point.iat[0, 2],
            departure=departure_datetime,
            transport_modes=[r5py.TransportMode.TRANSIT],
            percentiles=[
                1,
            ],
        )
