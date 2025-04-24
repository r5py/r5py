#!/usr/bin/env python3


"""Fixtures related to transport networks."""


import pytest

from .data_directory import DATA_DIRECTORY


BROKEN_GTFS_FILE = DATA_DIRECTORY / "test_broken_gtfs.zip"


@pytest.fixture
def not_a_gtfs_file():
    """Return a file path of something that is not a GTFS file."""
    import r5py.sampledata.helsinki

    yield r5py.sampledata.helsinki.osm_pbf


@pytest.fixture
def broken_gtfs_file_path():
    """Return a file path of a broken GTFS file."""
    yield BROKEN_GTFS_FILE


@pytest.fixture
def elevation_model_file_path():
    """Return the file path of a GTFS sample data set."""
    import r5py.sampledata.helsinki

    yield r5py.sampledata.helsinki.elevation_model


@pytest.fixture
def gtfs_file_path():
    """Return the file path of a GTFS sample data set."""
    import r5py.sampledata.helsinki

    yield r5py.sampledata.helsinki.gtfs


@pytest.fixture
def gtfs_timezone_helsinki():
    """Return the timezone for Helsinki."""
    yield "Europe/Helsinki"


@pytest.fixture
def helsinki_osm_pbf_file_path():
    """Return the path of the OSM sample data set covering Helsinki."""
    import r5py.sampledata.helsinki

    yield r5py.sampledata.helsinki.osm_pbf


@pytest.fixture
def sao_paulo_osm_pbf_file_path():
    """Return the path of the OSM sample data set covering São Paulo."""
    import r5py.sampledata.sao_paulo

    yield r5py.sampledata.sao_paulo.osm_pbf


@pytest.fixture
def transport_network_files_tuple():
    """Return a tuple of transport network input test data file paths."""
    import r5py.sampledata.helsinki

    yield r5py.sampledata.helsinki.osm_pbf, [r5py.sampledata.helsinki.gtfs]


@pytest.fixture
def transport_network_checksum():
    """Return the checksum of the default transport network (from files tuple)."""
    yield "43bb097531f722016b26293d9e1cd11878d91e07e89846e1f5ba85c43a4b243c"


@pytest.fixture
def cache_directory():
    """Return a pathlib.Path pointing to r5py’s cache directory."""
    from r5py.util.config import Config

    yield Config().CACHE_DIR


@pytest.fixture
def transport_network(transport_network_from_test_files):
    """Return an `r5py.TransportNetwork`."""
    yield transport_network_from_test_files


@pytest.fixture
def transport_network_from_test_directory():
    """Return an `r5py.TransportNetwork` initiated from a directory path."""
    import r5py
    import r5py.sampledata.helsinki
    from ..temporary_directory import TemporaryDirectory

    with TemporaryDirectory() as temp_directory:
        (temp_directory / r5py.sampledata.helsinki.osm_pbf.name).symlink_to(
            r5py.sampledata.helsinki.osm_pbf
        )
        (temp_directory / r5py.sampledata.helsinki.gtfs.name).symlink_to(
            r5py.sampledata.helsinki.gtfs
        )

        transport_network = r5py.TransportNetwork.from_directory(temp_directory)
        yield transport_network

        del transport_network


@pytest.fixture
def transport_network_from_test_files():
    """Return an `r5py.TransportNetwork` initiated from test file paths."""
    import r5py
    import r5py.sampledata.helsinki

    transport_network = r5py.TransportNetwork(
        r5py.sampledata.helsinki.osm_pbf, [r5py.sampledata.helsinki.gtfs]
    )
    yield transport_network

    del transport_network


@pytest.fixture
def transport_network_from_test_files_without_gtfs():
    """Return an `r5py.TransportNetwork` initiated without GTFS data."""
    import r5py
    import r5py.sampledata.helsinki

    transport_network = r5py.TransportNetwork(r5py.sampledata.helsinki.osm_pbf, [])
    yield transport_network

    del transport_network
