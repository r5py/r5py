#!/usr/bin/env python3


"""Wraps a com.conveyal.r5.transit.TransportNetwork."""


import functools
import pathlib
import random
import shutil
import warnings

import filelock
import jpype
import jpype.types

from .street_layer import StreetLayer
from .transit_layer import TransitLayer
from .transport_mode import TransportMode
from ..util import Config, contains_gtfs_data, start_jvm

import com.conveyal.gtfs
import com.conveyal.osmlib
import com.conveyal.r5


__all__ = ["TransportNetwork"]


PACKAGE = __package__.split(".")[0]


start_jvm()


class TransportNetwork:
    """Wrap a com.conveyal.r5.transit.TransportNetwork."""

    def __init__(self, osm_pbf, gtfs=[]):
        """
        Load a transport network.

        Arguments
        ---------
        osm_pbf : str
            file path of an OpenStreetMap extract in PBF format
        gtfs : list[str]
            paths to public transport schedule information in GTFS format
        """
        osm_pbf = self._working_copy(pathlib.Path(osm_pbf)).absolute()
        gtfs = [str(self._working_copy(path).absolute()) for path in gtfs]

        transport_network = com.conveyal.r5.transit.TransportNetwork()
        transport_network.scenarioId = PACKAGE

        osm_file = pathlib.Path(f"{osm_pbf}.mapdb")
        if osm_file.exists():
            osm_file.unlink()
        osm_file = com.conveyal.osmlib.OSM(f"{osm_file}")
        osm_file.intersectionDetection = True
        osm_file.readFromFile(f"{osm_pbf}")
        transport_network.streetLayer = com.conveyal.r5.streets.StreetLayer()
        transport_network.streetLayer.loadFromOsm(osm_file)
        transport_network.streetLayer.parentNetwork = transport_network
        transport_network.streetLayer.indexStreets()

        transport_network.transitLayer = com.conveyal.r5.transit.TransitLayer()
        for gtfs_file in gtfs:
            gtfs_feed = com.conveyal.gtfs.GTFSFeed.readOnlyTempFileFromGtfs(gtfs_file)
            transport_network.transitLayer.loadFromGtfs(gtfs_feed)
            gtfs_feed.close()
        transport_network.transitLayer.parentNetwork = transport_network

        transport_network.streetLayer.associateStops(transport_network.transitLayer)
        transport_network.streetLayer.buildEdgeLists()

        transport_network.transitLayer.rebuildTransientIndexes()

        transfer_finder = com.conveyal.r5.transit.TransferFinder(transport_network)
        transfer_finder.findTransfers()
        transfer_finder.findParkRideTransfer()

        transport_network.transitLayer.buildDistanceTables(None)

        self._transport_network = transport_network

    @classmethod
    def from_directory(cls, path):
        """
        Find input data in `path`, load an `r5py.TransportNetwork`.

        This mimicks r5r’s behaviour to accept a directory path
        as the only input to `setup_r5()`.

        If more than one OpenStreetMap extract (`.osm.pbf`) is
        found in `path`, the (alphabetically) first one is used.
        In case *no* OpenStreetMap extract is found, a `FileNotFound`
        exception is raised. Any and all GTFS data files are used.

        Arguments
        ---------
        path : str
            directory path in which to search for GTFS and .osm.pbf files

        Returns
        -------
        TransportNetwork
            A fully initialised r5py.TransportNetwork
        """
        path = pathlib.Path(path)
        try:
            potential_osm_pbf_files = sorted(path.glob("*.osm.pbf"))
            osm_pbf = potential_osm_pbf_files[0]
            if len(potential_osm_pbf_files) > 1:
                warnings.warn(
                    (
                        f"Found more than one OpenStreetMap extract file (`.osm.pbf`), "
                        f"using alphabetically first one ({osm_pbf.name})"
                    ),
                    RuntimeWarning,
                )
        except IndexError:
            raise FileNotFoundError(
                f"Could not find any OpenStreetMap extract file (`.osm.pbf`) in {path.absolute()}"
            )
        gtfs = [
            potential_gtfs_file
            for potential_gtfs_file in path.glob("*.zip")
            if contains_gtfs_data(potential_gtfs_file)
        ]

        return cls(osm_pbf, gtfs)

    def __enter__(self):
        """Provide a context."""
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        """Exit context."""
        return False

    @functools.cached_property
    def _cache_directory(self):
        cache_dir = (
            pathlib.Path(Config().TEMP_DIR)
            / f"{self.__class__.__name__:s}_{id(self):x}_{random.randrange(16**5):07x}"
        )
        cache_dir.mkdir(exist_ok=True)
        return cache_dir

    def _working_copy(self, input_file):
        """Create a copy or link of an input file in a cache directory.

        This method exists because R5 creates temporary files in the
        directory of input files. This can not only be annoying clutter,
        but also create problems of concurrency, performance, etc., for
        instance, when the data comes from a shared network drive or a
        read-only file system.

        Arguments
        ---------
        input_file : str or pathlib.Path
            The file to create a copy or link of in a cache directory

        Returns
        -------
        pathlib.Path
            The path to the copy or link created
        """
        # try to first create a symbolic link, if that fails (e.g., on Windows),
        # copy the file to a cache directory
        input_file = pathlib.Path(input_file).absolute()
        destination_file = pathlib.Path(
            self._cache_directory / input_file.name
        ).absolute()

        with filelock.FileLock(
            destination_file.parent / f"{destination_file.name}.lock"
        ):
            if not destination_file.exists():
                try:
                    destination_file.symlink_to(input_file)
                except OSError:
                    shutil.copyfile(str(input_file), str(destination_file))
        return destination_file

    @property
    def linkage_cache(self):
        """Expose the `TransportNetwork`’s `linkageCache` to Python."""
        return self._transport_network.linkageCache

    def snap_to_network(
        self,
        points,
        radius=com.conveyal.r5.streets.StreetLayer.LINK_RADIUS_METERS,
        street_mode=TransportMode.WALK,
    ):
        """
        Snap `points` to valid locations on the network.

        Arguments
        ---------
        points : geopandas.GeoSeries
            point geometries that will be snapped to the network
        radius : float
            Search radius around each `point`
        street_mode : travel mode that the snapped-to street should allow

        Returns
        -------
        geopandas.GeoSeries
            point geometries that have been snapped to the network,
            using the same index and order as the input `points`
        """
        return points.apply(
            functools.partial(
                self.street_layer.find_split,
                radius=radius,
                street_mode=street_mode,
            )
        )

    @property
    def street_layer(self):
        """Expose the `TransportNetwork`’s `streetLayer` to Python."""
        return StreetLayer.from_r5_street_layer(self._transport_network.streetLayer)

    @property
    def timezone(self):
        """Determine the timezone of the GTFS data."""
        return self._transport_network.getTimeZone()

    @functools.cached_property
    def transit_layer(self):
        """Expose the `TransportNetwork`’s `transitLayer` to Python."""
        transit_layer = TransitLayer.from_r5_transit_layer(
            self._transport_network.transitLayer
        )
        return transit_layer


@jpype._jcustomizer.JConversion(
    "com.conveyal.r5.transit.TransportNetwork", exact=TransportNetwork
)
def _cast_TransportNetwork(java_class, object_):
    return object_._transport_network
