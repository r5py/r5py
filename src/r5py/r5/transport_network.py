#!/usr/bin/env python3


"""Wraps a com.conveyal.r5.transit.TransportNetwork."""


import json
import pathlib
import warnings

import jpype
import jpype.types

from .. import util  # noqa: F401
from .transport_network_builder_config import TransportNetworkBuilderConfig

import com.conveyal.r5
import java.lang
import java.util.ArrayList


__all__ = ["TransportNetwork"]


class TransportNetwork:
    """Wrap a com.conveyal.r5.transit.TransportNetwork."""

    def __init__(self, osm_pbf, gtfs=[], build_config={}):
        """
        Load a transport network.

        Arguments
        ---------
        osm_pbf : str
            file path of an OpenStreetMap extract in PBF format
        gtfs : list[str]
            paths to public transport schedule information in GTFS format
        build_json : dict
            options accepted by TNBuilderConfig (including SpeedConfig)
        """
        # TODO: Add TNBuilderConfig and SpeedConfig options to docstring
        osm_pbf = str(pathlib.Path(osm_pbf).absolute())
        gtfs = [str(pathlib.Path(path).absolute()) for path in gtfs]
        build_config = TransportNetworkBuilderConfig(**build_config)
        self._transport_network = com.conveyal.r5.transit.TransportNetwork.fromFiles(
            java.lang.String(osm_pbf), java.util.ArrayList.of(gtfs), build_config
        )
        self._transport_network.transitLayer.buildDistanceTables(None)

    @classmethod
    def from_directory(cls, path):
        """
        Find input data in `path`, load an `r5py.TransportNetwork`.

        This mimicks r5r’s behaviour to accept a directory path
        as the only input to `setup_r5()`.

        If more than one OpenStreetMap extract (`.osm.pbf`) is
        found in `path`, the (alphabetically) first is used.
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
            if len(potential_osm_pbf_files > 1):
                warnings.warn(
                    (
                        f"Found more than one OpenStreetMap extract file (`.osm.pbf`), "
                        f"using alphabetically first one ({osm_pbf.name})"
                    ),
                    RuntimeWarning,
                )
        except KeyError:
            raise FileNotFoundError(
                f"Could not find any OpenStreetMap extract file (`.osm.pbf`) in {path.absolute()}"
            )
        gtfs = [
            potential_gtfs_file
            for potential_gtfs_file in path.glob("*.zip")
            if util.contains_gtfs_data(potential_gtfs_file)
        ]
        try:
            with open(pathlib.Path(path) / "build.json") as build_json_file:
                build_json = json.load(build_json_file)
        except (FileNotFoundError, json.JSONDecodeError):
            build_json = {}

        return cls(osm_pbf, gtfs, build_json)

    @property
    def linkage_cache(self):
        """Expose the `TransportNetwork`’s `linkageCache` to Python."""
        return self._transport_network.linkageCache

    @property
    def street_layer(self):
        """Expose the `TransportNetwork`’s `streetLayer` to Python."""
        return self._transport_network.streetLayer

    @property
    def timezone(self):
        """Determine the timezone of the GTFS data."""
        return self._transport_network.getTimeZone()


@jpype._jcustomizer.JConversion(
    "com.conveyal.r5.transit.TransportNetwork", exact=TransportNetwork
)
def _cast_TransportNetwork(java_class, object_):
    return object_._transport_network
