#!/usr/bin/env python3


"""A remote data set that is downloaded on demand."""


import hashlib
import pathlib
import warnings

from .config import Config
from .validating_requests_session import ValidatingRequestsSession


config = Config()


class SampleDataSet(pathlib.Path):
    """Data set that is downloaded and cached as needed."""

    # decide which kind of pathlib.Path we are (Windows, Unix, ...)
    # cf. https://stackoverflow.com/a/66613346/463864
    _flavour = type(pathlib.Path())._flavour

    _CACHE_DIR = pathlib.Path(config.CACHE_DIR) / "sampledata"

    def __new__(cls, remote_url, sha256_checksum):
        """Define a data set that is downloaded and cached on demand."""
        # pathlib.Path does everything in __new__, rather than __init__
        cached_path = cls._CACHE_DIR / pathlib.Path(remote_url).name
        return super().__new__(cls, cached_path)

    def __init__(self, remote_url, sha256_checksum, *args, **kwargs):
        """
        Define a data set that is downloaded and cached on demand.

        Arguments
        ---------
        remote_url : str
            source URL for this data set
        sha256_checksum : str
            checksum for this data set, using an SHA256 algorithm
        """
        cached_path = self._CACHE_DIR / pathlib.Path(remote_url).name

        try:  # Python>=3.12
            super().__init__(cached_path)
        except TypeError:
            super().__init__()

        self.remote_url = remote_url
        self.checksum = sha256_checksum
        self.cached_path = cached_path
        self._download_remote_file()

    def _download_remote_file(self):
        try:
            assert (
                hashlib.sha256(self.cached_path.read_bytes()).hexdigest()
                == self.checksum
            )
        except (AssertionError, FileNotFoundError):
            if config.arguments.verbose:
                warnings.warn(
                    f"First access to {pathlib.Path(self.remote_url).name}, "
                    "downloading remote file to local cache",
                    RuntimeWarning,
                )
            self.cached_path.parent.mkdir(exist_ok=True)
            with (
                ValidatingRequestsSession() as session,
                session.get(self.remote_url, self.checksum) as response,
            ):
                self.cached_path.write_bytes(response.content)
