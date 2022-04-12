#!/usr/bin/env python3

"""Set up a JVM and import basic java classes."""

import sys

import jpype
import jpype.imports

from . import config
from .memory_footprint import EIGHTY_PERCENT_OF_RAM


__all__ = []


# TODO: Check how to package the jar as a fallback, or maybe download it
# in case it’s not available on the local system


config.argparser.add(
    "-r",
    "--r5-classpath",
    help="R5’s class path, can point to r5-all.jar",
    default="/usr/share/java/r5/r5-all.jar"
)
arguments = config.arguments()

sys.modules['faulthandler'] = None

jpype.startJVM(
    "-Xmx{:d}G".format(EIGHTY_PERCENT_OF_RAM),
    "-Xcheck:jni",
    # "--illegal-access=permit",
    # "--add-opens=java.lang/java.nio.DirectByteBuffer=ALL-UNNAMED",
    classpath=[arguments.r5_classpath]
)
