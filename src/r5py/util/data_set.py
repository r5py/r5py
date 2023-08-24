#!/usr/bin/env python3


"""Download sample data on demand and supply a `pathlib.Path` object pointing to them."""


import hashlib
import pathlib
import warnings

from r5py.util.config import Config
from r5py.util.validating_requests_session import ValidatingRequestsSession


config = Config()


class DataSet(pathlib.Path):
    """Data set that is downloaded and cached as needed."""

    # decide which kind of pathlib.Path we are (Windows, Unix, ...)
    # cf. https://stackoverflow.com/a/66613346/463864
    _flavour = type(pathlib.Path())._flavour

    def __new__(cls, remote_url, sha256_checksum):
        # pathlib.Path does everything in __new__, rather than __init__
        cached_path = pathlib.Path(config.CACHE_DIR) / pathlib.Path(remote_url).name
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
        super().__init__()
        self.remote_url = remote_url
        self.checksum = sha256_checksum
        self.cached_path = (
            pathlib.Path(config.CACHE_DIR) / pathlib.Path(remote_url).name
        )
        self._downloaded = False

    def _download_remote_file(self):
        if not self._downloaded:
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
                with ValidatingRequestsSession() as session, session.get(
                    self.remote_url, self.checksum
                ) as response:
                    self.cached_path.write_bytes(response.content)

    def __str__(self):
        self._download_remote_file()
        return super().__str__()

    def __fspath__(self):
        self._download_remote_file()
        return super().__fspath__()
