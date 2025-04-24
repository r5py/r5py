#!/usr/bin/env python3


"""Wraps a com.conveyal.r5.transit.TransportNetwork."""


import functools
import hashlib
import pathlib
import warnings

import jpype
import jpype.types

from .elevation_cost_function import ElevationCostFunction
from .elevation_model import ElevationModel
from .street_layer import StreetLayer
from .transit_layer import TransitLayer
from .transport_mode import TransportMode
from ..util import Config, contains_gtfs_data, FileDigest, start_jvm, WorkingCopy
from ..util.exceptions import GtfsFileError

import com.conveyal.analysis
import com.conveyal.gtfs
import com.conveyal.osmlib
import com.conveyal.r5
import java.io


__all__ = ["TransportNetwork"]


PACKAGE = __package__.split(".")[0]


start_jvm()


class TransportNetwork:
    """Wrap a com.conveyal.r5.transit.TransportNetwork."""

    def __init__(
        self,
        osm_pbf,
        gtfs=[],
        elevation_model=None,
        elevation_cost_function=ElevationCostFunction.TOBLER,
        allow_errors=False,
    ):
        """
        Load a transport network.

        Arguments
        ---------
        osm_pbf : str | pathlib.Path
            file path of an OpenStreetMap extract in PBF format
        gtfs : str | pathlib.Path | list[str] | list[pathlib.Path]
            path(s) to public transport schedule information in GTFS format
        elevation_model : str | pathlib.Path
            file path to a digital elevation model in TIF format,
            single-band, the value of which is the elevation in metres
        elevation_cost_function : r5py.ElevationCostFunction
            which algorithm to use to compute the added effort and travel time
            of slopes
        allow_errors : bool
            try to proceed with loading the transport network even if input data
            contain errors
        """
        osm_pbf = WorkingCopy(osm_pbf)
        if isinstance(gtfs, (str, pathlib.Path)):
            gtfs = [gtfs]
        gtfs = [WorkingCopy(path) for path in gtfs]

        # a hash representing all input files
        digest = hashlib.sha256(
            "".join(
                [FileDigest(osm_pbf)]
                + [FileDigest(path) for path in gtfs]
                + [FileDigest(elevation_model) if elevation_model is not None else ""]
            ).encode("utf-8")
        ).hexdigest()

        try:
            transport_network = self._load_pickled_transport_network(
                Config().CACHE_DIR / f"{digest}.transport_network"
            )
        except (FileNotFoundError, java.io.IOError, java.lang.RuntimeException):
            transport_network = com.conveyal.r5.transit.TransportNetwork()
            transport_network.scenarioId = PACKAGE

            osm_mapdb = Config().CACHE_DIR / f"{digest}.mapdb"
            osm_file = com.conveyal.osmlib.OSM(f"{osm_mapdb}")
            osm_file.intersectionDetection = True
            osm_file.readFromFile(f"{osm_pbf}")

            transport_network.streetLayer = com.conveyal.r5.streets.StreetLayer()
            transport_network.streetLayer.parentNetwork = transport_network
            transport_network.streetLayer.loadFromOsm(osm_file)
            transport_network.streetLayer.indexStreets()

            transport_network.transitLayer = com.conveyal.r5.transit.TransitLayer()
            transport_network.transitLayer.parentNetwork = transport_network
            for gtfs_file in gtfs:
                gtfs_feed = com.conveyal.gtfs.GTFSFeed.writableTempFileFromGtfs(
                    f"{gtfs_file}"
                )
                if gtfs_feed.errors.size() > 0:
                    errors = [
                        f"{error.errorType}: {error.getMessageWithContext()}"
                        for error in gtfs_feed.errors
                    ]
                    if allow_errors:
                        warnings.warn(
                            (
                                "R5 reported the following issues with "
                                f"GTFS file {gtfs_file.name}: \n"
                                + ("\n- ".join(errors))
                            ),
                            RuntimeWarning,
                        )
                    else:
                        raise GtfsFileError(
                            (
                                f"Could not load GTFS file {gtfs_file.name}. \n"
                                + ("\n- ".join(errors))
                            )
                        )

                transport_network.transitLayer.loadFromGtfs(gtfs_feed)
                gtfs_feed.close()

            transport_network.streetLayer.associateStops(transport_network.transitLayer)
            transport_network.streetLayer.buildEdgeLists()

            transport_network.transitLayer.rebuildTransientIndexes()

            transfer_finder = com.conveyal.r5.transit.TransferFinder(transport_network)
            transfer_finder.findTransfers()
            transfer_finder.findParkRideTransfer()

            transport_network.transitLayer.buildDistanceTables(None)

            if elevation_model is not None:
                ElevationModel(
                    elevation_model,
                    elevation_cost_function,
                ).apply_to(transport_network)

            osm_file.close()  # not needed after here?

            self._save_pickled_transport_network(
                transport_network, Config().CACHE_DIR / f"{digest}.transport_network"
            )

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

    @property
    def extent(self):
        """The geographic area covered, as a `shapely.box`."""
        # TODO: figure out how to get the extent of the GTFS schedule,
        # then find the smaller extent of the two (or the larger one?)
        return self.street_layer.extent

    @property
    def linkage_cache(self):
        """Expose the `TransportNetwork`’s `linkageCache` to Python."""
        return self._transport_network.linkageCache

    def _load_pickled_transport_network(self, path):
        try:
            input_file = java.io.File(f"{path}")
            return com.conveyal.r5.kryo.KryoNetworkSerializer.read(input_file)
        except java.io.FileNotFoundException:
            raise FileNotFoundError

    def _save_pickled_transport_network(self, transport_network, path):
        output_file = java.io.File(f"{path}")
        com.conveyal.r5.kryo.KryoNetworkSerializer.write(transport_network, output_file)

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

    @functools.cached_property
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
        return TransitLayer.from_r5_transit_layer(self._transport_network.transitLayer)


@jpype._jcustomizer.JConversion(
    "com.conveyal.r5.transit.TransportNetwork", exact=TransportNetwork
)
def _cast_TransportNetwork(java_class, object_):
    return object_._transport_network
