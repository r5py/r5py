#!/usr/bin/env python3

import filecmp
import pathlib
import shutil

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

    def test_cache_directory(self, transport_network_files_tuple):
        transport_network = r5py.TransportNetwork(*transport_network_files_tuple)
        cache_dir = transport_network._cache_directory
        assert cache_dir.is_dir()
        assert (
            len(list(cache_dir.glob("*"))) > 0
        )  # files have been copied/linked to cache

        del transport_network

    @pytest.mark.parametrize(
        ["transport_network"],
        [
            (pytest_lazy_fixtures.lf("transport_network_from_test_files"),),
            (pytest_lazy_fixtures.lf("transport_network_from_test_directory"),),
        ],
    )
    def test_working_copy(self, transport_network):
        with TemporaryDirectory() as temp_directory:
            # create a file with (not really) random content
            input_file = pathlib.Path(temp_directory) / "test_input.txt"
            with open(input_file, "w") as f:
                print("asdffoobarrandomstring", file=f)
            working_copy = transport_network._working_copy(input_file)
            assert filecmp.cmp(input_file, working_copy, shallow=False)

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

    def test_failed_unlinking_of_temporary_files(
        self, transport_network_files_tuple, monkeypatch
    ):
        def _unlink(*args, **kwargs):
            raise OSError

        monkeypatch.setattr(pathlib.Path, "unlink", _unlink)

        transport_network = r5py.TransportNetwork(*transport_network_files_tuple)
        with pytest.warns(RuntimeWarning, match="Failed to clean cache directory"):
            del transport_network

    def test_failed_cachedir_rmdir(self, transport_network_files_tuple, monkeypatch):
        def _rmdir(*args, **kwargs):
            raise OSError

        monkeypatch.setattr(pathlib.Path, "rmdir", _rmdir)

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
        osm_pbf_file_path,
        gtfs_file_path,
        osm_pbf_type,
        gtfs_type,
        gtfs_is_list,
    ):
        osm_pbf = osm_pbf_type(osm_pbf_file_path)
        gtfs = gtfs_type(gtfs_file_path)
        if gtfs_is_list:
            gtfs = [gtfs]
        transport_network = r5py.TransportNetwork(osm_pbf, gtfs)
        del transport_network
