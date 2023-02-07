#!/usr/bin/env python3

"""Make sure R5 is in the class path, download it if not."""

import hashlib
import pathlib
import warnings

from .config import Config
from .validating_requests_session import ValidatingRequestsSession


# update these to use a newer R5 version if no R5 available locally
R5_JAR_URL = "https://github.com/conveyal/r5/releases/download/v6.9/r5-v6.9-all.jar"
R5_JAR_SHA256 = "a7e1c5ff8786a9fb9191073b8f31a6933b862f44b9ff85b2c00a68c85491274d"
# ---


__all__ = ["R5_CLASSPATH"]


config = Config()

config.argparser.add(
    "-r",
    "--r5-classpath",
    help="R5’s class path, can point to r5-all.jar",
    default="/usr/share/java/r5/r5-all.jar",
)


def find_r5_classpath(arguments):
    if pathlib.Path(arguments.r5_classpath).exists():
        # do not test local files’ checksums, as they might be customly compiled
        r5_classpath = arguments.r5_classpath
    else:
        r5_classpath = str(config.CACHE_DIR / pathlib.Path(R5_JAR_URL).name)
        try:
            with open(r5_classpath, "rb") as jar:
                assert hashlib.sha256(jar.read()).hexdigest() == R5_JAR_SHA256
        except (AssertionError, FileNotFoundError):
            if arguments.verbose:
                warnings.warn(
                    "Could not find R5 jar, trying to download it from upstream",
                    RuntimeWarning,
                )
            with ValidatingRequestsSession() as session, session.get(
                R5_JAR_URL, R5_JAR_SHA256
            ) as response, open(r5_classpath, "wb") as jar:
                jar.write(response.content)
            if arguments.verbose:
                warnings.warn(
                    f"Successfully downloaded {pathlib.Path(R5_JAR_URL).name}",
                    RuntimeWarning,
                )
    return r5_classpath


R5_CLASSPATH = find_r5_classpath(config.arguments)
