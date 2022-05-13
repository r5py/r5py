#!/usr/bin/env python3

"""Set up a JVM and import basic java classes."""

import jpype
import jpype.imports

from .classpath import R5_CLASSPATH
from .memory_footprint import MAX_JVM_MEMORY


__all__ = []


jpype.startJVM(
    f"-Xmx{MAX_JVM_MEMORY:d}M",
    "-Xcheck:jni",
    # "--illegal-access=permit",
    # "--add-opens=java.lang/java.nio.DirectByteBuffer=ALL-UNNAMED",
    classpath=[R5_CLASSPATH],
)
