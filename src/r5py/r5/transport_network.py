#!/usr/bin/env python3


"""Wraps a com.conveyal.r5.transit.TransportNetwork."""


import pathlib
import shutil
import warnings

import jpype
import jpype.types

from ..util import Config, contains_gtfs_data, start_jvm

import com.conveyal.r5
import java.lang
import java.util.ArrayList


__all__ = ["TransportNetwork"]


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

        self._transport_network = com.conveyal.r5.transit.TransportNetwork.fromFiles(
            java.lang.String(str(osm_pbf)),
            java.util.ArrayList.of(gtfs),
        )
        self._transport_network.transitLayer.buildDistanceTables(None)

        # attempt to remove temporary files created by R5 during import
        # (potentially frees up RAM)
        for temp_file in osm_pbf.parent.glob(f"{osm_pbf.name}.mapdb*"):
            try:
                temp_file.unlink()
            except (OSError, PermissionError):
                # it does not really matter if we cannot delete temp files now,
                # as they will be deleted, at latest, in __del__()

                # (e.g., on Windows there seem to occur race conditions between
                # here and the Java garbage collector, that prevent us from deleting)
                pass

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

    def __del__(self):
        """Remove cache directory when done."""
        shutil.rmtree(str(self._cache_directory))

    def __enter__(self):
        """Provide a context."""
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        """Exit context."""
        return False

    @property
    def _cache_directory(self):
        try:
            self.__cache_dir
        except AttributeError:
            self.__cache_dir = (
                pathlib.Path(Config().CACHE_DIR)
                / f"{self.__class__.__name__:s}_{hash(self):x}"
            )
            self.__cache_dir.mkdir(exist_ok=True)
        return self.__cache_dir

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
        try:
            destination_file.symlink_to(input_file)
        except OSError:
            shutil.copyfile(str(input_file), str(destination_file))
        return destination_file

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
