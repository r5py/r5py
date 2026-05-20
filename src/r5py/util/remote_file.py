#!/usr/bin/env python3


"""A remote data set that is downloaded on demand."""

import datetime
import hashlib
import pathlib
import warnings

import requests

from .config import Config
from .validating_requests_session import ValidatingRequestsSession

config = Config()

ONE_DAY = datetime.timedelta(days=1)


class RemoteFile(pathlib.Path):
    """Data set that is downloaded and cached as needed."""

    # decide which kind of pathlib.Path we are (Windows, Unix, ...)
    # cf. https://stackoverflow.com/a/66613346/463864
    try:
        _flavour = type(pathlib.Path())._flavour  # pylint: disable=protected-access
    except AttributeError:  # Python>=3.13
        pass

    _CACHE_DIR = pathlib.Path(config.CACHE_DIR) / "remote"

    def __new__(cls, remote_url, sha256_checksum=None):
        """Define a data set that is downloaded and cached on demand."""
        # pathlib.Path does everything in __new__, rather than __init__
        cached_path = cls._CACHE_DIR / pathlib.Path(remote_url).name
        return super().__new__(cls, cached_path)

    def __init__(self, remote_url, sha256_checksum=None, max_cache_age=ONE_DAY):
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
        self.max_cache_age = max_cache_age
        self._download_remote_file()

    def _download_remote_file(self):
        try:
            try:
                checksum = hashlib.sha256(self.cached_path.read_bytes()).hexdigest()
                if self.checksum is not None:
                    assert checksum == self.checksum
            except FileNotFoundError as exception:
                if config.arguments.verbose:
                    warnings.warn(
                        f"First access to {pathlib.Path(self.remote_url).name}, "
                        "downloading remote file to local cache",
                        RuntimeWarning,
                        stacklevel=1,
                    )
                raise exception
            except AssertionError as exception:
                if config.arguments.verbose:
                    warnings.warn(
                        f"{pathlib.Path(self.remote_url).name} changed, "
                        "re-downloading remote file to local cache",
                        RuntimeWarning,
                        stacklevel=1,
                    )
                raise exception
            assert datetime.datetime.fromtimestamp(self.cached_path.stat().st_mtime) > (
                datetime.datetime.now() - self.max_cache_age
            )
        except (AssertionError, FileNotFoundError):
            self.cached_path.parent.mkdir(exist_ok=True)
            if self.checksum is not None:
                with (
                    ValidatingRequestsSession() as session,
                    session.get(self.remote_url, checksum=self.checksum) as response,
                ):
                    self.cached_path.write_bytes(response.content)
            else:
                with (
                    requests.Session() as session,
                    session.get(self.remote_url) as response,
                ):
                    self.cached_path.write_bytes(response.content)
