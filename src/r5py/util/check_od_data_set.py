#!/usr/bin/env python3

"""Check whether an origin/destination data set fulfils certain minimum criteria."""


from .exceptions import NoIDColumnError, NonUniqueIDError


__all__ = ["check_od_data_set"]


def check_od_data_set(od_data_set):
    """Check whether an origin/destination data set fulfils certain minimum criteria.

    Checks whether `od_data_set` has an `id` column with unique values. Raises a
    `r5py.util.exceptions.NoIDColumnError` or a `r5py.util.exceptions.NonUniqueIDError`
    otherwise.

    Arguments
    ---------
        od_data_set : geopandas.GeoDataFrame
            The origin/destination data set to check.
    """
    if "id" not in od_data_set.columns:
        raise NoIDColumnError("Origin dataset must contain an 'id' column.")
    if not od_data_set.id.is_unique:
        raise NonUniqueIDError("Origin id values must be unique.")
