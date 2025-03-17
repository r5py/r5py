#!/usr/bin/env python3

import datetime

import geopandas
import geopandas.testing
import pandas
import pandas.testing
import pytest
import pytest_lazy_fixtures
import shapely

import r5py
import r5py.util.exceptions


class TestIsochrones:
    def test_isochrones_initialization(
        self,
        transport_network,
        origin_point,
        departure_datetime,
    ):

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
        )

        assert isinstance(isochrones, r5py.Isochrones)
        assert isinstance(isochrones, geopandas.GeoDataFrame)
        assert isochrones.geometry.geom_type.unique() == ["MultiLineString"]

        assert isinstance(isochrones.origins, geopandas.GeoDataFrame)

        assert isochrones.origins.shape == origin_point.shape

    def test_isochrones_origin_shapely_point(
        self,
        transport_network,
        origin_point,
        departure_datetime,
    ):
        origin_point = origin_point.iat[0, 2]
        assert isinstance(origin_point, shapely.Point)

        _ = r5py.Isochrones(
            transport_network,
            origins=origin_point,
            departure=departure_datetime,
            transport_modes=[r5py.TransportMode.TRANSIT],
            isochrones=pandas.timedelta_range(
                start=datetime.timedelta(minutes=15),
                end=datetime.timedelta(hours=2),
                freq=datetime.timedelta(minutes=15),
            ),
        )

    def test_isochrones_from_multiple_origins(
        self,
        transport_network,
        multiple_origins,
        departure_datetime,
        isochrones_from_multiple_origins,  # expected
    ):
        isochrones = r5py.Isochrones(
            transport_network,
            origins=multiple_origins,
            departure=departure_datetime,
            isochrones=[5, 10],
        )
        isochrones["travel_time"] = isochrones["travel_time"].apply(
            lambda t: round(t.total_seconds() / 60)
        )

        isochrones["geometry"] = isochrones["geometry"].set_precision(0.0001)

        geopandas.testing.assert_geodataframe_equal(
            isochrones,
            isochrones_from_multiple_origins,
            check_less_precise=True,  # geometries
            check_dtype=False,
            normalize=True,
        )

    @pytest.mark.parametrize(
        [
            "transport_mode",
            "expected_isochrones",
        ],
        [
            (
                r5py.TransportMode.BICYCLE,
                pytest_lazy_fixtures.lf("isochrones_bicycle"),
            ),
            (
                r5py.TransportMode.CAR,
                pytest_lazy_fixtures.lf("isochrones_car"),
            ),
            (
                r5py.TransportMode.TRANSIT,
                pytest_lazy_fixtures.lf("isochrones_transit"),
            ),
            (
                r5py.TransportMode.WALK,
                pytest_lazy_fixtures.lf("isochrones_walk"),
            ),
        ],
    )
    def test_isochrones_multimodal(
        self,
        transport_network,
        origin_point,
        departure_datetime,
        transport_mode,
        expected_isochrones,
    ):
        isochrones = r5py.Isochrones(
            transport_network,
            origins=origin_point,
            isochrones=[5],
            departure=departure_datetime,
            transport_modes=[transport_mode],
        )
        isochrones["travel_time"] = isochrones["travel_time"].apply(
            lambda t: round(t.total_seconds() / 60)
        )

        isochrones["geometry"] = isochrones["geometry"].set_precision(0.0001)

        geopandas.testing.assert_geodataframe_equal(
            isochrones,
            expected_isochrones,
            check_less_precise=True,  # geometries
            check_dtype=False,
            normalize=True,
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
            (
                [0, 5, 10],
                pandas.TimedeltaIndex(
                    [datetime.timedelta(minutes=5), datetime.timedelta(minutes=10)]
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
            percentiles=[1],
        )

    @pytest.mark.parametrize(
        [
            "point_grid_resolution",
            "point_grid_sample_ratio",
            "expected_number_of_destinations",
        ],
        [
            (100, 0.8, 2654),
            (50, 1.0, 12101),
            (200, 0.3, 285),
        ],
    )
    def test_isochrones_point_grid_parameters(
        self,
        transport_network,
        origin_point,
        departure_datetime,
        point_grid_resolution,
        point_grid_sample_ratio,
        expected_number_of_destinations,
    ):
        isochrones = r5py.Isochrones(
            transport_network,
            origins=origin_point,
            departure=departure_datetime,
            point_grid_resolution=point_grid_resolution,
            point_grid_sample_ratio=point_grid_sample_ratio,
        )

        assert len(isochrones.destinations) == pytest.approx(
            expected_number_of_destinations, abs=5
        )
