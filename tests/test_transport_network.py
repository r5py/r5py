#!/usr/bin/env python3

import pathlib
import random
import shutil
import string

import geopandas
import pytest
import pytest_lazy_fixtures
import shapely

from .temporary_directory import TemporaryDirectory

import r5py
import com.conveyal.r5
import java.time


class Test_TransportNetwork:
    def test_init_from_files_and_dir_cover_same_extent(
        self,
        transport_network_from_test_files,
        transport_network_from_test_directory,
    ):
        assert (
            transport_network_from_test_files._transport_network.getEnvelope()
            == transport_network_from_test_directory._transport_network.getEnvelope()
        )

    @pytest.mark.parametrize(
        ["transport_network"],
        [
            (pytest_lazy_fixtures.lf("transport_network_from_test_files"),),
            (pytest_lazy_fixtures.lf("transport_network_from_test_directory"),),
        ],
    )
    def test_transport_network_java_object(self, transport_network):
        assert isinstance(
            transport_network._transport_network,
            com.conveyal.r5.transit.TransportNetwork,
        )

    @pytest.mark.parametrize(
        ["transport_network"],
        [
            (pytest_lazy_fixtures.lf("transport_network_from_test_files"),),
            (pytest_lazy_fixtures.lf("transport_network_from_test_directory"),),
        ],
    )
    def test_context(self, transport_network):
        with transport_network as tn:
            assert isinstance(tn, r5py.TransportNetwork)
            assert tn == transport_network

    @pytest.mark.parametrize(
        ["transport_network"],
        [
            (pytest_lazy_fixtures.lf("transport_network_from_test_files"),),
            (pytest_lazy_fixtures.lf("transport_network_from_test_directory"),),
        ],
    )
    def test_linkage_cache_java_object(self, transport_network):
        assert isinstance(
            transport_network.linkage_cache, com.conveyal.r5.analyst.LinkageCache
        )

    @pytest.mark.parametrize(
        ["transport_network"],
        [
            (pytest_lazy_fixtures.lf("transport_network_from_test_files"),),
            (pytest_lazy_fixtures.lf("transport_network_from_test_directory"),),
        ],
    )
    def test_street_layer(self, transport_network):
        assert isinstance(transport_network.street_layer, r5py.r5.StreetLayer)

    @pytest.mark.parametrize(
        ["transport_network"],
        [
            (pytest_lazy_fixtures.lf("transport_network_from_test_files"),),
            (pytest_lazy_fixtures.lf("transport_network_from_test_directory"),),
        ],
    )
    def test_timezone(self, transport_network, gtfs_timezone_helsinki):
        assert isinstance(transport_network.timezone, java.time.ZoneId)
        assert transport_network.timezone.toString() == gtfs_timezone_helsinki

    def test_fromdirectory_multiple_osm_files(self, transport_network_files_tuple):
        # try to create transport network from a directory, in which
        # more than one osm file is found
        osm, gtfs = transport_network_files_tuple
        with TemporaryDirectory() as temp_directory:
            temp_directory = pathlib.Path(temp_directory)
            shutil.copy(osm, temp_directory / "first.osm.pbf")
            shutil.copy(osm, temp_directory / "second.osm.pbf")
            with pytest.warns(RuntimeWarning):
                transport_network = r5py.TransportNetwork.from_directory(  # noqa: F841
                    temp_directory
                )

    def test_fromdirectory_no_osm_files(self):
        # try to create transport network from a directory without osm file
        with TemporaryDirectory() as temp_directory:
            temp_directory = pathlib.Path(temp_directory)
            with pytest.raises(FileNotFoundError):
                transport_network = r5py.TransportNetwork.from_directory(  # noqa: F841
                    temp_directory
                )

    def test_snap_to_network(
        self,
        transport_network,
        population_grid_points,
        snapped_population_grid_points,
    ):
        snapped = transport_network.snap_to_network(population_grid_points.geometry)
        geopandas.testing.assert_geoseries_equal(
            snapped.geometry, snapped_population_grid_points.geometry
        )

    def test_snap_to_network_with_unsnappable_points(
        self,
        transport_network,
        unsnappable_points,
    ):
        snapped = transport_network.snap_to_network(unsnappable_points.geometry)
        assert snapped.geometry.unique() == [shapely.Point()]

    def test_failed_symlink(self, transport_network_files_tuple, monkeypatch):
        def _symlink_to(*args, **kwargs):
            raise OSError

        monkeypatch.setattr(pathlib.Path, "symlink_to", _symlink_to)

        transport_network = r5py.TransportNetwork(*transport_network_files_tuple)
        del transport_network

    @pytest.mark.parametrize(
        ["osm_pbf_type", "gtfs_type", "gtfs_is_list"],
        [
            (pathlib.Path, pathlib.Path, False),
            (pathlib.Path, pathlib.Path, True),
            (pathlib.Path, str, False),
            (pathlib.Path, str, True),
            (str, pathlib.Path, False),
            (str, pathlib.Path, True),
            (str, str, False),
            (str, str, True),
        ],
    )
    def test_argument_types(
        self,
        helsinki_osm_pbf_file_path,
        gtfs_file_path,
        osm_pbf_type,
        gtfs_type,
        gtfs_is_list,
    ):
        osm_pbf = osm_pbf_type(helsinki_osm_pbf_file_path)
        gtfs = gtfs_type(gtfs_file_path)
        if gtfs_is_list:
            gtfs = [gtfs]
        transport_network = r5py.TransportNetwork(osm_pbf, gtfs)
        del transport_network

    def test_broken_gtfs_file(
        self,
        helsinki_osm_pbf_file_path,
        broken_gtfs_file_path,
    ):
        with pytest.raises(
            r5py.util.exceptions.GtfsFileError,
            match="Could not load GTFS file.*",
        ):
            _ = r5py.TransportNetwork(
                helsinki_osm_pbf_file_path,
                [broken_gtfs_file_path],
            )

    def test_broken_gtfs_file_allow_errors(
        self,
        sao_paulo_osm_pbf_file_path,
        broken_gtfs_file_path,
    ):
        with pytest.warns(
            RuntimeWarning,
            match=".*issues with GTFS file.*",
        ):
            _ = r5py.TransportNetwork(
                sao_paulo_osm_pbf_file_path,
                [broken_gtfs_file_path],
                allow_errors=True,
            )

    def test_transport_network_with_elevation_model_tobler(
        self,
        helsinki_osm_pbf_file_path,
        gtfs_file_path,
        elevation_model_file_path,
    ):
        _ = r5py.TransportNetwork(
            osm_pbf=helsinki_osm_pbf_file_path,
            gtfs=[gtfs_file_path],
            elevation_model=elevation_model_file_path,
            elevation_cost_function=r5py.ElevationCostFunction.TOBLER,
        )

    def test_transport_network_with_elevation_model_minetti(
        self,
        helsinki_osm_pbf_file_path,
        gtfs_file_path,
        elevation_model_file_path,
    ):
        _ = r5py.TransportNetwork(
            osm_pbf=helsinki_osm_pbf_file_path,
            gtfs=[gtfs_file_path],
            elevation_model=elevation_model_file_path,
            elevation_cost_function=r5py.ElevationCostFunction.MINETTI,
        )

    def test_invalid_cache(
        self,
        transport_network_files_tuple,
        cache_directory,
        transport_network_checksum,
    ):
        _ = r5py.TransportNetwork(*transport_network_files_tuple)
        del _

        (
            cache_directory / f"{transport_network_checksum}.transport_network"
        ).write_text("".join(random.choices(string.printable, k=64)))

        _ = r5py.TransportNetwork(*transport_network_files_tuple)

    def test_cache_exists(
        self,
        transport_network,
        cache_directory,
        transport_network_checksum,
    ):
        del transport_network
        assert (
            cache_directory / f"{transport_network_checksum}.transport_network"
        ).exists()
