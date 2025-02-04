#!/usr/bin/env python3

import datetime

import pandas
import geopandas

import r5py
import r5py.util.exceptions


class TestIsochrones:
    def test_isochrones_initialization(
        self,
        transport_network,
        population_grid_points,
        origin_point,
        departure_datetime,
    ):
        isochrones = r5py.Isochrones(
            transport_network,
            origin=origin_point,
            departure=departure_datetime,
            transport_modes=[r5py.TransportMode.TRANSIT],
            isochrones=pandas.timedelta_range(
                start=datetime.timedelta(minutes=15),
                end=datetime.timedelta(hours=2),
                freq=datetime.timedelta(minutes=15),
            ),
        )

        # isochrones_ = isochrones.copy()
        # isochrones_["travel_time"] = isochrones_["travel_time"].apply(
        #    lambda t: round(t.total_seconds() / 60)
        # )
        # isochrones_.to_file("/tmp/isochrones.gpkg")

        assert isinstance(isochrones, r5py.Isochrones)
        assert isinstance(isochrones, geopandas.GeoDataFrame)
        assert isochrones.geometry.geom_type.unique() == ["Polygon"]

        assert isinstance(isochrones.transport_network, r5py.TransportNetwork)
        assert isinstance(isochrones.origins, geopandas.GeoDataFrame)

        assert isochrones.origins.shape == origin_point.shape
