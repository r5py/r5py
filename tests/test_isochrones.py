#!/usr/bin/env python3

import geopandas
import shapely

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
            transport_modes=[r5py.TransportMode.TRANSIT, r5py.TransportMode.WALK],
        )

        assert isinstance(isochrones, r5py.Isochrones)
        assert isinstance(isochrones, geopandas.GeoDataFrame)
        assert isochrones.geometry.geom_type in (
            shapely.geometry.Polygon,
            shapely.geometry.MultiPolygon,
        )

        assert isinstance(isochrones.transport_network, r5py.TransportNetwork)
        assert isinstance(isochrones.origins, geopandas.GeoDataFrame)

        assert isochrones.origins.shape == origin_point.shape
