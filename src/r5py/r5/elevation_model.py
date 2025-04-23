#!/usr/bin/env python3


"""Load a digital elevation model and apply it to an r5py.TransportNetwork."""


import rasterio

from .elevation_cost_function import ElevationCostFunction
from .file_storage import FileStorage
from ..util import WorkingCopy

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
        elevation_model : str | pathlib.Path
            file path to a digital elevation model in TIF format,
            single-band, the value of which is the elevation in metres
        elevation_cost_function : r5py.ElevationCostFunction
            which algorithm to use to compute the added effort and travel time
            of slopes
        """
        elevation_model = WorkingCopy(elevation_model)
        elevation_model = self._convert_tiff_to_format_readable_by_r5(elevation_model)

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
            with rasterio.open(output_tiff, "w", **metadata) as destination:
                destination.write(source.read())
        input_tiff.unlink()

        return output_tiff
