#!/usr/bin/env python3

"""Utility functions for validating input data."""


from .exceptions import NoIDColumnError, NonUniqueIDError, NoCrsError


__all__ = ["check_od_data_set"]


def check_od_data_set(od_data_set):
    """Check whether an origin/destination data set fulfils certain minimum criteria.

    Checks whether `od_data_set` has an `id` column with unique values, and a coordinate
    reference system defined. Raises a `r5py.util.exceptions.NoIDColumnError`, a
    `r5py.util.exceptions.NonUniqueIDError`, or a `r5py.util.exceptions.NoCrsError`
    otherwise.

    Arguments
    ---------
        od_data_set : geopandas.GeoDataFrame
            The origin/destination data set to check.
    """
    if "id" not in od_data_set.columns:
        raise NoIDColumnError("Data set must contain an 'id' column.")
    if not od_data_set.id.is_unique:
        raise NonUniqueIDError("Id values must be unique.")
    if od_data_set.crs is None:
        raise NoCrsError("Data set has to have a coordinate reference system defined.")
