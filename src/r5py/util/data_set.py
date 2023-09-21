#!/usr/bin/env python3


"""A remote data set that is downloaded on demand."""


import warnings

from .sample_data_set import SampleDataSet


class DataSet(SampleDataSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        warnings.warn(
            "r5py.util.data_set.DataSet is deprecated, use "
            "r5py.util.sample_data_set.SampleDataSet, instead.",
            DeprecationWarning,
        )
