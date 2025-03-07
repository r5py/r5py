#!/usr/bin/env python3


"""Assign a cluster label column to a point-geometry GeoDataFrame."""


import warnings

import geopandas
import numpy
import shapely
import sklearn.cluster

from .good_enough_equidistant_crs import GoodEnoughEquidistantCrs


__all__ = ["SpatiallyClusteredGeoDataFrame"]


class SpatiallyClusteredGeoDataFrame(geopandas.GeoDataFrame):
    """Assign a cluster label column to a point-geometry GeoDataFrame."""

    def __init__(self, data, *args, eps=200.0, min_cluster_size=3, **kwargs):
        """
        Assign a cluster label column to a point-geometry GeoDataFrame.

        Arguments:
        ----------
        data : geopandas.GeoDataFrame
            input data set
        eps : int | float
            EPS parameter to a DBSCAN cluster algorithm, the maximum
            intra-cluster distance between two points
        *args, **kwargs: passed to geopandas.GeoDataFrame.__init__()
        """
        geopandas.GeoDataFrame.__init__(self, *args, **kwargs)

        EQUIDISTANT_CRS = GoodEnoughEquidistantCrs(
            shapely.box(*data.to_crs("EPSG:4326").geometry.total_bounds)
        )

        # loosely based on:
        # https://github.com/geopandas/scipy2018-geospatial-data/blob/master/08-clustering.ipynb

        coordinates = numpy.vstack(
            data.to_crs(EQUIDISTANT_CRS)["geometry"]
            .apply(lambda geometry: numpy.hstack(geometry.xy))
            .values
        )

        with warnings.catch_warnings():
            warnings.filterwarnings(
                "ignore",
                "Could not find the number of physical cores",
                category=UserWarning,
            )
            data["cluster"] = (
                sklearn.cluster.DBSCAN(
                    eps=eps,
                    min_samples=min_cluster_size,
                    n_jobs=-1,
                )
                .fit(coordinates)
                .labels_
            )

        with warnings.catch_warnings():
            warnings.filterwarnings(
                "ignore",
                message=(
                    "You are adding a column named 'geometry' to a GeoDataFrame "
                    "constructed without an active geometry column"
                ),
                category=FutureWarning,
            )
            for column in data.columns:
                self[column] = data[column]
            self.set_geometry("geometry")
