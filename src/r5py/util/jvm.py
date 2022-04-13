#!/usr/bin/env python3

"""Set up a JVM and import basic java classes."""

import sys

import jpype
import jpype.imports

from .classpath import R5_CLASSPATH
from .memory_footprint import EIGHTY_PERCENT_OF_RAM


__all__ = []


sys.modules['faulthandler'] = None

jpype.startJVM(
    "-Xmx{:d}G".format(EIGHTY_PERCENT_OF_RAM),
    "-Xcheck:jni",
    # "--illegal-access=permit",
    # "--add-opens=java.lang/java.nio.DirectByteBuffer=ALL-UNNAMED",
    classpath=[R5_CLASSPATH]
)
