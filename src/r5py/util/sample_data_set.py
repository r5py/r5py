#!/usr/bin/env python3


"""A remote sample data set that is downloaded on demand."""

import pathlib

from .config import Config
from .remote_file import RemoteFile

config = Config()


class SampleDataSet(RemoteFile):
    """Data set that is downloaded and cached as needed."""

    _CACHE_DIR = pathlib.Path(config.CACHE_DIR) / "sampledata"
