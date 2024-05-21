#!/usr/bin/env python3


import geopandas
import pandas
import pytest
import pytest_lazy_fixtures
import shapely

import r5py


class TestDataValidation:
    @pytest.fixture
    def geodataframe_with_all_required_columns(self):
        df = geopandas.GeoDataFrame(
            {
                "id": [1],
                "geometry": [shapely.Point()],
            },
            crs="EPSG:4326",
        )
        yield df

    @pytest.fixture
    def geodataframe_without_id_column(self, geodataframe_with_all_required_columns):
        yield geodataframe_with_all_required_columns[["geometry"]]

    @pytest.fixture
    def geodataframe_with_nonunique_id_column(
        self, geodataframe_with_all_required_columns
    ):
        yield pandas.concat(
            [
                geodataframe_with_all_required_columns,
                geodataframe_with_all_required_columns,
            ]
        )

    @pytest.fixture
    def geodataframe_without_crs(self, geodataframe_with_all_required_columns):
        df = geopandas.GeoDataFrame(
            {
                "id": [1],
                "geometry": [shapely.Point()],
            }
        )
        yield df

    @pytest.mark.parametrize(
        ["geodataframe", "expected_exception"],
        [
            (pytest_lazy_fixtures.lf("geodataframe_with_all_required_columns"), False),
            (
                pytest_lazy_fixtures.lf("geodataframe_without_id_column"),
                r5py.util.exceptions.NoIDColumnError,
            ),
            (
                pytest_lazy_fixtures.lf("geodataframe_with_nonunique_id_column"),
                r5py.util.exceptions.NonUniqueIDError,
            ),
            (
                pytest_lazy_fixtures.lf("geodataframe_without_crs"),
                r5py.util.exceptions.NoCrsError,
            ),
        ],
    )
    def test_check_od_data_set(self, geodataframe, expected_exception):
        if expected_exception:
            with pytest.raises(expected_exception):
                r5py.util.data_validation.check_od_data_set(geodataframe)
        else:
            r5py.util.data_validation.check_od_data_set(geodataframe)
