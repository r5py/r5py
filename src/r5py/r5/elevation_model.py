#!/usr/bin/env python3


"""Load a digital elevation model and apply it to an r5py.TransportNetwork."""

import collections.abc
import hashlib
import pathlib

import rasterio
import rasterio.merge

from .elevation_cost_function import ElevationCostFunction
from .file_storage import FileStorage
from ..util import FileDigest, WorkingCopy

import com.conveyal.analysis
import com.conveyal.r5

__all__ = ["ElevationModel"]


class ElevationModel:
    """Load a digital elevation model and apply it to an r5py.TransportNetwork."""

    def __init__(
        self,
        elevation_model,
        elevation_cost_function=ElevationCostFunction.TOBLER,
    ):
        """
        Load an elevation model.

        Arguments
        ---------
        elevation_model : str | pathlib.Path | list[str, pathlib.Path]
            file path(s) to one or more digital elevation model(s) in TIF
            format, single-band, the value of which is the elevation in metres
        elevation_cost_function : r5py.ElevationCostFunction
            which algorithm to use to compute the added effort and travel time
            of slopes
        """
        print(type(elevation_model))
        if isinstance(elevation_model, collections.abc.Iterable):
            print("treating as iterable")
            elevation_model = self._merge_tiffs(
                [WorkingCopy(e) for e in elevation_model]
            )
        else:
            print("treating as scalar")
            elevation_model = self._convert_tiff_to_format_readable_by_r5(
                WorkingCopy(elevation_model)
            )

        # instantiate an com.conveyal.file.FileStorage singleton
        com.conveyal.analysis.components.WorkerComponents.fileStorage = FileStorage()

        self._elevation_model = com.conveyal.r5.analyst.scenario.RasterCost()
        self._elevation_model.dataSourceId = f"{elevation_model.with_suffix('')}"
        self._elevation_model.costFunction = elevation_cost_function

    def apply_to(self, transport_network):
        """
        Add the costs associated with elevation traversal to a transport network.

        Arguments
        ---------
        transport_network : r5py.TransportNetwork
            The transport network to which to add slope costs
        """
        self._elevation_model.resolve(transport_network)
        self._elevation_model.apply(transport_network)

    @staticmethod
    def _convert_tiff_to_format_readable_by_r5(tiff):
        # javax.imagio does not allow all compression/predictor
        # combinations of TIFFs
        # to work around it, convert the input to a format known to work.

        input_tiff = tiff.with_stem(f".{tiff.stem}")
        output_tiff = tiff.with_suffix(".tif")
        tiff.rename(input_tiff)

        with rasterio.open(input_tiff) as source:
            metadata = source.profile
            metadata.update(
                {
                    "compress": "LZW",
                    "predictor": "2",
                }
            )

            # rasterio warns if these are in invalid combinations,
            # let it choose itself
            del metadata["blockxsize"]
            del metadata["blockysize"]
            del metadata["tiled"]

            with rasterio.open(output_tiff, "w", **metadata) as destination:
                destination.write(source.read())
        input_tiff.unlink()

        return output_tiff

    @staticmethod
    def _merge_tiffs(input_tiffs):
        input_tiffs = [pathlib.Path(input_tiff) for input_tiff in input_tiffs]
        # a hash representing all input files
        digest = hashlib.sha256(
            "".join([FileDigest(input_tiff) for input_tiff in input_tiffs]).encode(
                "utf-8"
            )
        ).hexdigest()

        output_tiff = pathlib.Path(input_tiffs[0].parent / f"{digest}.tif")

        output_data, output_transform = rasterio.merge.merge(input_tiffs)

        with rasterio.open(input_tiffs[0]) as source:
            metadata = source.profile
        metadata.update(
            {
                "compress": "LZW",
                "predictor": "2",
                "height": output_data.shape[1],
                "width": output_data.shape[2],
                "transform": output_transform,
            }
        )

        # rasterio warns if these are in invalid combinations,
        # let it choose itself
        del metadata["blockxsize"]
        del metadata["blockysize"]
        del metadata["tiled"]

        with rasterio.open(output_tiff, "w", **metadata) as destination:
            destination.write(output_data)

        return output_tiff
